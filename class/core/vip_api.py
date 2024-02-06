# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------
# VIP用户管理
# ---------------------------------------------------------------------------------

import mw

from flask import request
import requests


class vip_api:

    api_url = 'https://wo.midoks.icu/api/wp-json/vip'

    def __init__(self):
        pass

    def loginApi(self):
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        password = mw.aesEncrypt(password)

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        print("name:", str(username))
        print("pwd:", str(password))
        args = {
            'name': username,
            'pass': password
        }
        data = requests.post(self.api_url + '/v1/login',
                             data=args, headers=headers)

        print(data.text)

        return mw.returnJson(False, "测试中!")
