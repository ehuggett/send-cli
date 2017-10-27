from sendclient.download import splitkeyurl
def test_splitkeyurl():
    url = 'https://send.firefox.com/download/c8ab3218f9/#39EL7SuqwWNYe4ISl2M06g'
    service, urlid, key = splitkeyurl(url)
    assert service == 'https://send.firefox.com/'
    assert urlid == 'c8ab3218f9'
    assert key == '39EL7SuqwWNYe4ISl2M06g'

from sendclient.download import decrypt_filedata
import hashlib
def test_decrypt_filedata(testdata_1M):

    class mock_secretKeys():
        def __init__(self):
            self.encryptKey = b'\x81\xbe^\t\xc1\x11Wa\x03\xa8PvX\xd4x\x91'
            self.encryptIV = b'\x81\xbe^\t\xc1\x11Wa\x03\xa8Pv'

    keys = mock_secretKeys()
    gcmTag = b'\xd2\xdc\xb1\x0c\xb3D\xc5\xf5\xb3\xc80EOc`v'

    encData = open(testdata_1M, 'a+b')
    encData.write(gcmTag)
    encData.seek(0)

    plain = decrypt_filedata(encData, keys)

    # The pointer should be at the beginning of the file
    assert plain.tell() == 0

    # To avoid storing the known-good plaintext for comparison check its sha256 hash
    assert hashlib.sha256(plain.read()).hexdigest() == 'cd55109593e01d4aec4a81ddcaf81d246dc9a17b7776c72cc1f8eead4d5457c0'
    encData.close
