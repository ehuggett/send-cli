import random
import pytest
from hashlib import sha256

@pytest.fixture(scope='session')
def testdata_1M(tmpdir_factory):
   path = tmpdir_factory.mktemp('data').join('1M')

   # save the current state of the random number generator
   state = random.getstate()
   # 'brake' the random number generator by always using the same seed value
   random.seed(a='send-cli test data')
   # get the test data
   data = bytearray(random.getrandbits(8) for _ in range(1024 * 1024) )
   # restore the state of the rng from before we broke it
   random.setstate(state)

   assert sha256(data).hexdigest() == 'c957c34dad5b9b74e8a7ef2c4867b3a6163f2b2020ceb87cd78fa54fce1037de'
   with open(str(path), 'wb') as f:
      f.write(data)

   return path


