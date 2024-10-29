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
import time
import uuid
import logging
from datetime import timedelta

from flask import Flask
from flask_socketio import SocketIO, emit, send
from flask import Flask, abort, request, current_app, session, url_for
from flask import Blueprint, render_template
from flask import render_template_string

from flask_migrate import Migrate
from flask_caching import Cache
from werkzeug.local import LocalProxy

from admin import model
from admin import setup

from admin.model import db as sys_db


import core.mw as mw
import config
import utils.config as utils_config

root_dir = mw.getRunDir()

socketio = SocketIO(manage_session=False, async_mode='threading',
                    logger=False, engineio_logger=False, debug=False,
                    ping_interval=25, ping_timeout=120)


app = Flask(__name__, template_folder='templates/default')

# app.debug = True

# 静态文件配置
from whitenoise import WhiteNoise
app.wsgi_app = WhiteNoise(app.wsgi_app, root="../web/static/", prefix="static/", max_age=604800)

# session配置
app.secret_key = uuid.UUID(int=uuid.getnode()).hex[-12:]
# app.config['sessions'] = dict()
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'MW_:'
app.config['SESSION_COOKIE_NAME'] = "MW_VER_1"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)

# db的配置
app.config['SQLALCHEMY_DATABASE_URI'] = mw.getSqitePrefix()+config.SQLITE_PATH+"?timeout=20"  # 使用 SQLite 数据库
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# 缓存配置
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app, config={'CACHE_TYPE': 'simple'})

# 初始化db
sys_db.init_app(app)
Migrate(app, sys_db)

# 检查数据库是否存在。如果没有就创建它。
setup_db_required = False
if not os.path.isfile(config.SQLITE_PATH):
    setup_db_required = True

# with app.app_context():
#     sys_db.create_all()

with app.app_context():
    if setup_db_required:
        sys_db.create_all()

# 初始化用户信息
with app.app_context():
    if setup_db_required:
        setup.init_admin_user()
        setup.init_option()



# 加载模块
from .submodules import get_submodules
for module in get_submodules():
    app.logger.info('Registering blueprint module: %s' % module)
    if app.blueprints.get(module.name) is None:
        app.register_blueprint(module)


@app.before_request
def requestCheck():
    # print("hh")
    pass

@app.after_request
def requestAfter(response):
    response.headers['soft'] = config.APP_NAME
    response.headers['mw-version'] = config.APP_VERSION
    return response


@app.errorhandler(404)
def page_unauthorized(error):
    return render_template_string('404 not found', error_info=error), 404


# 设置模板全局变量
@app.context_processor
def inject_global_variables():
    ver = config.APP_VERSION;
    if mw.isDebugMode():
        ver = ver + str(time.time())

    data = utils_config.getGlobalVar()
    g_config = {
        'version': ver,
        'title' : 'MW面板',
        'ip' : '127.0.0.1'
    }
    return dict(config=g_config, data=data)


# from flasgger import Swagger
# api = Api(app, version='1.0', title='API', description='API 文档')
# Swagger(app)

# @app.route('/colors/<palette>/')
# def colors(palette):
#     """
#     根据调色板名称返回颜色列表
#     ---
#     parameters:
#       - name: palette
#         in: path
#         type: string
#         enum: ['all', 'rgb', 'cmyk']
#         required: true
#         default: all
#     definitions:
#       Palette:
#         type: object
#         properties:
#           palette_name:
#             type: array
#             items:
#               $ref: '#/definitions/Color'
#       Color:
#         type: string
#     responses:
#       200:
#         description: 返回的颜色列表，可按调色板过滤
#         schema:
#           $ref: '#/definitions/Palette'
#         examples:
#           rgb: ['red', 'green', 'blue']
#     """
#     all_colors = {
#         'cmyk': ['cyan', 'magenta', 'yellow', 'black'],
#         'rgb': ['red', 'green', 'blue']
#     }
#     if palette == 'all':
#         result = all_colorselse
#         result = {palette: all_colors.get(palette)}
#     return jsonify(result)




# Log the startup
app.logger.info('########################################################')
app.logger.info('Starting %s v%s...', config.APP_NAME, config.APP_VERSION)
app.logger.info('########################################################')
app.logger.debug("Python syspath: %s", sys.path)



# OK
socketio.init_app(app, cors_allowed_origins="*")

# def create_app(app_name = None):
#     
#     if not app_name:
#         app_name = config.APP_NAME

#     # Check if app is created for CLI operations or Web
#     cli_mode = False
#     if app_name.endswith('-cli'):
#         cli_mode = True
#     return app