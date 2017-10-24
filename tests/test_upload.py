from sendclient.upload import encrypt_file
from hashlib import sha256
def test_encrypt_file(testdata_1M):

    class mock_secretKeys():
        def __init__(self):
            self.encryptKey = b'\x81\xbe^\t\xc1\x11Wa\x03\xa8PvX\xd4x\x91'
            self.encryptIV = b'\x81\xbe^\t\xc1\x11Wa\x03\xa8Pv'

    keys = mock_secretKeys()
    file = open(str(testdata_1M), 'rb')

    encData = encrypt_file(file, keys)

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

from sendclient.upload import encrypt_metadata
def test_encrypt_metadata():

    class mock_secretKeys():
        def __init__(self):
            self.metaKey = b'\x92\x0b*JH+i>\x1f\x0ey\x90 l\x99\xdb'
            self.metaIV = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            self.encryptIV = b'\xa9\x1b\x80\x7fzY\xb4\xb9\x94\xaas\xc0'

    keys = mock_secretKeys()

    fileName = 'testfile'
    encMeta = encrypt_metadata(keys, fileName)

    expectedValue = b'V\xad`(\xf8\xb3\x84Y\xfb@ \xb9\xb7\xd8)\x8b\xb51y\xed\xb1\xc2\xc0\x9b\xb6:\t\xda\x84\xc5\x12\xa4\xf3b\x00\x83\x07\xae\x81\xf1%\xc3CM\x04\xbd\xae\x9d\xaf\xc2\xd4VF5\xdb\xe7\xf0l\xa1\xe6IN\xeb\xf3:\xbe\xc3j6F&\x8b\xd75\x00\xce{\xfb\xc1)\x8f\xe4\x8c\xac\xd0\xc2\xd5_\xd7\xa9\xe8]\x13B\x00\xdd\x89!'
    assert encMeta == expectedValue

from sendclient.upload import sign_nonce
def test_sign_nonce():
    key = b'\x1d\x9d\x82^V\xf45C\xc0B\x81\xcbq\x1e>\x1a\x02*\x954`ot\x01\x8b0\xcaw\x81M\xceS*\xa5\xf8\x80h\xb4\xde7\xbe\x88\x83ll\xf8\x11~J\xd5*\x05\xe1a\x9e\x95Kn/\x82H\xd4B\xfa'
    nonce = b'\xb3\x16\xc4\x7fP\xf3\xc9\xaa\x17H\x8eY\xb8{\xf3&'
    # test for expected output
    assert sign_nonce(key, nonce) == b'A\xde6*\x1c\x05\x04\x94\xa8U+\x97\xcd\xf62\xa0\x89;\xee\x00E\x05\xed\x84^\xfdB\x82\x85lM\xf8'