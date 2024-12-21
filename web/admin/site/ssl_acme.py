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
import re

from flask import Blueprint, render_template
from flask import request

from admin.user_login_check import panel_login_required

from utils.plugin import plugin as MwPlugin
from utils.site import sites as MwSites
import core.mw as mw
import thisdb

from .site import blueprint


# 获取ACME日志
@blueprint.route('/get_acme_logs', endpoint='get_acme_logs', methods=['POST'])
@panel_login_required
def get_acme_logs():
    log_file = MwSites.instance().acmeLogFile()
    if not os.path.exists(log_file):
        mw.execShell('touch ' + log_file)
    return mw.returnData(True, 'OK', log_file)


@blueprint.route('/create_acme', endpoint='create_acme', methods=['POST'])
@panel_login_required
def create_acme():    
    site_name = request.form.get('siteName', '')
    domains = request.form.get('domains', '')
    force = request.form.get('force', '')
    renew = request.form.get('renew', '')
    email = request.form.get('email', '')
    wildcard_domain = request.form.get('wildcard_domain','')
    apply_type = request.form.get('apply_type', 'file')
    dnspai = request.form.get('dnspai','')
    dns_alias = request.form.get('dns_alias','')
    return MwSites.instance().createAcme(site_name, domains, force, renew, apply_type, dnspai, email, wildcard_domain,dns_alias)







