# coding:utf-8

import sys
import io
import os

sys.path.append("/class/core")
import config

app = config.config().makeApp(__name__)

try:
    if __name__ == "__main__":
        app.run()
except Exception as ex:
    print ex
