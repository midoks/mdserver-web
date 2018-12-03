# coding: utf-8

import time
import psutil
import random
import os
import urllib
import binascii
import json
import public
import re


def status():
    return 'start'

if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print status()
