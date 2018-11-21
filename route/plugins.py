# coding:utf-8

from flask import Blueprint, render_template
from flask import jsonify
from flask import request

import psutil
import time
import sys
import os
import json

sys.path.append("class/core")
import public
import plugin


plugins = Blueprint('plugins', __name__, template_folder='templates')
__plugin_name = "plugins"
__row_num = 3


@plugins.route("/file", methods=['GET'])
def file():
    name = request.args.get('name', '')
    if name.strip() == '':
        return ''

    f = request.args.get('f', '')
    if f.strip() == '':
        return ''

    file = "plugins/" + name + "/" + f
    if not os.path.exists(file):
        return ""

    c = public.readFile(file)
    return c


@plugins.route("/list", methods=['GET', 'POST'])
def list():
    typeVal = request.args.get('type', '0')
    data = plugin.plugin().getPluginList(typeVal, 1)
    return public.getJson(data)


@plugins.route('/install', methods=['POST'])
def install():

    rundir = public.getRunDir()
    name = request.form.get('name', '')
    version = request.form.get('version', '')
    stype = request.form.get('type', '0')

    mmsg = '安装'
    if hasattr(request.form, 'upgrade'):
        mtype = 'update'
        mmsg = 'upgrade'

    if name.strip() == '':
        return public.returnJson(False, "缺少插件名称!", ())

    if version.strip() == '':
        return public.returnJson(False, "缺少版本信息!", ())

    infoJsonPos = __plugin_name + '/' + name + '/' + 'info.json'

    if not os.path.exists(infoJsonPos):
        return public.retJson(False, "配置文件不存在!", ())

    pluginInfo = json.loads(public.readFile(infoJsonPos))

    execstr = "cd " + os.getcwd() + "/plugins/" + \
        name + " && /bin/bash " + pluginInfo["shell"] \
        + " install " + version + ' ' + stype

    taskAdd = (None, mmsg + '[' + name + '-' + version + ']',
               'execshell', '0', time.strftime('%Y-%m-%d %H:%M:%S'), execstr)

    public.M('tasks').add('id,name,type,status,addtime, execstr', taskAdd)
    return public.returnJson(True, '已将安装任务添加到队列!')


@plugins.route('/uninstall', methods=['POST'])
def uninstall():
    pass


@plugins.route('/installed', methods=['POST'])
def installed():

    rundir = public.getRunDir()
    name = request.form.get('name', '')

    if name.strip() == '':
        return public.retJson(-1, "缺少插件名称!", ())

    infoJsonPos = __plugin_name + '/' + name + '/' + 'info.json'
    if not os.path.exists(infoJsonPos):
        return public.returnJson(-1, "配置文件不存在!", ())

    pluginInfo = json.loads(public.readFile(infoJsonPos))

    sh = __plugin_name + '/' + name + '/' + pluginInfo['shell']
    os.system('/bin/bash ' + sh + ' install')
    print request.args
    return ''


@plugins.route('/check_installed', methods=['POST'])
def checkInstalled():
    checks = ['nginx', 'apache', 'php', 'mysql']
    for name in checks:
        filename = public.getRootDir() + "/server/" + name
        if os.path.exists(filename):
            return "True"
    return "False"
