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
    return os


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
    print request.args

    # return "123"
    # return public.returnJson(False, 'LOGIN_USER_EMPTY')
    return public.returnJson(True, 'LOGIN_SUCCESS')
