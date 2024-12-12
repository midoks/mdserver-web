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
@blueprint.route('/get_notify_tgbot', endpoint='get_notify_tgbot', methods=['POST'])
@panel_login_required
def get_notify_tgbot():
    notify_tgbot = thisdb.getOptionByJson('notify_tgbot', default={'open':False}, type='notify')
    if 'cfg' in notify_tgbot:
        decrypt_data = mw.deDoubleCrypt('tgbot', notify_tgbot['cfg'])
        notify_tgbot['tgbot'] =  json.loads(decrypt_data)
    else:
        notify_tgbot['tgbot'] = []
    return mw.returnData(True,'ok',notify_tgbot)


# 设置邮件信息
@blueprint.route('/set_notify_tgbot', endpoint='set_notify_tgbot', methods=['POST'])
@panel_login_required
def set_notify_tgbot():
    data = request.form.get('data', '').strip()

    crypt_data = mw.enDoubleCrypt('tgbot', data)
    
    notify_tgbot = thisdb.getOptionByJson('notify_tgbot', default={'open':False}, type='notify')
    notify_tgbot['cfg'] = crypt_data

    thisdb.setOption('notify_tgbot', json.dumps(notify_tgbot), type='notify')
    return mw.returnData(True,'设置成功')


# 设置邮件测试
@blueprint.route('/set_notify_tgbot_test', endpoint='set_notify_tgbot_test', methods=['POST'])
@panel_login_required
def set_notify_tgbot_test():
    tag_data = request.form.get('data', '').strip()

    tmp = json.loads(tag_data)
    test_pass = mw.tgbotNotifyTest(tmp['app_token'], tmp['chat_id'])
    if test_pass == True:
        return mw.returnData(True, '验证成功')
    return mw.returnData(False, '验证失败:'+test_pass)

# 切换邮件开关
@blueprint.route('/set_notify_tgbot_enable', endpoint='set_notify_tgbot_enable', methods=['POST'])
@panel_login_required
def set_notify_tgbot_enable():
    tag = request.form.get('tag', '').strip()
    data = request.form.get('data', '').strip()

    notify_tgbot = thisdb.getOptionByJson('notify_tgbot', default={'open':False}, type='notify')

    if notify_tgbot['open']:
        op_action = '关闭'
        notify_tgbot['open'] = False
    else:
        op_action = '开启'
        notify_tgbot['open'] = True

    thisdb.setOption('notify_tgbot', json.dumps(notify_tgbot), type='notify')
    return mw.returnData(True, op_action+'成功')