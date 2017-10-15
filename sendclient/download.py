import requests
import json

from urllib.parse import unquote_plus
from Cryptodome.Cipher import AES
from base64 import urlsafe_b64decode
from tempfile import SpooledTemporaryFile, NamedTemporaryFile

from sendclient.common import *

def splitkeyurl(url):
   '''
      Splits a Send url into key, urlid and 'prefix' for the Send server
      Should handle any hostname, but will brake on key & id length changes
   '''
   key = url[-22:]
   urlid = url[-34:-24]
   prefix = url[:-43]
   return prefix,urlid,key

def key_decode(jwk):
   """given the key from the Send URL returns the raw aes key"""
   # missing padding will error but superfluous padding is ignored ¯\_(ツ)_/¯
   jwk += '==='
   raw = urlsafe_b64decode(jwk.encode('utf-8'))
   return raw

def get(url, ignoreVersion=False):
   '''Given a Send url, download and return the encrypted data and metadata'''
   prefix, urlid, key = splitkeyurl(url)

   if checkServerVersion(prefix, ignoreVersion) == False:
      raise Exception('Potentially incompatible server version, use --ignore-version to disable version checks')

   data = SpooledTemporaryFile(max_size=SPOOL_SIZE, mode='w+b')

   r = requests.get(prefix + 'api/download/' + urlid, stream=True)
   r.raise_for_status()
   content_length = int(r.headers['Content-length'])
   meta = json.loads(r.headers['X-File-Metadata'])
   filename = unquote_plus(meta['filename'])
   iv = meta['id']

   pbar = progbar(content_length)
   for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
      data.write(chunk)
      pbar.update(len(chunk))
   pbar.close()

   # The last 16 bytes / 128 bits of data is the GCM tag
   # https://www.w3.org/TR/WebCryptoAPI/#aes-gcm-operations :-
   # 7. Let ciphertext be equal to C | T, where '|' denotes concatenation.
   data.seek(-16,2)
   tag = data.read()

   # now truncate the file to only contain encrypted data
   data.seek(-16,2)
   data.truncate()

   data.seek(0)
   return data, filename, key, iv, tag

def decrypt(data,key,iv,tag):
   '''Decrypts a file from Send'''
   key = key_decode(key)
   iv = bytes.fromhex(iv)
   plain = NamedTemporaryFile(mode='w+b', delete=False)

   pbar = progbar(fileSize(data))

   obj = AES.new(key, AES.MODE_GCM, iv)
   prev_chunk = b''
   for chunk in iter(lambda: data.read(CHUNK_SIZE), b''):
      plain.write(obj.decrypt(prev_chunk))
      pbar.update(len(chunk))
      prev_chunk = chunk

   plain.write(obj.decrypt_and_verify(prev_chunk,tag))
   data.close()
   pbar.close()

   plain.seek(0)
   return(plain)
