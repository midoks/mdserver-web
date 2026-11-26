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
import secrets
import logging

from datetime import timedelta

from flask import Flask
from flask import request
from flask import redirect
from flask import Response
from flask import Flask, abort, current_app, session, url_for
from flask import Blueprint, render_template
from flask import render_template_string
from flask_compress import Compress

from flask_socketio import SocketIO, emit, send

from flask_caching import Cache
from werkzeug.local import LocalProxy


from admin.common import isLogined

import core.mw as mw
import config
import utils.config as utils_config
import thisdb
import utils.csrf as csrf_mw

# 初始化db
from admin import setup
setup.init()

app = Flask(__name__, template_folder='templates/default')


# curl --compressed -I "http://127.0.0.1:44010/" -H "Accept-Encoding: br" --write-out "%{json}"
# 压缩算法优先级: gzip 最快, br 压缩率最高但慢, 大数据场景速度比压缩率更重要
app.config["COMPRESS_ALGORITHM"] = ["gzip", "zstd", "br", "deflate"]
# 压缩级别 4: brotli 默认推荐档, gzip 中档, 兼顾压缩率和速度
# 之前设为 9 (最高级别), 1MB JSON 需要 500-700ms 压缩时间, 严重拖慢动态接口
app.config["COMPRESS_LEVEL"] = 4
app.config["COMPRESS_MIN_SIZE"] = 500  # 最小压缩大小
Compress(app)

# 缓存配置
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})

# 静态文件配置
app.static_folder = "../static"
app.static_url_path = "/static"
app.jinja_env.trim_blocks = True

# from whitenoise import WhiteNoise
# app.wsgi_app = WhiteNoise(app.wsgi_app, root="../web/static/", prefix="static/", max_age=604800)

# session配置
# app.secret_key = uuid.UUID(int=uuid.getnode()).hex[-12:]
secrets_token = thisdb.getOption('secret_key')
if secrets_token and secrets_token != '':
    app.config['SECRET_KEY'] = secrets_token
else:
    token_hex = secrets.token_hex(24)
    app.config['SECRET_KEY'] = token_hex
    thisdb.setOption('secret_key', token_hex)

# app.config['sessions'] = dict()
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'MW_:'
app.config['SESSION_COOKIE_NAME'] = "MW_VER_1"
# 安全 Cookie: 防 XSS 偷 session, 防 CSRF 跨站携带
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
# secure 根据面板 SSL 配置在 before_request 里动态补
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 604800

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
    request.start_time = time.time()

    # 静态文件直接放行, 不做任何 DB 查询和 CSRF 处理 (性能优化)
    # /plugins/file 是插件静态资源服务, 同样跳过
    if request.path.startswith('/static/') or request.path == '/plugins/file':
        return

    # 动态决定 session cookie 是否 secure (面板开了 SSL 就强制 secure)
    # 用 cache 缓存 5 分钟, 避免每个请求查 DB
    ssl_open = cache.get('panel_ssl_open')
    if ssl_open is None:
        try:
            panel_ssl = thisdb.getOptionByJson('panel_ssl', default={'open':False})
            ssl_open = bool(panel_ssl.get('open'))
            cache.set('panel_ssl_open', ssl_open, timeout=300)
        except Exception:
            ssl_open = False
    if ssl_open:
        app.config['SESSION_COOKIE_SECURE'] = True

    admin_close = thisdb.getOption('admin_close')
    if admin_close == 'yes':
        if not request.path.startswith('/close'):
            return redirect('/close')
    # 自定义basic auth认证
    if app.config['BASIC_AUTH_OPEN']:
        basic_auth = thisdb.getOptionByJson('basic_auth', default={'open':False})
        if not basic_auth['open']:
            return

        auth = request.authorization
        if request.path in ['/download', '/hook', '/down',
                            '/quick_login/ticket', '/quick_login/entry']:
            return
        if not auth:
            return sendAuthenticated()

        salt = basic_auth['salt']
        basic_user = mw.md5(auth.username.strip() + salt)
        basic_pwd = mw.md5(auth.password.strip() + salt)
        if basic_user != basic_auth['basic_user'] or basic_pwd != basic_auth['basic_pwd']:
            return sendAuthenticated()

    # CSRF 双提交校验 (POST/PUT/PATCH/DELETE 才校验)
    csrf_resp = csrf_mw.apply_csrf_before_request()
    if csrf_resp is not None:
        return csrf_resp

    # domain_check = mw.checkDomainPanel()
    # if domain_check:
    #     return domain_check
            


@app.after_request
def requestAfter(response):
    response.headers['soft'] = config.APP_NAME
    response.headers['mw-version'] = config.APP_VERSION
    if mw.isDebugMode():
        response.headers['X-Response-Time'] = round(time.time() - request.start_time, 4)

    # 静态文件: 只加最基本的安全头, 跳过 CSRF cookie 处理 (性能优化)
    # /plugins/file 是插件静态资源, 同样跳过
    if request.path.startswith('/static/') or request.path == '/plugins/file':
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        return response

    # 安全响应头
    response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    response.headers.setdefault('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')

    # csrf_token cookie 金融级策略:
    #   危险方法(POST/PUT/PATCH/DELETE)成功后轮换 token
    #   安全方法(GET 等)复用现有 token + 滑动续期
    #   session 里保留最近 N 个 token, 容忍并发 AJAX 的轮换竞态
    #   只在必要时设置 cookie (cookie 不存在或 token 变化时), 避免静态资源重复写
    method = (request.method or 'GET').upper()
    existing_token = request.cookies.get(csrf_mw.COOKIE_NAME)

    if method in ('POST', 'PUT', 'PATCH', 'DELETE'):
        token = csrf_mw.generate_token()  # 危险请求后轮换
        csrf_mw.push_token(token)
        csrf_mw.set_csrf_cookie(response, token)
    elif not existing_token:
        token = csrf_mw.generate_token()  # 首次请求
        csrf_mw.push_token(token)
        csrf_mw.set_csrf_cookie(response, token)
    else:
        # 安全请求且 cookie 已存在: 复用 token, 不重新设置 cookie (减少响应头)
        csrf_mw.push_token(existing_token)

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
    cors_allowed_origins="*",
    async_mode='threading')
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