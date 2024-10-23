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

blueprint = Blueprint('site', __name__, url_prefix='/site', template_folder='../../templates/default')
@blueprint.route('/index', endpoint='index')
def index():
    return render_template('site.html', data={})

# 插件列表
@blueprint.route('/list', endpoint='list', methods=['GET','POST'])
def list():
    pg = MwPlugin.instance()
    # print(pg.getList())
    return pg.getList()

@blueprint.route('/get_site_types', endpoint='get_site_types',methods=['POST'])
def get_site_types():
    return []