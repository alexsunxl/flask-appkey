from flask import Flask, render_template, request
from genKey import generateKey
from auth import Auth
import requests
import json
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson.json_util import dumps


app = Flask(__name__)
client = MongoClient(host='db', port=27017, connect=False)
db = client.appkey


def initUserKey(name):
  """
    @param name 用户名
    初始化一个用户的appkey数据，并插入一行
  """
  access_key = generateKey(name)
  secret_key = generateKey('secret')

  data = {
    'name': name,
    'access_key' : access_key,
    'secret_key' : secret_key,
    'time' : 0,
    'created_at': datetime.now(),
    'updated_at': datetime.now(),
  }
  db.user_key.insert_one(data)

  return data


@app.route('/')
def index():
  """
    appkey的面板信息:
  """
  # 用户名字 并设置默认值
  name = request.args.get('name', 'alex')
  data = db.user_key.find_one({'name': name})

  # 如果没有该用户的keyinfo，就创建并插入
  if not bool(data) :
    data = initUserKey(name)

  return render_template(
    'index.html',
    data = data
  )

@app.route('/apply')
def apply():
  """
    加密并使用appkey:
  """
  # 用户名字 并设置默认值
  name = request.args.get('name', 'alex')
  params = request.args.get('params', 'hello')

  data = db.user_key.find_one({'name': name})

  # 如果没有该用户的keyinfo，就创建并插入
  if not bool(data) :
    data = initUserKey(name)

  access_key = data['access_key']
  secret_key = data['secret_key']

  # @todo 
  # 请求参数 去重，排序

  # 构造请求参数
  request_data = {
    'params': params,
  }

  token = Auth.genToken(access_key, secret_key, request_data)

  # 构造调用请求
  headers = {
    'Authorization' : token,
  }
  host = 'http://localhost/'
  url = host + 'cgi'

  resp = requests.post(url, request_data, headers=headers)
  text = resp.text

  return text


@app.route('/cgi', methods=['POST'])
def cgi():
  """
    接收token和data 并检验
  """
  data = request.form 
  token = request.headers.get('Authorization')
  access_key = Auth.getAccessKey(token)

  # 通过access_key去查找对应的appkeyinfo
  user_key = db.user_key.find_one({'access_key': access_key})
  access_key = user_key['access_key']
  secret_key = user_key['secret_key']



  # 检验token
  if token != Auth.genToken(access_key, secret_key, data) :
    return 'fail, 认证失败'

  one_minute_ago = datetime.now() - timedelta(minutes=1)
  record = db.key_record.find_one({'token': token, 'created_at': {'$gte': one_minute_ago}})

  # 限制调用时间
  limit_minutes = 5
  # 限制调用次数
  limit_time = 10
  # 某个用户在一段时间内的调用次数
  minutes_ago = datetime.now() - timedelta(minutes=limit_minutes)
  records = db.key_record.find({
    'access_key': access_key,
    'created_at': {'$gte': minutes_ago}
  })

  if records.count() >= limit_time : 
    return 'fail, 调用次数过多，请稍后再试' 

  # 调用成功并插入调用记录
  if not bool(record) :
    db.user_key.update_one(
      {'access_key': access_key},
      {
        '$inc': {
          'time': 1
        }
      }, upsert=False
    )
    db.key_record.insert_one({
      'access_key': access_key,
      'token': token,
      'created_at': datetime.now(),
      'data': json.dumps(data),
    })
    return 'sucess'
  else :
    return 'fail, 调用参数重复，请一分钟后再试'

@app.route('/records')
def recodes():
  """
    查看所有调用次数的面板
  """
  records = db.key_record.find({})

  return render_template(
    'records.html',
    records = records
  )


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True, port=80)
