# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------


from flask import Blueprint, render_template

from utils.mwplugin import MwPlugin

blueprint = Blueprint('plugins', __name__, url_prefix='/plugins', template_folder='../../templates/default')
@blueprint.route('/index', endpoint='index')
def index():
    return render_template('plugins.html', data={})

# 插件列表
@blueprint.route('/list', endpoint='list', methods=['GET'])
def list():
    pg = MwPlugin.instance()
    # print(pg.getList())
    return pg.getList()

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