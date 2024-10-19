# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------


from flask import Blueprint, render_template

blueprint = Blueprint('task', __name__, url_prefix='/task', template_folder='../../templates/default')
@blueprint.route('/count', endpoint='task_count')
def task_count():
    return "0"