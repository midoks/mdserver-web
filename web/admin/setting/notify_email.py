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

# 获取邮件信息
@blueprint.route('/get_notify_email', endpoint='get_notify_email', methods=['POST'])
@panel_login_required
def get_notify_email():
    notify_email = thisdb.getOptionByJson('notify_email', default={'open':False}, type='notify')

    if 'cfg' in notify_email:
        decrypt_data = mw.deDoubleCrypt('email', notify_email['cfg'])
        notify_email['email'] =  json.loads(decrypt_data)
    else:
        notify_email['email'] = {'smtp_host':'','smtp_port':'','smtp_ssl':'','to_mail_addr':'','username':'','password':''}
    
    return mw.returnData(True,'ok',notify_email)


# 设置邮件信息
@blueprint.route('/set_notify_email', endpoint='set_notify_email', methods=['POST'])
@panel_login_required
def set_notify_email():
    tag = request.form.get('tag', '').strip()
    data = request.form.get('data', '').strip()

    crypt_data = mw.enDoubleCrypt(tag, data)
    
    notify_email = thisdb.getOptionByJson('notify_email', default={'open':False}, type='notify')
    notify_email['cfg'] = crypt_data

    thisdb.setOption('notify_email', json.dumps(notify_email), type='notify')
    return mw.returnData(True,'设置成功')


# 设置邮件测试
@blueprint.route('/set_notify_email_test', endpoint='set_notify_email_test', methods=['POST'])
@panel_login_required
def set_notify_email_test():
    tag = request.form.get('tag', '').strip()
    tag_data = request.form.get('data', '').strip()

    data = json.loads(tag_data)
    test_pass = mw.emailNotifyTest(data)
    if test_pass == True:
        return mw.returnData(True, '验证成功')
    return mw.returnData(False, '验证失败:'+test_pass)

# 切换邮件开关
@blueprint.route('/set_notify_email_enable', endpoint='set_notify_email_enable', methods=['POST'])
@panel_login_required
def set_notify_email_enable():
    tag = request.form.get('tag', '').strip()
    data = request.form.get('data', '').strip()

    notify_email = thisdb.getOptionByJson('notify_email', default={'open':False}, type='notify')

    if notify_email['open']:
        op_action = '关闭'
        notify_email['open'] = False
    else:
        op_action = '开启'
        notify_email['open'] = True

    thisdb.setOption('notify_email', json.dumps(notify_email), type='notify')
    return mw.returnData(True, op_action+'成功')