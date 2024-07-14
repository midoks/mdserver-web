# coding:utf-8

import sys
import io
import os
import time
import re
import json
import shutil

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True

def getPluginName():
    return 'simpleping'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()

def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()

def pingData(args = ()):
    conn = mw.M('sp_ping').dbPos(getServerDir()+'/data', 'simpleping', 'db3')
    field = 'id,speed,created_unix'
    conn = conn.field(field)
    data = []
    atype = args['type']

    if not 'ip' in args:
        ip = 'all'
    else:
        ip = args['ip']
    if ip != 'all':
        conn = conn.where('ip=?',(ip,))
        
    if atype == 'pos':
        pos = args['pos']
        data = conn.where('created_unix>?',(pos,)).limit("3000").select()
    elif atype == 'range':
        start = args['start']
        end = args['end']
        data = conn.where('created_unix>=? and created_unix<=?',(start,end)).limit("1000").select()
    return data


def pingMySQLData(args = ()):
    conn = mw.M('sp_mysql_ping').dbPos(getServerDir()+'/data', 'simpleping', 'db3')
    field = 'id,value,created_unix'
    conn = conn.field(field)
    data = []
    atype = args['type']
    if atype == 'pos':
        pos = args['pos']
        data = conn.where('created_unix>?',(pos,)).limit("3000").select()
    elif atype == 'range':
        start = args['start']
        end = args['end']
        data = conn.where('created_unix>=? and created_unix<=?',(start,end)).limit("1000").select()
    return data

