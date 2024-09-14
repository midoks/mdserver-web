# coding:utf-8

import sys
import io
import os
import time
import re
import requests
import base64


# 8001 / 7788
goedge_addr = 'http://127.0.0.2:8009'
access_keyid = "xxx"
access_key = "xxx"

sys.path.append(os.getcwd() + "/class/core")
import mw

domain = sys.argv[1]
ssl_path = sys.argv[2]


def getToken():
    api_url = goedge_addr+'/APIAccessTokenService/getAPIAccessToken'
    # print(api_url)

    post_data = {
        "type": "admin",
        "accessKeyId": access_keyid,
        "accessKey": access_key
    }
    # json_data = mw.getJson(post_data)
    # print(json_data)
    data = requests.post(api_url,json=post_data)
    data_obj = data.json()

    return data_obj['data']['token']

token = getToken()

def commonReq(url, data):
    headers = {
        'X-Edge-Access-Token': token
    }
    api_url = goedge_addr+'/'+url

    json_data = mw.getJson(data)
    print(json_data)
    resp_data = requests.post(api_url,json=json_data, headers=headers)
    return resp_data.json()


def createSSLCert(domain):
    ssl_cer_file = ssl_path + '/'+domain+'.cer'
    cer_data = mw.readFile(ssl_cer_file)
    cer_data = mw.base64StrEncode(cer_data)
    # print('cer',cer_data)

    ssl_key_file = ssl_path + '/'+domain+'.key'
    key_data = mw.readFile(ssl_key_file)
    key_data = mw.base64StrEncode(key_data)
    # print('key',key_data)

    return ''

    request_data = {
    	"isOn":False,
    	# "userId":"0",
    	"name":"test",
    	"isCA":True,
    	"description":domain,
    	"serverName":domain,
    	"certData":cer_data,
    	'keyData':key_data,
    	'dnsNames':[domain,"*."+domain]
    }
    print(request_data)
    response_data = commonReq('/SSLCertService/createSSLCert', request_data)
    # print(response_data)
    return response_data

createSSLCert(domain)


print(domain,ssl_path)