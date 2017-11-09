import json
import os
import requests
import tempfile

import Cryptodome.Cipher.AES
import Cryptodome.Hash.HMAC
import Cryptodome.Hash.SHA256
import requests_toolbelt

from sendclient.common import unpadded_urlsafe_b64encode, unpadded_urlsafe_b64decode, secretKeys, SPOOL_SIZE, CHUNK_SIZE, checkServerVersion, progbar, fileSize


def encrypt_file(file, keys=secretKeys()):
    '''Encrypt file data with the same method as the Send browser/js client'''
    key = keys.encryptKey
    iv = keys.encryptIV
    encData = tempfile.SpooledTemporaryFile(max_size=SPOOL_SIZE, mode='w+b')
    cipher = Cryptodome.Cipher.AES.new(key, Cryptodome.Cipher.AES.MODE_GCM, iv)

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
    metadata = json.dumps({'iv' : unpadded_urlsafe_b64encode(keys.encryptIV), 'name' : fileName, 'type' : fileType}, sort_keys=True)

    cipher = Cryptodome.Cipher.AES.new(keys.metaKey, Cryptodome.Cipher.AES.MODE_GCM, keys.metaIV)
    encMeta, gcmTag = cipher.encrypt_and_digest(metadata.encode())

    # WebcryptoAPI expects the gcm tag at the end of the ciphertext, return them concatenated
    return encMeta + gcmTag

def api_upload(service, encData, encMeta, keys):
    '''
       Uploads data to Send.
       Caution! Data is uploaded as given, this function will not encrypt it for you
    '''
    service += 'api/upload'
    files = requests_toolbelt.MultipartEncoder(fields={'file': ('blob', encData, 'application/octet-stream') })
    pbar = progbar(files.len)
    monitor = requests_toolbelt.MultipartEncoderMonitor(files, lambda files: pbar.update(monitor.bytes_read - pbar.n))

    headers = {
        'X-File-Metadata' : unpadded_urlsafe_b64encode(encMeta),
        'Authorization' : 'send-v1 ' + unpadded_urlsafe_b64encode(keys.authKey),
        'Content-type' : monitor.content_type
    }

    r = requests.post(service, data=monitor, headers=headers, stream=True)
    r.raise_for_status()
    pbar.close()

    body_json = r.json()
    secretUrl = body_json['url'] + '#' + unpadded_urlsafe_b64encode(keys.secretKey)
    fileId = body_json['id']
    fileNonce = unpadded_urlsafe_b64decode(r.headers['WWW-Authenticate'].replace('send-v1 ', ''))
    delete_token = body_json['delete']
    return secretUrl, fileId, fileNonce, delete_token

def sign_nonce(key, nonce):
    ''' sign the server nonce from the WWW-Authenticate header with an authKey'''
    # HMAC.new(key, msg='', digestmod=None)
    return Cryptodome.Hash.HMAC.new(key, nonce, digestmod=Cryptodome.Hash.SHA256).digest()

def set_password(service, keys, url, fileId, password, nonce):
    ''' sets the download password by sending a HMAC key derived from it to the Send server'''
    service += 'api/password/' + str(fileId)

    sig = sign_nonce(keys.authKey, nonce)
    newAuthKey = keys.deriveNewAuthKey(password, url)

    headers = {'Authorization' : 'send-v1 ' + unpadded_urlsafe_b64encode(sig) }
    r = requests.post(service, json={'auth' :unpadded_urlsafe_b64encode(newAuthKey) }, headers=headers)
    r.raise_for_status()

def send_file(service, file, fileName=None, password=None, ignoreVersion=False):

    if checkServerVersion(service, ignoreVersion=ignoreVersion) == False:
        print('\033[1;41m!!! Potentially incompatible server version !!!\033[0m')

    ''' Encrypt & Upload a file to send and return the download URL'''
    fileName = fileName if fileName != None else os.path.basename(file.name)

    print('Encrypting data from "' + fileName + '"')
    keys = secretKeys()
    encData = encrypt_file(file, keys)
    encMeta = encrypt_metadata(keys, fileName)

    print('Uploading "' + fileName + '"')
    secretUrl, fileId, fileNonce, delete_token = api_upload(service, encData, encMeta, keys)

    if password != None:
        print('Setting password')
        set_password(service, keys, secretUrl, fileId, password, fileNonce)

    return secretUrl, delete_token
