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
import utils.site as site
import core.mw as mw
import thisdb

from .site import blueprint

# 获取网站分类
@blueprint.route('/get_site_types', endpoint='get_site_types',methods=['POST'])
@panel_login_required
def get_site_types():
    data = thisdb.getSiteTypesList()
    data.insert(0, {"id": 0, "name": "默认分类"})
    return data


# 添加网站分类
@blueprint.route('/add_site_type', endpoint='add_site_type',methods=['POST'])
@panel_login_required
def add_site_type():
    name = request.form.get('name', '').strip()
    return MwSites.instance().addSiteTypes(name)