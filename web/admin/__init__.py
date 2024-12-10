# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os
import sys
import json
import time
import uuid
import logging

from datetime import timedelta

from flask import Flask
from flask import request
from flask import redirect
from flask import Response
from flask import Flask, abort, current_app, session, url_for
from flask import Blueprint, render_template
from flask import render_template_string

from flask_socketio import SocketIO, emit, send

from flask_caching import Cache
from werkzeug.local import LocalProxy


from admin.common import isLogined

import core.mw as mw
import config
import utils.config as utils_config
import thisdb

# 初始化db
from admin import setup
setup.init()

app = Flask(__name__, template_folder='templates/default')

# 缓存配置
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app, config={'CACHE_TYPE': 'simple'})

# 静态文件配置
from whitenoise import WhiteNoise
app.wsgi_app = WhiteNoise(app.wsgi_app, root="../web/static/", prefix="static/", max_age=604800)
app.jinja_env.trim_blocks = True

# session配置
# app.secret_key = uuid.UUID(int=uuid.getnode()).hex[-12:]
app.config['SECRET_KEY'] = uuid.UUID(int=uuid.getnode()).hex[-12:]

# app.config['sessions'] = dict()
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'MW_:'
app.config['SESSION_COOKIE_NAME'] = "MW_VER_1"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)

# db的配置
# app.config['SQLALCHEMY_DATABASE_URI'] = mw.getSqitePrefix()+config.SQLITE_PATH+"?timeout=20"  # 使用 SQLite 数据库
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# BASIC AUTH
app.config['BASIC_AUTH_OPEN'] = False
try:
    basic_auth = thisdb.getOptionByJson('basic_auth', default={'open':False})
    if basic_auth['open']:
        app.config['BASIC_AUTH_OPEN'] = True
except Exception as e:
    pass

# 加载模块
from .submodules import get_submodules
for module in get_submodules():
    app.logger.info('Registering blueprint module: %s' % module)
    if app.blueprints.get(module.name) is None:
        app.register_blueprint(module)

def sendAuthenticated():
    # 发送http认证信息
    request_host = mw.getHostAddr()
    result = Response('', 401, {'WWW-Authenticate': 'Basic realm="%s"' % request_host.strip()})
    if not 'login' in session and not 'admin_auth' in session:
        session.clear()
    return result

@app.before_request
def requestCheck():

    admin_close = thisdb.getOption('admin_close')
    if admin_close == 'yes':
        if not request.path.startswith('/close'):
            return redirect('/close')

    config.APP_START_TIME=time.time()
    # 自定义basic auth认证
    if app.config['BASIC_AUTH_OPEN']:
        basic_auth = thisdb.getOptionByJson('basic_auth', default={'open':False})
        if not basic_auth['open']:
            return

        auth = request.authorization
        if request.path in ['/download', '/hook', '/down']:
            return
        if not auth:
            return sendAuthenticated()

        salt = basic_auth['salt']
        basic_user = mw.md5(auth.username.strip() + salt)
        basic_pwd = mw.md5(auth.password.strip() + salt)
        if basic_user != basic_auth['basic_user'] or basic_pwd != basic_auth['basic_pwd']:
            return sendAuthenticated()

    domain_check = mw.checkDomainPanel()
    if domain_check:
        return domain_check
            


@app.after_request
def requestAfter(response):
    response.headers['soft'] = config.APP_NAME
    response.headers['mw-version'] = config.APP_VERSION
    if mw.isDebugMode():
        response.headers['mw-debug-cos'] = time.time() - config.APP_START_TIME
    return response


@app.errorhandler(404)
def page_unauthorized(error):
    from flask import redirect
    return redirect('/', code=302)
    # return render_template_string('404 not found', error_info=error), 404


# 设置模板全局变量
@app.context_processor
def inject_global_variables():
    app_ver = config.APP_VERSION
    if mw.isDebugMode():
        app_ver = app_ver + str(time.time())

    data = utils_config.getGlobalVar()
    g_config = {
        'version': app_ver,
        'title' : 'MW面板',
        'ip' : '127.0.0.1'
    }
    return dict(config=g_config, data=data)

# webssh
# socketio = SocketIO(manage_session=False, async_mode='threading',
#                     logger=False, engineio_logger=False, debug=False,
#                     ping_interval=25, ping_timeout=120)
socketio = SocketIO(logger=False,
    engineio_logger=False,
    cors_allowed_origins="*")
socketio.init_app(app)

@socketio.on('webssh_websocketio')
def webssh_websocketio(data):
    if not isLogined():
        emit('server_response', {'data': '会话丢失，请重新登陆面板!\r\n'})
        return
    import utils.ssh.ssh_terminal as ssh_terminal
    shell_client = ssh_terminal.ssh_terminal.instance()
    shell_client.run(request.sid, data)
    return


@socketio.on('webssh')
def webssh(data):
    if not isLogined():
        emit('server_response', {'data': '会话丢失，请重新登陆面板!\r\n'})
        return None

    import utils.ssh.ssh_local as ssh_local
    shell = ssh_local.ssh_local.instance()
    shell.run(data)
    return


# File logging
logger = logging.getLogger('werkzeug')
logger.setLevel(config.CONSOLE_LOG_LEVEL)

from utils.enhanced_log_rotation import EnhancedRotatingFileHandler
fh = EnhancedRotatingFileHandler(config.LOG_FILE,
                                 config.LOG_ROTATION_SIZE,
                                 config.LOG_ROTATION_AGE,
                                 config.LOG_ROTATION_MAX_LOG_FILES)
fh.setLevel(config.FILE_LOG_LEVEL)
app.logger.addHandler(fh)
logger.addHandler(fh)

# Console logging
ch = logging.StreamHandler()
ch.setLevel(config.CONSOLE_LOG_LEVEL)
ch.setFormatter(logging.Formatter(config.CONSOLE_LOG_FORMAT))

# Log the startup
app.logger.info('########################################################')
app.logger.info('Starting %s v%s...', config.APP_NAME, config.APP_VERSION)
app.logger.info('########################################################')
app.logger.debug("Python syspath: %s", sys.path)