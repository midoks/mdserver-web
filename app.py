# coding:utf-8

from gevent import monkey
monkey.patch_all()

import sys
import io
import os
from route import app, socketio


from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

try:
    if __name__ == "__main__":
        f = open('data/port.pl')
        PORT = int(f.read())
        HOST = '0.0.0.0'

        http_server = WSGIServer(
            (HOST, PORT), app, handler_class=WebSocketHandler)
        http_server.serve_forever()
        socketio.run(app, host=HOST, port=PORT)
except Exception as ex:
    print(ex)
