from sendclient.common import fileSize
def test_fileSize(testdata_1M):
   # open the test file and move the pointer to check fileSize() does not change it
   with open(str(testdata_1M), 'rb') as f:
      f.seek(123)

      # check the correct size is returned for the 1MiB file
      assert fileSize(f) == 1024 * 1024

      # check the pointer has not moved
      assert f.tell() == 123
