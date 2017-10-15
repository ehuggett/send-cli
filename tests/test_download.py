from sendclient.download import splitkeyurl
def test_splitkeyurl():
   url = 'https://send.firefox.com/download/c8ab3218f9/#39EL7SuqwWNYe4ISl2M06g'
   prefix,urlid,key = splitkeyurl(url)
   assert prefix == 'https://send.firefox.com/'
   assert urlid == 'c8ab3218f9'
   assert key == '39EL7SuqwWNYe4ISl2M06g'

from sendclient.download import key_decode
def test_key_decode():
   jwk = '39EL7SuqwWNYe4ISl2M06g'
   assert key_decode(jwk) == b'\xdf\xd1\x0b\xed+\xaa\xc1cX{\x82\x12\x97c4\xea'


from sendclient.download import decrypt
from hashlib import sha256
def test_decrypt(testdata_1M):
   key = 'gb5eCcERV2EDqFB2WNR4kQ'
   iv = '81be5e09c111576103a85076'
#   tag = b'L\x1f\xf6\xe3\r\x94L\xd0 \x9b\\\xd1\xaf\xe3>K'
   tag = b'\xd2\xdc\xb1\x0c\xb3D\xc5\xf5\xb3\xc80EOc`v'

   with open(str(testdata_1M), 'rb') as data:
      plain = decrypt(data,key,iv,tag)

   # The pointer should be at the beginning of the file
   assert plain.tell() == 0

   # To avoid storing the known-good plaintext for comparison check its sha256 hash
   assert sha256(plain.read()).hexdigest() == 'cd55109593e01d4aec4a81ddcaf81d246dc9a17b7776c72cc1f8eead4d5457c0'
