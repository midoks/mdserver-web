# coding: utf-8

import time
import random
import os
import json
import re
import sys

sys.path.append(os.getcwd() + "/class/core")
import public


def status():
    return 'start'


def sysConf():
    return '/etc/sysctl.conf'

if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print status()
    elif func == 'conf':
        print sysConf()
