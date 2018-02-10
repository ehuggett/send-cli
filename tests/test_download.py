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

from sendclient.download import decrypt_metadata
def test_decrypt_metadata():
    class mock_secretKeys():
        metaKey = b'\xa3\xb4e\xcb\xc1\x89a\xd9G/\xa0v\x12\x9bv\xfd'
        metaIV = bytes(12)
    keys = mock_secretKeys()
    encMeta = b"'b1\x9d\xaf\xb3NZ\xe9\xd8\x1c-\x9djC\x97\xc2\xff\xa0\xf9W\xec\x16\xa6s\xdf\xfb\xcb\xdd\x1d#[x;&0\xe5<\xfbm\xcf\x98\xb5D\xbd\xda\xf8Q\xd3C\xb6\xe1\n\xa9O\x88\x0b\xa2'\x16\xa9\xcc \xadB\x0b\xa5\x88\xf0\x81g\xd3\xd7\x97I0\x9e k $Q\xb6\xc6\x1b\xb1\xfd"

    expected = {'iv': '_A0RiOgeV9NAq4jx', 'type': 'image/svg+xml', 'name': 'send_logo.svg'}
    assert decrypt_metadata(encMeta, keys) == expected

from sendclient.download import sign_nonce
def test_sign_nonce():
    key = b'\x95\xe33b5\xd3\xddxC\x17\xd8Q\xa0`\xc5*\n\xe3q\xf5j\xa6\x00w\xb1r\xef\x8f\xf2\x96Tv=\xb54\x92R.0\xa7@\xcd\x84E\xa8wqv\xf2\x91\xb3\x04\xd5\x9fU!\xcc\xd4y8\xb1z\x8d\x18'
    nonce = b'\x9d\xe7w\xff\xe4\xe8\xd1\x9d\xbd!\xb4b\xa2D8\xe5'
    expected = b'\x85\xaek\xc3~\xb4\nx\xb0\x0e\x97g\xb7\xee+Y\xbc\xfbo\xb4\x02H\xf3y\xdcic\xcb\xcb1i\x02'
    assert sign_nonce(key, nonce) == expected
