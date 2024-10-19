# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------


from flask import Blueprint, render_template

blueprint = Blueprint('control', __name__, url_prefix='/control', template_folder='../../templates/default')
@blueprint.route('/index', endpoint='index')
def index():
    return render_template('control.html', data={})