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


# 获取证书信息
@blueprint.route('/get_ssl', endpoint='get_ssl', methods=['POST'])
@panel_login_required
def get_ssl():
    site_name = request.form.get('site_name', '')
    ssl_type = request.form.get('ssl_type', '')
    return MwSites.instance().getSsl(site_name, ssl_type)

# 获取证书信息
@blueprint.route('/set_ssl', endpoint='set_ssl', methods=['POST'])
@panel_login_required
def set_ssl():
    site_name = request.form.get('siteName', '')
    key = request.form.get('key', '')
    csr = request.form.get('csr', '')
    return MwSites.instance().setSsl(site_name, key, csr)


# 删除证书
@blueprint.route('/close_ssl_conf', endpoint='close_ssl_conf', methods=['POST'])
@panel_login_required
def close_ssl_conf():
    site_name = request.form.get('siteName', '')
    ssl_type = request.form.get('updateOf', '')
    return MwSites.instance().closeSslConf(site_name)


# 删除证书
@blueprint.route('/delete_ssl', endpoint='delete_ssl', methods=['POST'])
@panel_login_required
def delete_ssl():
    site_name = request.form.get('site_name', '')
    ssl_type = request.form.get('ssl_type', '')
    return MwSites.instance().deleteSsl(site_name, ssl_type)


# 获取证书列表
@blueprint.route('/get_cert_list', endpoint='get_cert_list', methods=['GET','POST'])
@panel_login_required
def get_cert_list():
    return MwSites.instance().getCertList()


# 获取DNSAPI
@blueprint.route('/get_dnsapi', endpoint='get_dnsapi', methods=['GET','POST'])
@panel_login_required
def get_dnsapi():
    return MwSites.instance().getDnsapi()

# 设置DNSAPI
@blueprint.route('/set_dnsapi', endpoint='set_dnsapi', methods=['GET','POST'])
@panel_login_required
def set_dnsapi():
    type = request.form.get('type', '')
    data = request.form.get('data')
    return MwSites.instance().setDnsapi(type,data)

# 设置证书到站点
@blueprint.route('/set_cert_to_site', endpoint='set_cert_to_site', methods=['GET','POST'])
@panel_login_required
def set_cert_to_site():
    site_name = request.form.get('siteName', '')
    cert_name = request.form.get('certName', '')
    return MwSites.instance().setCertToSite(site_name, cert_name)

# 删除证书
@blueprint.route('/remove_cert', endpoint='remove_cert', methods=['GET','POST'])
@panel_login_required
def remove_cert():
    cert_name = request.form.get('certName', '')
    return MwSites.instance().removeCert(cert_name)

# 强制开启HTTPS
@blueprint.route('/http_to_https', endpoint='http_to_https', methods=['GET','POST'])
@panel_login_required
def http_to_https():
    site_name = request.form.get('siteName', '')
    return MwSites.instance().httpToHttps(site_name)

# 强制关闭HTTPS
@blueprint.route('/close_to_https', endpoint='close_to_https', methods=['GET','POST'])
@panel_login_required
def close_to_https():
    site_name = request.form.get('siteName', '')
    return MwSites.instance().closeToHttps(site_name)









