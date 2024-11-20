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

@blueprint.route('/get_logs', endpoint='get_logs',methods=['POST'])
@panel_login_required
def get_logs():
    siteName = request.form.get('siteName', '')
    return MwSites.instance().getLogs(siteName)


@blueprint.route('/get_error_logs', endpoint='get_error_logs',methods=['POST'])
@panel_login_required
def get_error_logs():
    siteName = request.form.get('siteName', '')
    return MwSites.instance().getErrorLogs(siteName)







