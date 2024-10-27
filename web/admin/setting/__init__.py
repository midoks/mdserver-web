# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------


from flask import Blueprint, render_template
from flask import request

from admin import model
import core.mw as mw

# 默认页面
blueprint = Blueprint('setting', __name__, url_prefix='/setting', template_folder='../../templates')
@blueprint.route('/index', endpoint='index')
def index():
    return render_template('default/setting.html')



@blueprint.route('/get_panel_list', endpoint='get_panel_list', methods=['POST'])
def get_panel_list():
    return []


# 设置面板名称
@blueprint.route('/set_webname', endpoint='set_webname', methods=['POST'])
def set_webname():
    webname = request.form.get('webname', '')
    src_webname = model.getOption('title')
    if webname != src_webname:
        model.setOption('title', webname)
    return mw.returnData(True, '面板别名保存成功!')

@blueprint.route('/set_ip', endpoint='set_ip', methods=['POST'])
def set_ip():
    host_ip = request.form.get('host_ip', '')
    src_host_ip = model.getOption('server_ip')
    if host_ip != src_host_ip:
        model.setOption('server_ip', host_ip)
    return mw.returnJson(True, 'IP保存成功!')

 