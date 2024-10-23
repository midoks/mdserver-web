# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------


from flask import Blueprint, render_template

blueprint = Blueprint('dashboard', __name__, url_prefix='/', template_folder='../../templates/default')
@blueprint.route('/')
def index():
    return render_template('index.html', data = {})


@blueprint.route('/check_login',methods=['GET','POST'])
def check_login():
    return "0"
