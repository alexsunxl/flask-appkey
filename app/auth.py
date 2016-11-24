import hmac
from hashlib import sha1
import json
from utils import urlsafe_base64_encode, b

class Auth(object):
  def __init__(self, access_key, secret_key):
    self.__access_key = access_key
    self.__secret_key = b(secret_key)

  @staticmethod
  def genToken(access_key, secret_key, data):
    """
      生成token
    """
    # 请求参数处理
    data = json.dumps(data, separators=(',', ':'))
    data = b(data)
    secret_key = b(secret_key)

    # 混入data 加密
    hashed = hmac.new(secret_key, data, sha1)

    # 安全转移
    based = urlsafe_base64_encode(hashed.digest())
    data = urlsafe_base64_encode(data)

    # 格式化
    token = '{0}:{1}:{2}'.format(access_key, based, data)

    return token


  @staticmethod
  def getAccessKey(token):
    """
      从token中获取 access_key
    """
    params = token.split(':')

    return params[0]



