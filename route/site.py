# coding:utf-8

import time
import sys
import os
import json

from flask import Flask
from flask import Blueprint, render_template
from flask import request

site = Blueprint('site', __name__, template_folder='templates')

sys.path.append("class/core")
import public
import site_api


@site.route('/')
def index():
    return render_template('default/site.html')


@site.route('/list', methods=['POST'])
def list():
    return site_api.site_api().list()


@site.route('get_php_version', methods=['POST'])
def getPhpVersion():
    return site_api.site_api().getPhpVersion()


@site.route('get_domain', methods=['POST'])
def getDomain():
    pid = request.form.get('pid', '').encode('utf-8')
    return site_api.site_api().getDomain(pid)


@site.route('get_index', methods=['POST'])
def getIndex():
    sid = request.form.get('id', '').encode('utf-8')
    data = {}
    index = site_api.site_api().getIndex(sid)
    data['index'] = index
    return public.getJson(data)


@site.route('set_index', methods=['POST'])
def setIndex():
    sid = request.form.get('id', '').encode('utf-8')
    index = request.form.get('index', '').encode('utf-8')
    return site_api.site_api().setIndex(sid, index)


@site.route('get_logs', methods=['POST'])
def getLogs():
    siteName = request.form.get('siteName', '').encode('utf-8')
    return site_api.site_api().getLogs(siteName)


@site.route('get_site_php_version', methods=['POST'])
def getSitePhpVersion():
    siteName = request.form.get('siteName', '').encode('utf-8')
    return site_api.site_api().getSitePhpVersion(siteName)


@site.route('get_host_conf', methods=['POST'])
def getHostConf():
    siteName = request.form.get('siteName', '').encode('utf-8')
    host = site_api.site_api().getHostConf(siteName)
    return public.getJson({'host': host})


@site.route('get_root_dir', methods=['POST'])
def getRootDir():
    data = {}
    data['dir'] = public.getWwwDir()
    return public.getJson(data)


@site.route('set_end_date', methods=['POST'])
def setEndDate():
    sid = request.form.get('id', '').encode('utf-8')
    edate = request.form.get('edate', '').encode('utf-8')
    return site_api.site_api().setEndDate(sid, edate)


@site.route('add', methods=['POST'])
def add():
    webname = request.form.get('webinfo', '').encode('utf-8')
    ps = request.form.get('ps', '').encode('utf-8')
    path = request.form.get('path', '').encode('utf-8')
    version = request.form.get('version', '').encode('utf-8')
    port = request.form.get('port', '').encode('utf-8')
    return site_api.site_api().add(webname, port, ps, path, version)


@site.route('delete', methods=['POST'])
def delete():
    sid = request.form.get('id', '').encode('utf-8')
    webname = request.form.get('webname', '').encode('utf-8')
    return site_api.site_api().delete(sid, webname)
