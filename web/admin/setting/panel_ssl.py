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

from utils.setting import setting as MwSetting

from .setting import blueprint
import thisdb

# 获取面板证书信息
@blueprint.route('/get_panel_ssl', endpoint='get_panel_ssl', methods=['POST'])
@panel_login_required
def get_panel_ssl():
    return MwSetting.instance().getPanelSsl()


# 获取面板证书信息
@blueprint.route('/save_panel_ssl', endpoint='save_panel_ssl', methods=['POST'])
@panel_login_required
def save_panel_ssl():
    choose = request.form.get('choose', '').strip()
    certPem = request.form.get('certPem', '').strip()
    privateKey = request.form.get('privateKey', '').strip()
    return MwSetting.instance().savePanelSsl(choose,certPem,privateKey)

# 获取面板证书信息
@blueprint.route('/del_panel_ssl', endpoint='del_panel_ssl', methods=['POST'])
@panel_login_required
def del_panel_ssl():
    choose = request.form.get('choose', '').strip()
    return MwSetting.instance().delPanelSsl(choose)

# 开启面板证书
@blueprint.route('/set_panel_local_ssl', endpoint='set_panel_local_ssl', methods=['POST'])
@panel_login_required
def set_panel_local_ssl():
    cert_type = request.form.get('cert_type', '').strip()
    return MwSetting.instance().setPanelLocalSsl(cert_type)

# 关闭面板证书
@blueprint.route('/close_panel_ssl', endpoint='close_panel_ssl', methods=['POST'])
@panel_login_required
def close_panel_ssl():
    return MwSetting.instance().closePanelSsl()

# 设置面板域名
@blueprint.route('/set_panel_domain', endpoint='set_panel_domain', methods=['POST'])
@panel_login_required
def set_panel_domain():
    domain = request.form.get('domain', '').strip()
    return MwSetting.instance().setPanelDomain(domain)









