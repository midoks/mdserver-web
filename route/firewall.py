# coding:utf-8

import sys
import os
import re

from flask import Flask
from flask import Blueprint, render_template
from flask import request


sys.path.append(os.getcwd() + "/class/core/")
import db
import public
import firewall_api

firewall = Blueprint('firewall', __name__, template_folder='templates')


@firewall.route('/')
def index():
    return render_template('default/firewall.html')


@firewall.route('/get_www_path', methods=['POST'])
def getWwwPath():
    path = public.getLogsDir()
    return public.getJson({'path': path})


@firewall.route("/get_list", methods=['POST'])
def getList():
    p = request.form.get('p', '1').strip()
    limit = request.form.get('limit', '10').strip()
    return firewall_api.firewall_api().getList(int(p), int(limit))


@firewall.route("/get_log_list", methods=['POST'])
def getLogList():
    p = request.form.get('p', '1').strip()
    limit = request.form.get('limit', '10').strip()
    search = request.form.get('search', '').strip()
    return firewall_api.firewall_api().getLogList(int(p), int(limit), search)


@firewall.route('get_ssh_info', methods=['POST'])
def getSshInfo():
    file = '/etc/ssh/sshd_config'
    conf = public.readFile(file)
    rep = "#*Port\s+([0-9]+)\s*\n"
    port = re.search(rep, conf).groups(0)[0]

    data = {}
    data['port'] = port
    data['status'] = True
    data['ping'] = True
    if public.getOs() == 'draim':
        data['firewall_status'] = False
    else:
        data['firewall_status'] = True
    return public.getJson(data)
