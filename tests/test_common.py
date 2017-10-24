from sendclient.common import fileSize
def test_fileSize(testdata_1M):
    # open the test file and move the pointer to check fileSize() does not change it
    with open(str(testdata_1M), 'rb') as f:
        f.seek(123)

        # check the correct size is returned for the 1MiB file
        assert fileSize(f) == 1024 * 1024

        # check the pointer has not moved
        assert f.tell() == 123

from sendclient.common import secretKeys
def test_secretKeys_known_good_keys():
    # test data was obtained by adding debug messages to {"commit":"188b28f","source":"https://github.com/mozilla/send/","version":"v1.2.4"}
    testdata = {
        'secretKey': b'q\xd94B\xa1&\x03\xa5<8\xddk\xee.\xea&',
        'encryptKey': b'\xc4\x979\xaa\r\n\xeb\xc7\xa16\xa4%\xfd\xa6\x91\t',
        'authKey': b'5\xa0@\xef\xd0}f\xc7o{S\x05\xe4,\xe1\xe4\xc2\x8cE\xa1\xfat\xc1\x11\x94e[L\x89%\xf5\x8b\xfc\xb5\x9b\x87\x9a\xf2\xc3\x0eKt\xdeL\xab\xa4\xa6%t\xa6"4\r\x07\xb3\xf5\xf6\xb9\xec\xcc\x08\x80}\xea',
        'metaKey': b'\xd5\x9dF\x05\x86\x1a\xfdi\xaeK+\xe7\x8e\x7f\xf2\xfd',
        'password': 'drowssap',
        'url': 'http://192.168.254.87:1443/download/fa4cd959de/#cdk0QqEmA6U8ON1r7i7qJg',
        'newAuthKey': b'U\x02F\x19\x1b\xc1W\x03q\x86q\xbc\xe7\x84WB\xa7(\x0f\x8a\x0f\x17\\\xb9y\xfaZT\xc1\xbf\xb2\xd48\x82\xa7\t\x9a\xb1\x1e{cg\n\xc6\x995+\x0f\xd3\xf4\xb3kd\x93D\xca\xf9\xa1(\xdf\xcb_^\xa3',
    }
    # generate all keys
    keys = secretKeys(secretKey=testdata['secretKey'], password=testdata['password'], url=testdata['url'])

    # Check every key has the expected value
    assert keys.secretKey == testdata['secretKey']
    assert keys.encryptKey == testdata['encryptKey']
    assert keys.authKey == testdata['authKey']
    assert keys.metaKey == testdata['metaKey']
    assert keys.password == testdata['password']
    assert keys.url == testdata['url']
    assert keys.newAuthKey == testdata['newAuthKey']

def test_secretKeys_random_key_lengths():
    # test key generation without providing the master secretKey
    keys = secretKeys()
    assert len(keys.secretKey) == 16
    assert len(keys.encryptKey) == 16
    assert len(keys.encryptIV) == 12
    assert len(keys.authKey) == 64
    assert len(keys.metaKey) == 16
    assert len(keys.deriveNewAuthKey('drowssap', 'https://send.server/download/aFileID/#someSecretKey' )) == 64