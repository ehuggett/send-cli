# Constants
CHUNK_SIZE = 8192
SPOOL_SIZE = 16 * 1024 * 1024

from tqdm import tqdm
import requests
import base64

def checkServerVersion(service, ignoreVersion=False):
    if ignoreVersion == True:
        return True

    r = requests.get(service + '__version__')
    r.raise_for_status()
    b = r.json()
    if b['version'] == 'v2.0.0' and b['commit'] == 'cfdef23':
        return True
    else:
        return False

def fileSize(f):
    '''returns the size of a file like object in bytes/octets'''
    offset = f.tell()

    f.seek(0, 2)
    size = f.tell()

    f.seek(offset)  # return to the previous position in the file
    return size

def progbar(total):
    return tqdm(unit='B', unit_scale=True, total=total)

def unpadded_urlsafe_b64encode(b):
    ''' base64 encode bytes with url-safe alphabet and strip padding '''
    return base64.urlsafe_b64encode(b).decode().replace('=','')

def unpadded_urlsafe_b64decode(s):
    ''' Decode url-safe base64 string, with or without padding, to bytes'''
    return base64.urlsafe_b64decode(s + '=' * (4 - len(s) % 4))

import Cryptodome.Hash
import Cryptodome.Protocol.KDF
import Cryptodome.Random

class secretKeys:
    def __init__(self, secretKey=None, password=None, url=None):
        self.secretKey = secretKey if secretKey is not None else self.randomSecretKey()
        self.encryptKey = self.deriveEncryptKey()
        self.encryptIV = self.randomEncryptIV()
        self.authKey = self.deriveAuthKey()
        self.metaKey = self.deriveMetaKey()
        self.metaIV = bytes(12) # Send uses a 12 byte all-zero IV when encrypting metadata
        if password != None and url != None:
            self.deriveNewAuthKey(password, url)

    def randomSecretKey(self):
        return Cryptodome.Random.get_random_bytes(16)

    def randomEncryptIV(self):
        return Cryptodome.Random.get_random_bytes(12)

    def deriveEncryptKey(self):
        master = self.secretKey
        key_len = 16
        salt = b''
        hashmod = Cryptodome.Hash.SHA256
        num_keys = 1
        context = b'encryption'
        return Cryptodome.Protocol.KDF.HKDF(master, key_len, salt, hashmod, num_keys=num_keys, context=context)

    def deriveAuthKey(self):
        master = self.secretKey
        key_len = 64
        salt = b''
        hashmod = Cryptodome.Hash.SHA256
        num_keys = 1
        context = b'authentication'
        return Cryptodome.Protocol.KDF.HKDF(master, key_len, salt, hashmod, num_keys=num_keys, context=context)

    def deriveMetaKey(self):
        master = self.secretKey
        key_len = 16
        salt = b''
        hashmod = Cryptodome.Hash.SHA256
        num_keys = 1
        context = b'metadata'
        return Cryptodome.Protocol.KDF.HKDF(master, key_len, salt, hashmod, num_keys=num_keys, context=context)

    def deriveNewAuthKey(self, password, url):
        self.password = password
        self.url = url
        hmac_sha256 = lambda key, msg: Cryptodome.Hash.HMAC.new(key, msg, Cryptodome.Hash.SHA256).digest()
        self.newAuthKey = Cryptodome.Protocol.KDF.PBKDF2(password.encode('utf8'), url.encode('utf8'), dkLen=64, count=100, prf=hmac_sha256)
        return self.newAuthKey
