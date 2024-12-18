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


# 获取代理列表
@blueprint.route('/get_proxy_list', endpoint='get_proxy_list', methods=['POST'])
@panel_login_required
def get_proxy_list():
    site_name = request.form.get("siteName", '')
    return MwSites.instance().getProxyList(site_name)

# 获取代理列表
@blueprint.route('/set_proxy', endpoint='set_proxy', methods=['POST'])
@panel_login_required
def set_proxy():
    site_name = request.form.get('siteName', '')
    site_from = request.form.get('from', '')
    to = request.form.get('to', '')
    host = request.form.get('host', '')
    name = request.form.get('name', '')
    open_proxy = request.form.get('open_proxy', '')
    open_cors = request.form.get('open_cors','')
    open_cache = request.form.get('open_cache', '')
    cache_time = request.form.get('cache_time', '')
    proxy_id = request.form.get('id', '')
    return MwSites.instance().setProxy(site_name,site_from,to,host,name,open_proxy,open_cors,open_cache,cache_time, proxy_id)

# 设置代理状态
@blueprint.route('/set_proxy_status', endpoint='set_proxy_status', methods=['POST'])
@panel_login_required
def set_proxy_status():
    site_name = request.form.get("siteName", '')
    status = request.form.get("status", '')
    proxy_id = request.form.get("id", '')
    return MwSites.instance().setProxyStatus(site_name,proxy_id,status)


# 获取代理配置
@blueprint.route('/get_proxy_conf', endpoint='get_proxy_conf', methods=['POST'])
@panel_login_required
def get_proxy_conf():
    site_name = request.form.get("siteName", '')
    rid = request.form.get("id", '')
    return MwSites.instance().getProxyConf(site_name, rid)

# 设置代理
@blueprint.route('/save_proxy_conf', endpoint='save_proxy_conf', methods=['POST'])
@panel_login_required
def save_proxy_conf():
    site_name = request.form.get("siteName", '')
    rid = request.form.get("id", '')
    config = request.form.get("config", "")
    return MwSites.instance().saveProxyConf(site_name, rid, config)


# 删除代理配置
@blueprint.route('/del_proxy', endpoint='del_proxy', methods=['POST'])
@panel_login_required
def del_proxy():
    site_name = request.form.get("siteName", '')
    rid = request.form.get("id", '')
    return MwSites.instance().delProxy(site_name, rid)




