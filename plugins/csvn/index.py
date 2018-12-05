# coding: utf-8

import time
import psutil
import random
import os
import urllib
import binascii
import json
import re
import sys

sys.path.append(os.getcwd() + "/class/core")
import public


def status():
    return 'start'

if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print status()
