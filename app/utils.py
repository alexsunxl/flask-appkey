from hashlib import sha1
from base64 import urlsafe_b64encode, urlsafe_b64decode


def urlsafe_base64_encode(data):
  """urlsafe的base64编码:
    String -> String
  """
  ret = urlsafe_b64encode(b(data))
  return s(ret)


def urlsafe_base64_decode(data):
  """urlsafe的base64解码:
    String -> String
  """
  ret = urlsafe_b64decode(s(data))
  return ret


def s(data):
  if isinstance(data, bytes):
    data = data.decode('utf-8')
  return data

def b(data):
  if isinstance(data, str):
    return data.encode('utf-8')
  return data