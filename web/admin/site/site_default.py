# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os

from flask import Blueprint, render_template
from flask import request

from admin.user_login_check import panel_login_required

from utils.plugin import plugin as MwPlugin
from utils.site import sites as MwSites

import core.mw as mw
import thisdb

from .site import blueprint

@blueprint.route('/get_site_doc', endpoint='get_site_doc',methods=['POST'])
def get_site_doc():
    stype = request.form.get('type', '0').strip()
    vlist = []
    vlist.append('')
    vlist.append(mw.getServerDir() +'/openresty/nginx/html/index.html')
    vlist.append(mw.getServerDir() + '/openresty/nginx/html/404.html')
    vlist.append(mw.getServerDir() +'/openresty/nginx/html/index.html')
    vlist.append(mw.getServerDir() + '/web_conf/stop/index.html')
    data = {}
    data['path'] = vlist[int(stype)]
    return mw.returnData(True, 'ok', data)