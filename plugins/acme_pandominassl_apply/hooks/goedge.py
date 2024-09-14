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

# 指定用户
userId = 1

sys.path.append(os.getcwd() + "/class/core")
import mw

domain = sys.argv[1]
ssl_path = sys.argv[2]


def getToken():
    api_url = goedge_addr+'/APIAccessTokenService/getAPIAccessToken'
    post_data = {
        "type": "admin",
        "accessKeyId": access_keyid,
        "accessKey": access_key
    }
    data = requests.post(api_url,json=post_data)
    data_obj = data.json()

    return data_obj['data']['token']

token = getToken()

def commonReq(url, data):
    headers = {
        'X-Edge-Access-Token': token
    }
    api_url = goedge_addr+url
    resp_data = requests.post(api_url,json=data, headers=headers)
    return resp_data.json()

def listSSLCerts(domain):
    request_data = {
        "userId":userId,
        "isCA":False,
        "keyword": "ACME泛域名自动上传",
        "domains":[domain,"*."+domain],
        "size":1
    }
    response_data = commonReq('/SSLCertService/listSSLCerts', request_data)

    data = response_data['data']['sslCertsJSON']
    data = mw.base64StrDecode(data)
    data = mw.getObjectByJson(data)
    # print(data)
    return data



# createSSLCert(domain)
def createSSLCert(domain, did=0):

    ssl_cer_file = ssl_path + '/'+domain+'.cer'

    if not os.path.exists(ssl_cer_file):
        print("没有有效证书!")
        return ''
    # print(ssl_cer_file)
    ssl_info = mw.getCertName(ssl_cer_file)
    cer_data = mw.readFile(ssl_cer_file)
    cer_data = mw.base64StrEncode(cer_data)
    # print('cer',cer_data)

    ssl_key_file = ssl_path + '/'+domain+'.key'
    key_data = mw.readFile(ssl_key_file)
    key_data = mw.base64StrEncode(key_data)
    # print('ssl_info',ssl_info)

    timeBeginAt = int(time.mktime(time.strptime(ssl_info['notBefore'], "%Y-%m-%d")))
    timeEndAt = int(time.mktime(time.strptime(ssl_info['notAfter'], "%Y-%m-%d")))

    request_data = {
        "isOn":True,
        "userId":userId,
        "name": "ACME泛域名自动上传",
        "isCA":False,
        "description":domain,
        "serverName":domain,
        "certData":cer_data,
        "keyData":key_data,
        "timeBeginAt":timeBeginAt,
        "timeEndAt": timeEndAt,
        "dnsNames":[domain,"*."+domain],
        "commonNames":[ssl_info['issuer']]
    }
    
    if did>0:
        request_data['sslCertId'] = did
        # print(request_data)
        response_data = commonReq('/SSLCertService/updateSSLCert', request_data)
        print('更新成功',domain,response_data)
        return response_data
    else:
        # print(request_data)
        response_data = commonReq('/SSLCertService/createSSLCert', request_data)
        print('创建成功',domain,response_data)
        return response_data
    return response_data

def autoSyncDomain(domain):
    data = listSSLCerts(domain)
    if len(data) > 0 :
        did = data[0]['id']
        createSSLCert(domain,did)
    else:
        createSSLCert(domain)
    print(data)


autoSyncDomain(domain)
print(domain,ssl_path)