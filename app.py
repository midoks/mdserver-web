# coding:utf-8

import sys
import io
import os


sys.path.append("/class/core")
reload(sys)
sys.setdefaultencoding('utf8')

import route
import config

app = config.config().makeApp(__name__)

try:
    if __name__ == "__main__":
        app.run()
except Exception as ex:
    print ex
