# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import io
import time

from flask import Blueprint, render_template
from flask import make_response
from flask import redirect
from flask import Response
from flask import request,g

from admin.common import isLogined
from admin.user_login_check import panel_login_required
from admin import cache,session
from admin.model import db,TempLogin,Users

import core.mw as mw
import thisdb


blueprint = Blueprint('dashboard', __name__, url_prefix='/', template_folder='../../templates')
@blueprint.route('/')
@panel_login_required
def index():
    return render_template('default/index.html')

# 安全路径
@blueprint.route('/<path>',endpoint='admin_safe_path',methods=['GET'])
def admin_safe_path(path):
    db_path = thisdb.getOption('admin_path')
    if isLogined():
       return redirect('/')

    print(db_path,path)
    if db_path == path:
        return render_template('default/login.html')

    unauthorized_status = thisdb.getOption('unauthorized_status')
    if unauthorized_status == '0':
        return render_template('default/path.html')
    return Response(status=int(unauthorized_status))

# 仅针对webhook插件
@blueprint.route("/hook", methods=['POST', 'GET'])
def webhook():
    # 兼容获取关键数据
    access_key = request.args.get('access_key', '').strip()
    if access_key == '':
        access_key = request.form.get('access_key', '').strip()

    params = request.args.get('params', '').strip()
    if params == '':
        params = request.form.get('params', '').strip()

    input_args = {
        'access_key': access_key,
        'params': params,
    }

    wh_install_path = mw.getServerDir() + '/webhook'
    if not os.path.exists(wh_install_path):
        return mw.returnData(False, '请先安装WebHook插件!')

    package = mw.getPanelDir() + "/plugins/webhook"
    if not package in sys.path:
        sys.path.append(package)
        
    try:
        import webhook_index
        return webhook_index.runShellArgs(input_args)
    except Exception as e:
        return str(e)
