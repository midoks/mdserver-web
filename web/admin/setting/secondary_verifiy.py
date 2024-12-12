# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import re
import json
import os
import time

from flask import Blueprint, render_template
from flask import request

from admin import session
from admin.user_login_check import panel_login_required

import core.mw as mw
import utils.config as utils_config

from .setting import blueprint
import thisdb

# 获取二次验证信息
@blueprint.route('/get_auth_secret', endpoint='get_auth_secret', methods=['POST'])
@panel_login_required
def get_auth_secret():
    import pyotp

    reset = request.form.get('reset', '')
    tag = 'mdserver-web'
    two_step_verification = thisdb.getOptionByJson('two_step_verification', default={'open':False})

    if 'secret' in two_step_verification and reset != '1':
        secret = mw.deDoubleCrypt(tag, two_step_verification['secret'])
    else:
        secret = pyotp.random_base32()
        crypt_data = mw.enDoubleCrypt(tag, secret)
        two_step_verification['secret'] = crypt_data
        thisdb.setOption('two_step_verification', json.dumps(two_step_verification))

    ip = mw.getHostAddr()
    url = pyotp.totp.TOTP(secret).provisioning_uri(name=ip, issuer_name=tag)

    rdata = {}
    rdata['secret'] = secret
    rdata['url'] = url
    return mw.returnData(True, '设置成功!', rdata)


# 设置二次验证，加强安全登录
@blueprint.route('/set_auth_secret', endpoint='set_auth_secret', methods=['POST'])
@panel_login_required
def set_auth_secret():
    two_step_verification = thisdb.getOptionByJson('two_step_verification', default={'open':False})
    if two_step_verification['open']:
        two_step_verification['open'] = False
        thisdb.setOption('two_step_verification', json.dumps(two_step_verification))
        return mw.returnData(True, '关闭成功!', 0)
    else:
        two_step_verification['open'] = True
        thisdb.setOption('two_step_verification', json.dumps(two_step_verification))
        return mw.returnData(True, '开启成功!', 1)


        