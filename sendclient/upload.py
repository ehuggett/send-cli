import json
import requests

from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from base64 import urlsafe_b64encode
from tempfile import SpooledTemporaryFile
from urllib.parse import quote_plus
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from sendclient.common import *

def jwk_encode(key):
    '''base64 encode with url safe alphabet and strip padding'''
    jwk = urlsafe_b64encode(key)
    jwk = jwk.decode('utf-8').replace('=', '')
    return jwk

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
    return encData, keys

def encrypt_metadata(keys, fileName, fileType='application/octet-stream'):
    '''Encrypt file metadata with the same method as the Send browser/js client'''
    metadata = json.dumps({'iv' : jwk_encode(keys.encryptIV), 'name' : fileName, 'type' : fileType}).encode('utf8')

    cipher = AES.new(keys.metaKey, AES.MODE_GCM, keys.metaIV)
    encMeta, gcmTag = cipher.encrypt_and_digest(metadata)

    # WebcryptoAPI expects the gcm tag at the end of the ciphertext, return them concatenated
    return encMeta + gcmTag

def put(service, data, filename, iv):
    '''
       Uploads data to Send.
       Caution! Data is uploaded as given, this function will not encrypt it for you
    '''

    if checkServerVersion(service.replace('api/upload', '')) == False:
        print('\033[1;41m!!! Potentially incompatible server version !!!\033[0m')

    filename = quote_plus(filename)
    # nb the Content-Type is also "public" metadata
    files = MultipartEncoder(fields={'file': (filename, data, 'application/octet-stream') })
    pbar = progbar(files.len)
    monitor = MultipartEncoderMonitor(files, lambda files: pbar.update(monitor.bytes_read - pbar.n))

    public_meta = {'filename' : filename, 'id': iv }
    headers = {'X-File-Metadata' : json.dumps(public_meta), 'Content-type' : monitor.content_type}

    r = requests.post(service, data=monitor, headers=headers, stream=True)
    r.raise_for_status()
    pbar.close()
    return r.json()
