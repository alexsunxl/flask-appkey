import hashlib
from base64 import b64encode
import os
import time


# 生成 key
def generateKey(salt = ''):
  random = b64encode(os.urandom(12)).decode('utf-8')
  stamp = str(time.time())
  sed = (stamp + random + salt).encode('utf-8')
  key = hashlib.sha256(sed).hexdigest()
  return key