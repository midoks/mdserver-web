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

@blueprint.route('/get_cli_php_version', endpoint='get_cli_php_version',methods=['POST'])
@panel_login_required
def get_cli_php_version():
    php_dir = mw.getServerDir() + '/php'
    if not os.path.exists(php_dir):
        return mw.returnData(False, '未安装PHP,无法设置')

    php_bin = '/usr/bin/php'
    data = MwSites.instance().getPhpVersion()
    php_versions = data['data']
    php_versions = php_versions[1:]

    if len(php_versions) < 1:
        return mw.returnData(False, '未安装PHP,无法设置')

    if os.path.exists(php_bin) and os.path.islink(php_bin):
        link_re = os.readlink(php_bin)
        for v in php_versions:
            if link_re.find(v['version']) != -1:
                return {"select": v, "versions": php_versions}

    return {"select": php_versions[0],"versions": php_versions}

@blueprint.route('/set_cli_php_version', endpoint='set_cli_php_version',methods=['POST'])
@panel_login_required
def set_cli_php_version():
    if mw.isAppleSystem():
        return mw.returnData(False, "开发机不可设置!")
    version = request.form.get('version', '')
    return MwSites.instance().setCliPhpVersion(version)




