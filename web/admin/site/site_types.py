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

# 获取网站分类
@blueprint.route('/get_site_types', endpoint='get_site_types',methods=['POST'])
@panel_login_required
def get_site_types():
    data = thisdb.getSiteTypesList()
    data.insert(0, {"id": 0, "name": "默认分类"})
    return mw.returnData(True, "ok", data)


# 添加网站分类
@blueprint.route('/add_site_type', endpoint='add_site_type',methods=['POST'])
@panel_login_required
def add_site_type():
    name = request.form.get('name', '').strip()
    return MwSites.instance().addSiteTypes(name)


# 添加网站分类
@blueprint.route('/remove_site_type', endpoint='remove_site_type',methods=['POST'])
@panel_login_required
def remove_site_type():
    site_type_id = request.form.get('id', '')
    if mw.M('site_types').where('id=?', (site_type_id,)).count() == 0:
        return mw.returnData(False, "指定分类不存在!")
    mw.M('site_types').where('id=?', (site_type_id,)).delete()
    mw.M("sites").where("type_id=?", (site_type_id,)).save("type_id", (0,))
    return mw.returnData(True, "分类已删除!")

# 修改网站分类
@blueprint.route('/modify_site_type_name', endpoint='modify_site_type_name',methods=['POST'])
@panel_login_required
def modify_site_type_name():
    name = request.form.get('name', '').strip()
    site_type_id = request.form.get('id', '')
    if not name:
        return mw.returnData(False, "分类名称不能为空")
    if len(name) > 18:
        return mw.returnData(False, "分类名称长度不能超过6个汉字或18位字母")
    if mw.M('site_types').where('id=?', (site_type_id,)).count() == 0:
        return mw.returnData(False, "指定分类不存在!")
    mw.M('site_types').where('id=?', (site_type_id,)).setField('name', name)
    return mw.returnData(True, "修改成功!")

# 设置网站分类
@blueprint.route('/set_site_type', endpoint='set_site_type',methods=['POST'])
@panel_login_required
def set_site_type():
    # 设置指定站点的分类
    site_ids = request.form.get('site_ids', '')
    site_type_id = request.form.get('id', '')
    site_ids = json.loads(site_ids)
    for site_id in site_ids:
        mw.M('sites').where('id=?', (site_id,)).setField('type_id', site_type_id)
    return mw.returnData(True, "设置成功!")





