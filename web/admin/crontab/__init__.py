# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------


from flask import Blueprint, render_template

blueprint = Blueprint('crontab', __name__, url_prefix='/crontab', template_folder='../../templates/default')
@blueprint.route('/index', endpoint='index')
def index():
    return render_template('crontab.html', data={})

# 插件列表
@blueprint.route('/list', endpoint='list', methods=['GET','POST'])
def list():
    return []