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


@site.route('add', methods=['POST'])
def add():
    webname = request.form.get('webname', '').encode('utf-8')
    ps = request.form.get('ps', '').encode('utf-8')
    path = request.form.get('path', '').encode('utf-8')
    version = request.form.get('version', '').encode('utf-8')
    port = request.form.get('port', '').encode('utf-8')
    webname = request.form.get('webname', '').encode('utf-8')
    print webname
    return site_api.site_api().add(webname, ps, path, version)
