from common import checkServerVersion
def test_checkServerVersion():
   service = 'https://send.firefox.com/'
   ignoreVersion = False
   assert checkServerVersion(service, ignoreVersion) == True

from common import fileSize
def test_fileSize():

   # open the test file and move the pointer to check fileSize() does not change it
   with open('tests/data/1M', 'rb') as f:
      f.seek(123)

      # check the correct size is returned for the 1MiB file
      assert fileSize(f) == 1024 * 1024

      # check the pointer has not moved
      assert f.tell() == 123
