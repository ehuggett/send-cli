from sendclient.download import splitkeyurl
def test_splitkeyurl():
    url = 'https://send.firefox.com/download/c8ab3218f9/#39EL7SuqwWNYe4ISl2M06g'
    service, urlid, key = splitkeyurl(url)
    assert service == 'https://send.firefox.com/'
    assert urlid == 'c8ab3218f9'
    assert key == '39EL7SuqwWNYe4ISl2M06g'

from sendclient.download import decrypt_filedata
from hashlib import sha256
def test_decrypt_filedata(testdata_1M):
    key = 'gb5eCcERV2EDqFB2WNR4kQ'
    iv = '81be5e09c111576103a85076'
    tag = b'\xd2\xdc\xb1\x0c\xb3D\xc5\xf5\xb3\xc80EOc`v'

    with open(str(testdata_1M), 'rb') as data:
        plain = decrypt(data, key, iv, tag)

    # The pointer should be at the beginning of the file
    assert plain.tell() == 0

    # To avoid storing the known-good plaintext for comparison check its sha256 hash
    assert sha256(plain.read()).hexdigest() == 'cd55109593e01d4aec4a81ddcaf81d246dc9a17b7776c72cc1f8eead4d5457c0'
