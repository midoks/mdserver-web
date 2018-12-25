# coding:utf-8

import sys
import io
import os
import time
import shutil

from datetime import timedelta

from flask import Flask
from flask import render_template

sys.path.append(os.getcwd() + "/class/core")
import public

# from dashboard import *
# from site import *
# from files import *
# from soft import *
# from config import *
# from plugins import *
# from task import *
# from system import *
# from database import *
# from crontab import *
# from control import *
# from firewall import *

app = Flask(__name__, template_folder='templates/default')
app.config.version = '0.0.1'
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)


def funConvert(fun):
    block = fun.split('_')
    func = block[0]
    for x in range(len(block) - 1):
        suf = block[x + 1].title()
        func += suf
    return func


def publicObject(toObject, func, action=None, get=None):
    name = funConvert(func) + 'Api'
    if hasattr(toObject, name):
        efunc = 'toObject.' + name + '()'
        data = eval(efunc)
        return public.getJson(data)
    return public.retFail('Access Exception!')


@app.route("/check_login", methods=['POST', 'GET'])
def checkLogin():
    return "true"


@app.route('/<reqClass>/<reqAction>', methods=['POST', 'GET'])
@app.route('/<reqClass>/', methods=['POST', 'GET'])
@app.route('/<reqClass>', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def index(reqClass=None, reqAction=None, reqData=None):

    if (reqClass == None):
        reqClass = 'index'
    classFile = ('config', 'control', 'crontab',
                 'files', 'firewall', 'index', 'login', 'system', 'site', 'soft')
    if not reqClass in classFile:
        return '403 no access!'

    if reqAction == None:
        return render_template(reqClass + '.html')

    className = reqClass + '_api'

    eval_str = "__import__('" + className + "')." + className + '()'
    newInstance = eval(eval_str)
    return publicObject(newInstance, reqAction)
