import pytest

import random
import hashlib
@pytest.fixture(scope='function')
def testdata_1M(tmpdir_factory):
    '''Creates and returns the path to the 1MB test file'''
    path = tmpdir_factory.mktemp('data').join('1M')

    # Create a new instance of random with a fixed seed
    predictable = random.Random(x='send-cli test data')
    data = bytearray(predictable.getrandbits(8) for _ in range(1024 * 1024))

    assert hashlib.sha256(data).hexdigest() == 'c957c34dad5b9b74e8a7ef2c4867b3a6163f2b2020ceb87cd78fa54fce1037de'

    with open(str(path), 'wb') as f:
        f.write(data)

    return str(path)