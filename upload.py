import json
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from base64 import urlsafe_b64encode

import requests
from urllib.parse import quote_plus


def jwk_encode(key):
   '''base64 encode with url safe alphabet and strip padding'''
   jwk = urlsafe_b64encode(key)
   jwk = jwk.decode('utf-8').replace('=','')
   return jwk

def encrypt(fh):
   '''Encrypt data with the same method as the Send browser/js client'''
   key = get_random_bytes(16)
   iv = get_random_bytes(12)

   cipher = AES.new(key, AES.MODE_GCM, iv)
   ciphertext, tag = cipher.encrypt_and_digest(fh.read())

   ciphertext += tag
   key = jwk_encode(key)
   iv = iv.hex()

   return ciphertext,key,iv


def put(service,data,filename,iv):
   ''' 
      Uploads data to Send.
      Caution! Data is uploaded as given, this function will not encrypt it for you
   '''
   filename = quote_plus(filename)
   #nb the Content-Type is also "public" metadata
   files = { 'file': (filename, data, 'application/octet-stream') }
   public_meta = {'filename' : filename, 'id': iv }
   headers = {'X-File-Metadata' : json.dumps(public_meta)}

   r = requests.post(service, files=files, headers=headers)
   return json.loads(r.content.decode("utf-8"))
