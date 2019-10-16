# -*- coding: utf-8 -*-

import json

import requests
import time
import hashlib

url = 'http://api.mix2.zthysms.com/v2/sendSms'
headers = {
    "Content-Type": "application/json"
}


# 发送验证码
def sendcaptch(mobile, captch):
    tKey = str(time.time())[:10]
    m = hashlib.md5(hashlib.md5('lucmf2nJ').hexdigest() + tKey)
    password = m.hexdigest()
    body = {
        "content": '',
        "mobile": '',
        "username": "ypk888hy",
        "password": password,
        "tKey": tKey,
        "ext": "9999"
    }

    body['content'] = "【银票库】您的验证码是：{}，请在5分钟内验证，本验证码使用后，将自动失效。如有疑问请联系：400-686-5776。".format(captch)
    body['mobile'] = mobile
    res = requests.post(url=url, headers=headers, data=json.dumps(body))
    print(res)
    for i in res:
        print(i)
    return res


# 发送提醒信息。
def sendremindmsg(mobile, msg):
    tKey = str(time.time())[:10]
    m = hashlib.md5((hashlib.md5('lucmf2nJ'.encode('utf8')).hexdigest() + tKey).encode('utf8'))
    password = m.hexdigest()
    body = {
        "content":'',
        "mobile": '',
        "username": "ypk888hy",
        "password": password,
        "tKey": tKey,
        "ext": "9999"
    }
    body['content'] = "【银票库】" + msg
    body['mobile'] = str(mobile)
    res = requests.post(url=url, headers=headers, data=json.dumps(body))
    for i in res:
        print(i)
    return res
