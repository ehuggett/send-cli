import json
import requests
import os

from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import Cryptodome.Hash.HMAC
import Cryptodome.Hash.SHA256
from base64 import urlsafe_b64encode, urlsafe_b64decode
from tempfile import SpooledTemporaryFile
from urllib.parse import quote_plus
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from sendclient.common import *

def encrypt_file(file, keys=secretKeys()):
    '''Encrypt file data with the same method as the Send browser/js client'''
    key = keys.encryptKey
    iv = keys.encryptIV
    encData = SpooledTemporaryFile(max_size=SPOOL_SIZE, mode='w+b')
    cipher = AES.new(key, AES.MODE_GCM, iv)

    pbar = progbar(fileSize(file))

    for chunk in iter(lambda: file.read(CHUNK_SIZE), b''):
        encData.write(cipher.encrypt(chunk))
        pbar.update(len(chunk))

    pbar.close()
    encData.write(cipher.digest())
    file.close()

    encData.seek(0)
    return encData

def encrypt_metadata(keys, fileName, fileType='application/octet-stream'):
    '''Encrypt file metadata with the same method as the Send browser/js client'''
    metadata = json.dumps({'iv' : unpadded_urlsafe_b64encode(keys.encryptIV), 'name' : fileName, 'type' : fileType}).encode('utf8')

    cipher = AES.new(keys.metaKey, AES.MODE_GCM, keys.metaIV)
    encMeta, gcmTag = cipher.encrypt_and_digest(metadata)

    # WebcryptoAPI expects the gcm tag at the end of the ciphertext, return them concatenated
    return encMeta + gcmTag

def put(service, encData, encMeta, keys):
    '''
       Uploads data to Send.
       Caution! Data is uploaded as given, this function will not encrypt it for you
    '''

    if checkServerVersion(service.replace('api/upload', '')) == False:
        print('\033[1;41m!!! Potentially incompatible server version !!!\033[0m')

    files = MultipartEncoder(fields={'file': ('blob', encData, 'application/octet-stream') })
    pbar = progbar(files.len)
    monitor = MultipartEncoderMonitor(files, lambda files: pbar.update(monitor.bytes_read - pbar.n))

    headers = {
        'X-File-Metadata' : unpadded_urlsafe_b64encode(encMeta),
        'Authorization' : 'send-v1 ' + unpadded_urlsafe_b64encode(keys.authKey),
        'Content-type' : monitor.content_type
    }

    r = requests.post(service, data=monitor, headers=headers, stream=True)
    r.raise_for_status()
    pbar.close()

    bodyJson = r.json()
    secretUrl = bodyJson['url'] + '#' + unpadded_urlsafe_b64encode(keys.secretKey)
    fileId = bodyJson['id']
    fileNonce = urlsafe_b64decode(r.headers['WWW-Authenticate'].replace('send-v1 ','') + '==')
    return secretUrl, fileId, fileNonce

def sign_nonce(key, nonce):
    #HMAC.new(key, msg='', digestmod=None)
    return Cryptodome.Hash.HMAC.new(key, nonce, digestmod=Cryptodome.Hash.SHA256).digest()

def set_password(service, keys, url, fileId, password, nonce):
    # TODO fix url handling
    service = service.replace('api/upload','api/password/' + str(fileId) )

    sig = sign_nonce(keys.authKey, nonce)
    newAuthKey = keys.deriveNewAuthKey(password, url)

    headers = {'Authorization' : 'send-v1 ' + unpadded_urlsafe_b64encode(sig) }
    r = requests.post(service, json={'auth' :unpadded_urlsafe_b64encode(newAuthKey) }, headers=headers )
    r.raise_for_status()

def send_file(service, file, fileName=None, password=None, silent=False):
    ''' Encrypt & Upload a file to send and return the download URL'''
    fileName = fileName if fileName != None else os.path.basename(file.name)

    print('Encrypting data from "' + file.name + '"')
    keys = secretKeys()
    encData= encrypt_file(file, keys)
    encMeta = encrypt_metadata(keys, fileName)

    print('Uploading "' + fileName + '"')
    secretUrl, fileId, fileNonce = put(service, encData, encMeta, keys)

    if password != None:
        print('Setting password')
        set_password(service, keys, secretUrl, fileId, password, fileNonce)

    return secretUrl
