# Constants
CHUNK_SIZE = 8192
SPOOL_SIZE = 16 * 1024 * 1024

from tqdm import tqdm

def fileSize(f):
   '''returns the size of a file like object in bytes/octets'''
   offset = f.tell()

   f.seek(0, 2)
   size = f.tell()

   f.seek(offset) # return to the previous position in the file
   return size

def progbar(total):
   return tqdm(unit='B', unit_scale=True, total=total)
