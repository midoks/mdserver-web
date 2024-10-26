# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------


from flask import Blueprint, render_template
from flask import request,g

import core.mw as mw

blueprint = Blueprint('dashboard', __name__, url_prefix='/', template_folder='../../templates')
@blueprint.route('/')
def index():
    return render_template('default/index.html')


# ---------------------------------------------------------------------------------
# 定义登录入口相关方法
# ---------------------------------------------------------------------------------

@blueprint.route('/login')
def login():
    return render_template('default/login.html')

# 检查是否登录
@blueprint.route('/check_login',methods=['GET','POST'])
def check_login():
    return "0"

# 执行登录操作
@blueprint.route('/do_login', endpoint='do_login', methods=['POST'])
def do_login():

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    code = request.form.get('code', '').strip()

    print(g)
    print(username, password, code  )

    return mw.returnData(False, '面板已经关闭!')
