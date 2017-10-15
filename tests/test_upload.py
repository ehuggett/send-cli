from sendclient.upload import jwk_encode
def test_jwk_encode():
   key = b'\xdf\xd1\x0b\xed+\xaa\xc1cX{\x82\x12\x97c4\xea'
   assert jwk_encode(key) == '39EL7SuqwWNYe4ISl2M06g'

from sendclient.upload import encrypt
from hashlib import sha256
def test_encrypt(monkeypatch, testdata_1M):
   def mockrandom(number_of_bytes):
      return b'\x81\xbe^\t\xc1\x11Wa\x03\xa8PvX\xd4x\x91'[:number_of_bytes]

   # use the same 'random' bytes every time (for encryption key and IV)
   monkeypatch.setattr('sendclient.upload.get_random_bytes', mockrandom)

   fh = open(str(testdata_1M), 'rb')
   ciphertext,key,iv = encrypt(fh)

   assert key == 'gb5eCcERV2EDqFB2WNR4kQ'
   assert iv == '81be5e09c111576103a85076'

   # The pointer should be at the beginning of the file
   assert ciphertext.tell() == 0

   # check the aes-gcm tag
   ciphertext.seek(-16,2)
   assert ciphertext.read() == b'L\x1f\xf6\xe3\r\x94L\xd0 \x9b\\\xd1\xaf\xe3>K'

   # To avoid storing the known-good ciphertext for comparison check its sha256 hash, after removing appended gcm tag
   ciphertext.seek(-16,2)
   ciphertext.truncate()
   ciphertext.seek(0)
   assert sha256(ciphertext.read()).hexdigest() == 'cd55109593e01d4aec4a81ddcaf81d246dc9a17b7776c72cc1f8eead4d5457c0'

