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

socketio = SocketIO(manage_session=False, async_mode='threading',
                    logger=False, engineio_logger=False, debug=False,
                    ping_interval=25, ping_timeout=120)

class MwAdmin(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
	

    def find_submodules(self, basemodule):
        print(basemodule)

    @property
    def submodules(self):
        for blueprint in self.blueprints.values():
            if isinstance(blueprint, PgAdminModule):
                yield blueprint


def _find_blueprint():
    if request.blueprint:
        return current_app.blueprints[request.blueprint]


current_blueprint = LocalProxy(_find_blueprint)
print("current_blueprint",current_blueprint)

def create_app(app_name = None):
    import config
    if not app_name:
        app_name = config.APP_NAME

    # Check if app is created for CLI operations or Web
    cli_mode = False
    if app_name.endswith('-cli'):
        cli_mode = True

    app = MwAdmin(__name__, template_folder='templates/default')
    socketio.init_app(app, cors_allowed_origins="*")

    # Log the startup
    app.logger.info('########################################################')
    app.logger.info('Starting %s v%s...', config.APP_NAME, config.APP_VERSION)
    app.logger.info('########################################################')
    app.logger.debug("Python syspath: %s", sys.path)

    return app