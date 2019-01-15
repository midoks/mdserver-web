# coding: utf-8

import os
import sys
import time
import string
import json
import hashlib
import shlex
import datetime
import subprocess
import re
import hashlib
from random import Random

import public
import db


def init():
    initDB()
    initInitD()
    initUserInfo()


def initDB():
    try:
        sql = db.Sql().dbfile('default')
        csql = public.readFile('data/sql/default.sql')
        csql_list = csql.split(';')
        for index in range(len(csql_list)):
            sql.execute(csql_list[index], ())

    except Exception, ex:
        print str(ex)


def initInitD():
    script = public.getRunDir() + '/scripts/init.d/mw.tpl'
    script_bin = public.getRunDir() + '/scripts/init.d/mw'
    if os.path.exists(script_bin):
        return

    content = public.readFile(script)
    content = content.replace("{$SERVER_PATH}", public.getRunDir())

    public.writeFile(script_bin, content)
    public.execShell('chmod +x ' + script_bin)

    if public.getOs() != 'darwin':
        initd_bin = '/etc/init.d/mw'
        if not os.path.exists(initd_bin):
            shutil.copyfile(script_bin, initd_bin)
            public.execShell('chmod +x ' + initd_bin)


def initUserInfo():
    data = public.M('users').where('id=?', (1,)).getField('password')
    if data == '21232f297a57a5a743894a0e4a801fc3':
        pwd = public.getRandomString(8).lower()
        file_pw = public.getRunDir() + '/data/default.pl'
        public.writeFile(file_pw, pwd)
        public.M('users').where('id=?', (1,)).setField(
            'password', public.md5(pwd))
