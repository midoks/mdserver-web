# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------


from flask import Blueprint, render_template

blueprint = Blueprint('config', __name__, url_prefix='/config', template_folder='../../templates/default')
@blueprint.route('/index', endpoint='index')
def index():
    return render_template('config.html')



@blueprint.route('/get_panel_list', endpoint='get_panel_list', methods=['POST'])
def get_panel_list():
    return []