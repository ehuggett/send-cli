import json
import requests

from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from base64 import urlsafe_b64encode
from tempfile import SpooledTemporaryFile
from urllib.parse import quote_plus
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from common import *

def jwk_encode(key):
   '''base64 encode with url safe alphabet and strip padding'''
   jwk = urlsafe_b64encode(key)
   jwk = jwk.decode('utf-8').replace('=','')
   return jwk

def encrypt(fh):
   '''Encrypt data with the same method as the Send browser/js client'''
   key = get_random_bytes(16)
   iv = get_random_bytes(12)
   ciphertext = SpooledTemporaryFile(max_size=SPOOL_SIZE, mode='w+b')
   cipher = AES.new(key, AES.MODE_GCM, iv)

   pbar = progbar(fileSize(fh))

   for chunk in iter(lambda: fh.read(CHUNK_SIZE), b'' ):
      ciphertext.write(cipher.encrypt(chunk))
      pbar.update(len(chunk))

   pbar.close()
   ciphertext.write( cipher.digest() )
   fh.close()

   key = jwk_encode(key)
   iv = iv.hex()
   ciphertext.seek(0)

   return ciphertext,key,iv


def put(service,data,filename,iv):
   ''' 
      Uploads data to Send.
      Caution! Data is uploaded as given, this function will not encrypt it for you
   '''
   filename = quote_plus(filename)
   #nb the Content-Type is also "public" metadata
   files = MultipartEncoder(fields={'file': (filename, data, 'application/octet-stream') } )
   pbar = progbar(files.len)
   monitor = MultipartEncoderMonitor(files, lambda files: pbar.update(monitor.bytes_read - pbar.n))

   public_meta = {'filename' : filename, 'id': iv }
   headers = {'X-File-Metadata' : json.dumps(public_meta), 'Content-type' : monitor.content_type}

   r = requests.post(service, data=monitor, headers=headers, stream=True)
   r.raise_for_status()
   pbar.close()
   return r.json()
