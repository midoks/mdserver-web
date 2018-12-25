# coding:utf-8

import sys
import io
import os
import time
import shutil
import uuid

from datetime import timedelta

from flask import Flask
from flask import render_template
from flask import make_response
from flask import Response
from flask import session
from flask import request
from flask import redirect
from flask import url_for

from flask_session import Session

sys.path.append(os.getcwd() + "/class/core")
import db
import public


app = Flask(__name__, template_folder='templates/default')
app.config.version = '0.0.1'
# app.config['SECRET_KEY'] = os.urandom(24)
app.config['SECRET_KEY'] = uuid.UUID(int=uuid.getnode()).hex[-12:]
# app.secret_key = uuid.UUID(int=uuid.getnode()).hex[-12:]
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
try:
    from flask_sqlalchemy import SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/py_mw_session.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    sdb = SQLAlchemy(app)
    app.config['SESSION_TYPE'] = 'sqlalchemy'
    app.config['SESSION_SQLALCHEMY'] = sdb
    app.config['SESSION_SQLALCHEMY_TABLE'] = 'session'
except:
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = '/tmp/py_mw_session_' + \
        str(sys.version_info[0])
    app.config['SESSION_FILE_THRESHOLD'] = 1024
    app.config['SESSION_FILE_MODE'] = 384

app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'MW_:'
app.config['SESSION_COOKIE_NAME'] = "MW_VER_1"
Session(app)


def initDB():
    try:
        sql = db.Sql().dbfile('default')
        csql = public.readFile('data/sql/default.sql')
        csql_list = csql.split(';')
        for index in range(len(csql_list)):
            sql.execute(csql_list[index], ())
    except Exception, ex:
        print str(ex)

initDB()


def funConvert(fun):
    block = fun.split('_')
    func = block[0]
    for x in range(len(block) - 1):
        suf = block[x + 1].title()
        func += suf
    return func


def isLogined():
    if 'login' in session and 'username' in session:
        return True
    return False


def publicObject(toObject, func, action=None, get=None):
    name = funConvert(func) + 'Api'
    if hasattr(toObject, name):
        efunc = 'toObject.' + name + '()'
        data = eval(efunc)
        return data
    return public.retFail('访问异常!')


@app.route("/test")
def test():
    print session
    os = public.getOs()
    print os

    print(sys.platform)
    return public.getLocalIp()


@app.route("/code")
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

    session['code'] = public.md5(''.join(codeImage[1]).lower())

    img = Response(out.getvalue(), headers={'Content-Type': 'image/png'})
    return make_response(img)


@app.route("/check_login", methods=['POST'])
def checkLogin():
    return "true"


@app.route("/login")
def login():
    if isLogined():
        return redirect('/')
    return render_template('login.html')


@app.route("/do_login", methods=['POST'])
def doLogin():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    code = request.form.get('code', '').strip()
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

    session['login'] = True
    session['username'] = userInfo['username']
    return public.returnJson(True, '登录成功,正在跳转...')


@app.route('/<reqClass>/<reqAction>', methods=['POST', 'GET'])
@app.route('/<reqClass>/', methods=['POST', 'GET'])
@app.route('/<reqClass>', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def index(reqClass=None, reqAction=None, reqData=None):

    if (reqClass == None):
        reqClass = 'index'
    classFile = ('config', 'control', 'crontab', 'files', 'firewall',
                 'index', 'plugins', 'login', 'system', 'site', 'task', 'soft')
    if not reqClass in classFile:
        return '403 no access!'

    if reqAction == None:
        if not isLogined():
            return redirect('/login')
        return render_template(reqClass + '.html')

    className = reqClass + '_api'

    eval_str = "__import__('" + className + "')." + className + '()'
    newInstance = eval(eval_str)
    return publicObject(newInstance, reqAction)
