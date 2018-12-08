# coding: utf-8

import time
import random
import os
import urllib
import binascii
import json
import re
import sys

sys.path.append(os.getcwd() + "/class/core")
import public


def getPluginName():
    return 'csvn'


def getPluginDir():
    return public.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return public.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def status():
    return 'start'

if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print status()
    else:
        print 'error'
