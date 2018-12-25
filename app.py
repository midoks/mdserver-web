# coding:utf-8

import sys
import io
import os
from route import app

try:
    if __name__ == "__main__":
        app.run()
except Exception as ex:
    print ex
