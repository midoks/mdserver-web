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

from admin import model
from admin import session
from admin.model import db,TempLogin
from admin.user_login_check import panel_login_required

import core.mw as mw
import utils.config as utils_config

from .main import blueprint


@blueprint.route('/get_auth_secret', endpoint='get_auth_secret', methods=['POST'])
@panel_login_required
def get_auth_secret():
    reset = request.form.get('reset', '')
    __file = mw.getCommonFile()

    import pyotp
    auth = __file['auth_secret']
    tag = 'mdserver-web'
    if os.path.exists(auth) and reset != '1':
        content = mw.readFile(auth)
        sec = mw.deDoubleCrypt(tag,content)
    else:
        sec = pyotp.random_base32()
        crypt_data = mw.enDoubleCrypt(tag, sec)
        mw.writeFile(auth, crypt_data)

    ip = mw.getHostAddr()
    url = pyotp.totp.TOTP(sec).provisioning_uri(name=ip, issuer_name=tag)

    rdata = {}
    rdata['secret'] = sec
    rdata['url'] = url
    return mw.returnData(True, '设置成功!', rdata)
        