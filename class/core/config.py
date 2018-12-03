# coding:utf-8

import sys
import io
import os
import time

from flask import Flask
from datetime import timedelta


class config:
    __version = '0.0.1'
    __app = None

    def __init__(self):
        pass

    def makeApp(self, name):
        app = Flask(name)
        app.debug = True

        app.config.version = self.__version + str(time.time())
        app.config['SECRET_KEY'] = os.urandom(24)
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
        __app = app
        return app

    def getVersion(self):
        return self.__version

    def getApp(self):
        return self.__app
