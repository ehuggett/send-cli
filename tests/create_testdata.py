import random

# sha256 - name
# c957c34dad5b9b74e8a7ef2c4867b3a6163f2b2020ceb87cd78fa54fce1037de  - data/1M
# 085ff278c9d0c790f4a99a00917c35b5f9c6290130fb5e92c2ce0244d9e4049a  - data/128M

random.seed(a='send-cli test data')
data = bytearray(random.getrandbits(8) for _ in range(1024 * 1024) )
with open('data/1M', 'wb') as f:
   f.write(data)

#random.seed(a='send-cli test data')
#data = bytearray(random.getrandbits(8) for _ in range(1024 * 1024 * 128) )
#with open('data/128M', 'wb') as f:
#   f.write(data)
