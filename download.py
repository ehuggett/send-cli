import requests
import json

from urllib.parse import unquote_plus
from Cryptodome.Cipher import AES
from base64 import urlsafe_b64decode

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

def get(url):
   '''Given a Send url, download and return the encrypted data and metadata'''
   prefix, urlid, key = splitkeyurl(url)

   r = requests.get(prefix + 'assets/download/' + urlid)
   data = r.content

   meta = json.loads(r.headers['X-File-Metadata'])
   filename = unquote_plus(meta['filename'])
   iv = meta['id']

   return data, filename, key, iv


def decrypt(data,key,iv):
   '''Decrypts a file from Send'''
   key = key_decode(key)
   iv = bytes.fromhex(iv)

   # The last 16 bytes / 128 bits of data is the GCM tag
   # https://www.w3.org/TR/WebCryptoAPI/#aes-gcm-operations :-
   # 7. Let ciphertext be equal to C | T, where '|' denotes concatenation.
   tag = data[-16:]
   data = data[:-16]

   obj = AES.new(key, AES.MODE_GCM, iv)
   data = obj.decrypt_and_verify(data,tag)

   return(data)
