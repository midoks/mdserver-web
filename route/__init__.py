# coding:utf-8

import sys
import io
import os
import time
import shutil

from flask import Flask
from flask import render_template

sys.path.append(os.getcwd() + "/class/core")

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


@app.route('/<reqClass>/<reqAction>', methods=['POST', 'GET'])
@app.route('/<reqClass>/', methods=['POST', 'GET'])
@app.route('/<reqClass>', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def index(reqClass=None, reqAction=None, reqData=None):
    print reqClass, reqAction, reqData

    if (reqClass == None):
        reqClass = 'index'
    classFile = ('config', 'control', 'crontab',
                 'files', 'firewall', 'index', 'login', 'system', 'site', 'soft')
    if not reqClass in classFile:
        return '403 no access!'

    if reqAction == None:
        return render_template(reqClass + '.html')

    className = reqClass + '_api'
    print reqClass, reqAction, className

    eval_str = "__import__('" + className + "')" + "\n" + \
        className + '.' + className + '()'
    print eval(eval_str)

    print newClass
    newInstance = eval(newClass)
    print newInstance
    return '123'
