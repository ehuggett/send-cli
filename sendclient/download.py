import getpass
import json
import requests
import tempfile

import Cryptodome.Cipher.AES
import Cryptodome.Hash.HMAC
import Cryptodome.Hash.SHA256
import bs4

from sendclient.common import unpadded_urlsafe_b64decode, unpadded_urlsafe_b64encode, SPOOL_SIZE, CHUNK_SIZE, progbar, secretKeys, fileSize, checkServerVersion


def splitkeyurl(url):
    '''
       Splits a Send url into key, urlid and 'prefix' for the Send server
       Should handle any hostname, but will brake on key & id length changes
    '''
    key = url[-22:]
    urlid = url[-34:-24]
    service = url[:-43]
    return service, urlid, key

def api_download(service, fileId, authorisation):
    '''Given a Send url, download and return the encrypted data and metadata'''
    data = tempfile.SpooledTemporaryFile(max_size=SPOOL_SIZE, mode='w+b')

    headers = {'Authorization' : 'send-v1 ' + unpadded_urlsafe_b64encode(authorisation)}
    url = service + 'api/download/' + fileId

    r = requests.get(url, headers=headers, stream=True)
    r.raise_for_status()
    content_length = int(r.headers['Content-length'])

    pbar = progbar(content_length)
    for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
        data.write(chunk)
        pbar.update(len(chunk))
    pbar.close()

    data.seek(0)
    return data

def decrypt_filedata(data, keys):
    '''Decrypts a file from Send'''
    # The last 16 bytes / 128 bits of data is the GCM tag
    # https://www.w3.org/TR/WebCryptoAPI/#aes-gcm-operations :-
    # 7. Let ciphertext be equal to C | T, where '|' denotes concatenation.
    data.seek(-16, 2)
    tag = data.read()

    # now truncate the file to only contain encrypted data
    data.seek(-16, 2)
    data.truncate()
    data.seek(0)

    plain = tempfile.NamedTemporaryFile(mode='w+b', delete=False)

    pbar = progbar(fileSize(data))

    obj = Cryptodome.Cipher.AES.new(keys.encryptKey, Cryptodome.Cipher.AES.MODE_GCM, keys.encryptIV)
    prev_chunk = b''
    for chunk in iter(lambda: data.read(CHUNK_SIZE), b''):
        plain.write(obj.decrypt(prev_chunk))
        pbar.update(len(chunk))
        prev_chunk = chunk

    plain.write(obj.decrypt_and_verify(prev_chunk, tag))
    data.close()
    pbar.close()

    plain.seek(0)
    return plain

def decrypt_metadata(encMeta, keys):
    cipher = Cryptodome.Cipher.AES.new(keys.metaKey, Cryptodome.Cipher.AES.MODE_GCM, keys.metaIV)
    tag = encMeta[-16:]
    encMeta = encMeta[:-16]
    metadata = json.loads(cipher.decrypt_and_verify(encMeta, tag).decode())
    return metadata

def check_for_password(url):
    # Its very unlikely that requests would pass the secretKey to the server, but lets ensure its not present
    url = url.rsplit('#')[0]
    response = requests.get(url)
    response.raise_for_status()

    parse = bs4.BeautifulSoup(response.text, 'html.parser').find(id='dl-file')['data-requires-password']

    if parse == '0':
        passwordRequired = False
    elif parse == '1':
        passwordRequired = True
    else:
        print(parse)
        Exception('Failed to read password requirement from html')

    return passwordRequired

def get_nonce(url):
    r = requests.get(url)
    r.raise_for_status()
    nonce = unpadded_urlsafe_b64decode(r.headers['WWW-Authenticate'].replace('send-v1 ', ''))
    return nonce

def sign_nonce(key, nonce):
    ''' sign the server nonce from the WWW-Authenticate header with an authKey'''
    # HMAC.new(key, msg='', digestmod=None)
    return Cryptodome.Hash.HMAC.new(key, nonce, digestmod=Cryptodome.Hash.SHA256).digest()

def api_metadata(service, fileId, authorisation):
    headers = {'Authorization' : 'send-v1 ' + unpadded_urlsafe_b64encode(authorisation)}
    url = service + 'api/metadata/' + fileId
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    newNonce = unpadded_urlsafe_b64decode(response.headers['WWW-Authenticate'].replace('send-v1 ', ''))
    return response.json(), newNonce

def send_urlToFile(url, password=None, ignoreVersion=False):
    service, fileId, key = splitkeyurl(url)

    if checkServerVersion(service, ignoreVersion) == False:
        raise Exception('Potentially incompatible server version, use --ignore-version to disable version checks')

    passwordRequired = check_for_password(service + 'download/' + str(fileId) + '/')

    rawKey = unpadded_urlsafe_b64decode(key)
    if passwordRequired == False and password == None:
        keys = secretKeys(rawKey)
    elif passwordRequired == True and password != None:
        keys = secretKeys(rawKey, password=password, url=url)
        keys.authKey = keys.newAuthKey
    elif passwordRequired and password == None:
        print("A password is required, please enter it now")
        password = getpass.getpass()
        keys = secretKeys(rawKey, password=password, url=url)
        keys.authKey = keys.newAuthKey
    elif passwordRequired == False and password != None:
        raise Exception('A password was provided but none is required')

    print('Checking if file exists...')
    passwordRequired = check_for_password(service + 'download/' + fileId)

    if password == None and passwordRequired == True:
        raise Exception('This Send url requires a password')

    nonce = get_nonce(service + 'download/' + str(fileId) + '/')
    authorisation = sign_nonce(keys.authKey, nonce)
    print('Fetching metadata...')
    jsonMeta, nonce = api_metadata(service, fileId, authorisation)

    encMeta = unpadded_urlsafe_b64decode(jsonMeta['metadata'])
    metadata = decrypt_metadata(encMeta, keys)
    keys.encryptIV = unpadded_urlsafe_b64decode(metadata['iv'])
    print('The file wishes to be called \'' + metadata['name'] + '\' and is ' + str(jsonMeta['size'] - 16) + ' bytes in size')

    print('Downloading ' + url)
    authorisation = sign_nonce(keys.authKey, nonce)
    data = api_download(service, fileId, authorisation)

    print('Decrypting to temp file')
    tmpfile = decrypt_filedata(data, keys)

    return tmpfile, metadata['name']
