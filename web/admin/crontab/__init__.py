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

from admin.user_login_check import panel_login_required
from admin.model import Crontab

blueprint = Blueprint('crontab', __name__, url_prefix='/crontab', template_folder='../../templates/default')
@blueprint.route('/index', endpoint='index')
def index():
    return render_template('crontab.html')

# 插件列表
@blueprint.route('/list', endpoint='list', methods=['GET','POST'])
@panel_login_required
def list():
    page = request.args.get('p', 1)
    size = 10
    count = Crontab.query.count()
    print(count)
    clist = Crontab.query.paginate(page=int(page), per_page=size)
    print(clist)

    return []