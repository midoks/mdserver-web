# coding=utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

# import eventlet
# eventlet.monkey_patch()

import sys
import os

# from admin import create_app
from admin import app, socketio
import config

# from gevent.pywsgi import WSGIServer
# from geventwebsocket.handler import WebSocketHandler


if sys.version_info < (3, 6):
    raise RuntimeError('This application must be run under Python 3.6 or later.')

# 我们需要在sys.path中包含根目录，以确保我们可以找到在独立运行时运行时所需的一切。
if sys.path[0] != os.path.dirname(os.path.realpath(__file__)):
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))


# print(config.DEFAULT_SERVER,config.DEFAULT_SERVER_PORT)
# app = create_app()

def main():

    # try:
    #     # http_server = WSGIServer(
    #     #         (HOST, PORT), app, handler_class=WebSocketHandler)
    #     # http_server.serve_forever()
    #     # socketio.run(app, host=HOST, port=PORT)
    #     socketio.run(
    #         app,
    #         debug=config.DEBUG,
    #         host=config.DEFAULT_SERVER,
    #         port=7201,
    #     )
    # except Exception as e:
    #     print(str(e))

    app.run(debug=True)

if __name__ == '__main__':
    main()
