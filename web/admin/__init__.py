# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import sys

from flask import Flask
from flask_socketio import SocketIO, emit, send
from flask import Flask, abort, request, current_app, session, url_for
from werkzeug.local import LocalProxy
from flask import Blueprint, render_template

import setting

socketio = SocketIO(manage_session=False, async_mode='threading',
                    logger=False, engineio_logger=False, debug=False,
                    ping_interval=25, ping_timeout=120)


app = Flask(__name__, template_folder='templates/default')
socketio.init_app(app, cors_allowed_origins="*")

from whitenoise import WhiteNoise
app.wsgi_app = WhiteNoise(app.wsgi_app, root="../web/static/", prefix="static/", max_age=604800)

# 加载模块
from .submodules import get_submodules
for module in get_submodules():
    app.logger.info('Registering blueprint module: %s' % module)
    if app.blueprints.get(module.name) is None:
        app.register_blueprint(module)


# Log the startup
app.logger.info('########################################################')
app.logger.info('Starting %s v%s...', setting.APP_NAME, setting.APP_VERSION)
app.logger.info('########################################################')
app.logger.debug("Python syspath: %s", sys.path)


# def create_app(app_name = None):
#     
#     if not app_name:
#         app_name = config.APP_NAME

#     # Check if app is created for CLI operations or Web
#     cli_mode = False
#     if app_name.endswith('-cli'):
#         cli_mode = True
#     return app