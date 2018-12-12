# coding:utf-8

import psutil
import time
import os
import sys


from flask import Flask, session
from flask import Blueprint, render_template
from flask import jsonify
from flask import request
from flask import make_response
from flask import Response

sys.path.append(os.getcwd() + "/class/core/")
import public

dashboard = Blueprint('dashboard', __name__, template_folder='templates')


from functools import wraps


def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        print 'test!!!'
        return 'test!!!' + func(*args, **kwargs)
    return wrapper


@dashboard.route("/test")
@login_required
def test():
    os = public.getOs()
    print os

    print(sys.platform)
    return public.getLocalIp()


@dashboard.route("/")
def index():
    # if session.has_key('code'):
    #     print session['code']
    return render_template('default/index.html')


@dashboard.route("/code")
def code():
    import vilidate
    vie = vilidate.vieCode()
    codeImage = vie.GetCodeImage(80, 4)
    try:
        from cStringIO import StringIO
    except:
        from StringIO import StringIO

    out = StringIO()
    codeImage[0].save(out, "png")

    session['code'] = public.md5("".join(codeImage[1]).lower())

    img = Response(out.getvalue(), headers={'Content-Type': 'image/png'})
    ret = make_response(img)
    return ret


@dashboard.route("/check_login", methods=['POST'])
def checkLogin():
    return "true"


@dashboard.route("/login")
def login():
    return render_template('default/login.html')


@dashboard.route("/do_login", methods=['POST'])
def doLogin():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    code = request.form.get('code', '').strip()
    print session
    if session.has_key('code'):
        if session['code'] != public.md5(code):
            return public.returnJson(False, '验证码错误,请重新输入!')

    userInfo = public.M('users').where(
        "id=?", (1,)).field('id,username,password').find()

    password = public.md5(password)
    if userInfo['username'] != username or userInfo['password'] != password:
        public.writeLog('TYPE_LOGIN', public.getInfo(
            "< a style='color: red'>密码错误</a>,帐号:{1},密码:{2},登录IP:{3}", (('****', '******', request.remote_addr))))
        return public.returnJson(False, public.getInfo("用户名或密码错误,您还可以尝试[{1}]次!", ('1')))

    return public.returnJson(True, '登录成功,正在跳转...')
