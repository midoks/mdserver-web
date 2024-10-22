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

from utils.mwplugin import MwPlugin

import core.mw as mw

blueprint = Blueprint('plugins', __name__, url_prefix='/plugins', template_folder='../../templates/default')
@blueprint.route('/index', endpoint='index')
def index():
    return render_template('plugins.html', data={})

# 初始化检查,首页提示选择安装
@blueprint.route('/init', endpoint='init', methods=['POST'])
def init():
    plugin_names = {
        'openresty': '1.25.3',
        'php': '56',
        'swap': '1.1',
        'mysql': '5.7',
        'phpmyadmin': '4.4.15',
    }
    return []

# 插件列表
@blueprint.route('/list', endpoint='list', methods=['GET'])
def list():
    plugins_type = request.args.get('type', '0')
    page = request.args.get('p', '1')
    search = request.args.get('search', '').lower()

    if not mw.isNumber(plugins_type):
        plugins_type = 1

    if not mw.isNumber(page):
        page = 0

    pg = MwPlugin.instance()

    # pg.getList(plugins_type, search, int(page))
    return pg.getList(plugins_type, search, int(page))

# 图片文件读取
@blueprint.route('/file', endpoint='file', methods=['GET'])
def file():
    name = request.args.get('name', '')
    if name.strip() == '':
        return ''

    f = request.args.get('f', '')
    if f.strip() == '':
        return ''

    file = mw.getPluginDir() + '/' + name + '/' + f
    if not os.path.exists(file):
        return ''

    suffix = mw.getPathSuffix(file)
    if suffix == '.css':
        content = mw.readFile(file)
        from flask import Response
        from flask import make_response
        v = Response(content, headers={'Content-Type': 'text/css; charset="utf-8"'})
        return make_response(v)
    content = open(file, 'rb').read()
    return content


