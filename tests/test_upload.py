from sendclient.upload import jwk_encode
def test_jwk_encode():
    key = b'\xdf\xd1\x0b\xed+\xaa\xc1cX{\x82\x12\x97c4\xea'
    assert jwk_encode(key) == '39EL7SuqwWNYe4ISl2M06g'

from sendclient.upload import encrypt_file
from hashlib import sha256
def test_encrypt_file(testdata_1M):

    class mock_secretKeys():
        def __init__(self):
            self.encryptKey = b'\x81\xbe^\t\xc1\x11Wa\x03\xa8PvX\xd4x\x91'
            self.encryptIV = b'\x81\xbe^\t\xc1\x11Wa\x03\xa8Pv'

    mock_keys = mock_secretKeys()

    file = open(str(testdata_1M), 'rb')
    encData, keys = encrypt_file(file, mock_keys)

    # The pointer should be at the beginning of the file
    assert encData.tell() == 0

    # check the aes-gcm tag
    encData.seek(-16, 2)
    assert encData.read() == b'L\x1f\xf6\xe3\r\x94L\xd0 \x9b\\\xd1\xaf\xe3>K'

    # To avoid storing the known-good ciphertext for comparison check its sha256 hash, after removing appended gcm tag
    encData.seek(-16, 2)
    encData.truncate()
    encData.seek(0)
    assert sha256(encData.read()).hexdigest() == 'cd55109593e01d4aec4a81ddcaf81d246dc9a17b7776c72cc1f8eead4d5457c0'
