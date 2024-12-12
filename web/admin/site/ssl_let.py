# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os
import json

from flask import Blueprint, render_template
from flask import request

from admin.user_login_check import panel_login_required

from utils.plugin import plugin as MwPlugin
from utils.site import sites as MwSites
import core.mw as mw
import thisdb

from .site import blueprint


# 获取ACME日志
@blueprint.route('/get_let_logs', endpoint='get_let_logs', methods=['POST'])
@panel_login_required
def get_let_logs():
    log_file = MwSites.instance().letLogFile()
    if not os.path.exists(log_file):
        mw.execShell('touch ' + log_file)
    return mw.returnData(True, 'OK', log_file)


@blueprint.route('/create_let', endpoint='create_let', methods=['POST'])
@panel_login_required
def create_let():
    site_name = request.form.get('siteName', '')
    domains = request.form.get('domains', '')
    force = request.form.get('force', '')
    renew = request.form.get('renew', '')
    email = request.form.get('email', '')
    wildcard_domain = request.form.get('wildcard_domain','')
    apply_type = request.form.get('apply_type', 'file')
    dnspai = request.form.get('dnspai','') 
    return MwSites.instance().createLet(site_name, domains, force, renew, apply_type, dnspai, email, wildcard_domain)







