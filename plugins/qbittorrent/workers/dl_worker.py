#!/usr/bin/env python
# encoding: utf-8
"""
磁力搜索meta信息入库程序
"""

import hashlib
import os
import SimpleXMLRPCServer
import time
import datetime
import traceback
import sys
import json
import socket
import threading
from hashlib import sha1
from random import randint
from struct import unpack
from socket import inet_ntoa
from threading import Timer, Thread
from time import sleep
from collections import deque
from Queue import Queue

reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append('/usr/local/lib/python2.7/site-packages')

# import pygeoip
import MySQLdb as mdb


# from configparser import ConfigParser
# cp = ConfigParser()
# cp.read("../db.cfg")
# section_db = cp.sections()[0]
# DB_HOST = cp.get(section_db, "DB_HOST")
# DB_USER = cp.get(section_db, "DB_USER")
# DB_PORT = cp.getint(section_db, "DB_PORT")
# DB_PASS = cp.get(section_db, "DB_PASS")
# DB_NAME = cp.get(section_db, "DB_NAME")


def checkDL():
    while True:
        print time.time()
        time.sleep(1)
        checkDL()

if __name__ == "__main__":

    # import threading
    # t = threading.Thread(target=checkDL)
    # t.setDaemon(True)
    # t.start()

    checkDL()
