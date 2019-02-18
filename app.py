# coding:utf-8

import sys
import io
import os
from route import app, socketio

try:
    if __name__ == "__main__":
        PORT = 7200
        HOST = '0.0.0.0'
        socketio.run(app, host=HOST, port=PORT)
except Exception as ex:
    print ex
