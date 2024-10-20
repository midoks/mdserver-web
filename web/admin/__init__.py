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
from flask import render_template_string

import core.mw as mw
import setting

socketio = SocketIO(manage_session=False, async_mode='threading',
                    logger=False, engineio_logger=False, debug=False,
                    ping_interval=25, ping_timeout=120)


app = Flask(__name__, template_folder='templates/default')
socketio.init_app(app, cors_allowed_origins="*")

from whitenoise import WhiteNoise
app.wsgi_app = WhiteNoise(app.wsgi_app, root="../web/static/", prefix="static/", max_age=604800)



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp/example.db'  # 使用 SQLite 数据库
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



# print(mw.getRunDir())


# 加载模块
from .submodules import get_submodules
for module in get_submodules():
    app.logger.info('Registering blueprint module: %s' % module)
    if app.blueprints.get(module.name) is None:
        app.register_blueprint(module)


@app.after_request
def requestAfter(response):
    response.headers['soft'] = setting.APP_NAME
    response.headers['mw-version'] = setting.APP_VERSION
    return response


@app.errorhandler(404)
def page_unauthorized(error):
    return render_template_string('404 not found', error_info=error), 404


# 设置模板全局变量
@app.context_processor
def inject_global_variables():
    config = {
        'version': setting.APP_VERSION
    }
    return dict(config=config)


# from flasgger import Swagger
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