# coding:utf-8

import sys
import io
import os
import time
import shutil
import uuid

reload(sys)
sys.setdefaultencoding('utf-8')


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
sys.path.append("/usr/local/lib/python2.7/site-packages")
import db
import public
import config_api

app = Flask(__name__, template_folder='templates/default')
app.config.version = config_api.config_api().getVersion()
# app.config['SECRET_KEY'] = os.urandom(24)
# app.secret_key = uuid.UUID(int=uuid.getnode()).hex[-12:]
app.config['SECRET_KEY'] = uuid.UUID(int=uuid.getnode()).hex[-12:]
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)


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

# socketio
from flask_socketio import SocketIO, emit, send
socketio = SocketIO()
socketio.init_app(app)


# debug macosx dev
if public.isAppleSystem():
    app.debug = True
    app.config.version = app.config.version + str(time.time())


import common
common.init()


def funConvert(fun):
    block = fun.split('_')
    func = block[0]
    for x in range(len(block) - 1):
        suf = block[x + 1].title()
        func += suf
    return func


def isLogined():
    if 'login' in session and 'username' in session and session['login'] == True:
        return True
    return False


def publicObject(toObject, func, action=None, get=None):
    name = funConvert(func) + 'Api'
    try:
        if hasattr(toObject, name):
            efunc = 'toObject.' + name + '()'
            data = eval(efunc)
            return data
    except Exception as e:
        data = {'msg': '访问异常:' + str(e) + '!', "status": False}
        return public.getJson(data)


@app.route("/test")
def test():
    print sys.version_info
    print session
    os = public.getOs()
    print os
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
    if isLogined():
        return "true"
    return "false"


@app.route("/login")
def login():
    print session
    dologin = request.args.get('dologin', '')
    if dologin == 'True':
        session.clear()
        return redirect('/login')

    if isLogined():
        return redirect('/')
    return render_template('login.html')


@app.route("/do_login", methods=['POST'])
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
                 'index', 'plugins', 'login', 'system', 'site', 'ssl', 'task', 'soft')
    if not reqClass in classFile:
        return redirect('/')

    if reqAction == None:
        if not isLogined():
            return redirect('/login')

        # if reqClass == 'config':
        import config_api
        data = config_api.config_api().get()
        return render_template(reqClass + '.html', data=data)
        # else:
        #     return render_template(reqClass + '.html')

    className = reqClass + '_api'

    eval_str = "__import__('" + className + "')." + className + '()'
    newInstance = eval(eval_str)
    return publicObject(newInstance, reqAction)

ssh = None
shell = None
try:
    import paramiko
    ssh = paramiko.SSHClient()
except:
    public.execShell('pip install paramiko==2.0.2 &')


def create_rsa():
    public.execShell("rm -f /root/.ssh/*")
    public.execShell('ssh-keygen -q -t rsa -P "" -f /root/.ssh/id_rsa')
    public.execShell('cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys')
    public.execShell('chmod 600 /root/.ssh/authorized_keys')


def connect_ssh():
    global shell, ssh
    if not os.path.exists('/root/.ssh/authorized_keys') or not os.path.exists('/root/.ssh/id_rsa') or not os.path.exists('/root/.ssh/id_rsa.pub'):
        create_rsa()

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect('127.0.0.1', public.getSSHPort())
    except Exception as e:
        if public.getSSHStatus():
            try:
                ssh.connect('localhost', public.getSSHPort())
            except:
                return False
        ssh.connect('127.0.0.1', public.getSSHPort())
    shell = ssh.invoke_shell(term='xterm', width=83, height=21)
    shell.setblocking(0)
    return True


# 取数据对象
def get_input_data(data):
    pdata = common.dict_obj()
    for key in data.keys():
        pdata[key] = str(data[key])
    return pdata


@socketio.on('webssh')
def webssh(msg):
    print 'webssh', msg
    if not isLogined():
        emit('server_response', {'data': '会话丢失，请重新登陆面板!\r\n'})
        return None
    global shell, ssh
    ssh_success = True
    if not shell:
        ssh_success = connect_ssh()
    if not shell:
        emit('server_response', {'data': '连接SSH服务失败!\r\n'})
        return
    if shell.exit_status_ready():
        ssh_success = connect_ssh()
    if not ssh_success:
        emit('server_response', {'data': '连接SSH服务失败!\r\n'})
        return
    shell.send(msg)
    try:
        time.sleep(0.005)
        recv = shell.recv(4096)
        emit('server_response', {'data': recv.decode("utf-8")})
    except Exception as ex:
        print 'webssh:' + str(ex)


@socketio.on('connect_event')
def connected_msg(msg):
    if not isLogined():
        emit(pdata.s_response, {'data': '会话丢失，请重新登陆面板!\r\n'})
        return None
    global shell, ssh
    try:
        recv = shell.recv(8192)
        print recv.decode("utf-8")
        emit('server_response', {'data': recv.decode("utf-8")})
    except Exception as e:
        print 'connected_msg:' + str(e)


@socketio.on('panel')
def websocket_test(data):
    pdata = get_input_data(data)
    if not isLogined():
        emit(pdata.s_response, {
             'data': public.returnData(-1, '会话丢失，请重新登陆面板!\r\n')})
        return None
    mods = ['site', 'ftp', 'database', 'ajax', 'system', 'crontab', 'files',
            'config', 'panel_data', 'plugin', 'ssl', 'auth', 'firewall', 'panel_wxapp']
    if not pdata['s_module'] in mods:
        result = '指定模块不存在!'
    else:
        result = eval("%s(pdata)" % pdata['s_module'])
    if not hasattr(pdata, 's_response'):
        pdata.s_response = 'response'
    emit(pdata.s_response, {'data': result})
