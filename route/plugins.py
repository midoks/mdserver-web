# coding:utf-8

from flask import Blueprint, render_template
from flask import jsonify
from flask import request

import psutil
import time
import sys
import os
import json

sys.path.append("class/")
import public


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

    # public.M('tasks')

    data = json.loads(public.readFile("data/type.json"))
    ret = {}
    ret["type"] = data

    plugins_info = []

    typeVal = request.args.get('type', '')
    if typeVal == "":
        typeVal = "0"

    for dirinfo in os.listdir(__plugin_name):
        path = __plugin_name + "/" + dirinfo
        if os.path.isdir(path):
            jsonFile = path + "/info.json"
            if os.path.exists(jsonFile):
                try:
                    tmp = json.loads(public.readFile(jsonFile))
                    if typeVal == "0":
                        plugins_info.append(tmp)
                    else:
                        if tmp['pid'] == typeVal:
                            plugins_info.append(tmp)
                except:
                    pass

    ret['data'] = plugins_info
    ret['list'] = get_page(plugins_info, request.args)
    return jsonify(ret)


@plugins.route('/install', methods=['POST'])
def install():

    rundir = public.getRunDir()
    name = request.form.get('name', '')
    version = request.form.get('version', '')

    mmsg = '安装'
    if hasattr(request.form, 'upgrade'):
        mtype = 'update'
        mmsg = 'upgrade'

    if name.strip() == '':
        return public.returnJson(-1, "缺少name数据!", ())

    if version.strip() == '':
        return public.returnJson(-1, "缺少版本信息!", ())

    infoJsonPos = __plugin_name + '/' + name + '/' + 'info.json'

    if not os.path.exists(infoJsonPos):
        return public.retJson(-1, "info.json数据不存在!", ())

    pluginInfo = json.loads(public.readFile(infoJsonPos))

    execstr = "cd " + os.getcwd() + "/plugins/" + \
        name + " && /bin/bash " + pluginInfo["shell"] + " install" + version

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
        return public.retJson(-1, "缺少name数据!", ())

    infoJsonPos = __plugin_name + '/' + name + '/' + 'info.json'

    if not os.path.exists(infoJsonPos):
        return public.retJson(-1, "配置数据(info.json)不存在!", ())

    pluginInfo = json.loads(public.readFile(infoJsonPos))

    sh = __plugin_name + '/' + name + '/' + pluginInfo['shell']
    os.system('/bin/bash ' + sh + ' install')
    print request.args
    return ''

# 取分页


def get_page(data, args):
    # 包含分页类
    import page
    # 实例化分页类
    page = page.Page()
    info = {}
    info['count'] = len(data)
    info['row'] = __row_num
    info['p'] = 1
    if hasattr(args, 'p'):
        info['p'] = int(get['p'])
    info['uri'] = {}
    info['return_js'] = ''
    if hasattr(args, 'tojs'):
        info['return_js'] = args.tojs

    # 获取分页数据
    result = {}
    result['page'] = page.GetPage(info)
    return result
