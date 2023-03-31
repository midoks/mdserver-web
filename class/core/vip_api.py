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


class vip_api:

    def __init__(self):
        pass

    def loginApi(self):
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        print(username, password)

        return mw.returnJson(False, "测试中!")
