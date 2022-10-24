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

import mw
import db

from flask import redirect


def init():
    initDB()
    initUserInfo()
    initInitD()


def local():
    result = checkClose()
    if result:
        return result


# 检查面板是否关闭
def checkClose():
    if os.path.exists('data/close.pl'):
        return redirect('/close')


def initDB():
    try:
        sql = db.Sql().dbfile('default')
        csql = mw.readFile('data/sql/default.sql')
        csql_list = csql.split(';')
        for index in range(len(csql_list)):
            sql.execute(csql_list[index], ())

    except Exception as ex:
        print(str(ex))


def doContentReplace(src, dst):
    content = mw.readFile(src)
    content = content.replace("{$SERVER_PATH}", mw.getRunDir())
    mw.writeFile(dst, content)


def initInitD():

    # systemctl
    # 有问题
    # if os.path.exists('/lib/systemd/system'):
    #     systemd_mw = '/lib/systemd/system/mw.service'
    #     systemd_mw_task = '/lib/systemd/system/mw-task.service'

    #     systemd_mw_tpl = mw.getRunDir() + '/scripts/init.d/mw.service.tpl'
    #     systemd_mw_task_tpl = mw.getRunDir() + '/scripts/init.d/mw-task.service.tpl'

    #     os.remove(systemd_mw)
    #     os.remove(systemd_mw_task)
    #     doContentReplace(systemd_mw_tpl, systemd_mw)
    #     doContentReplace(systemd_mw_task_tpl, systemd_mw_task)

    #     mw.execShell('systemctl enable mw')
    #     mw.execShell('systemctl enable mw-task')
    #     mw.execShell('systemctl daemon-reload')

    script = mw.getRunDir() + '/scripts/init.d/mw.tpl'
    script_bin = mw.getRunDir() + '/scripts/init.d/mw'
    doContentReplace(script, script_bin)
    mw.execShell('chmod +x ' + script_bin)

    # 在linux系统中,确保/etc/init.d存在
    if not mw.isAppleSystem() and not os.path.exists("/etc/init.d"):
        mw.execShell('mkdir -p /etc/init.d')

    # initd
    if os.path.exists('/etc/init.d'):
        initd_bin = '/etc/init.d/mw'
        if not os.path.exists(initd_bin):
            import shutil
            shutil.copyfile(script_bin, initd_bin)
            mw.execShell('chmod +x ' + initd_bin)
        # 加入自启动
        mw.execShell('which chkconfig && chkconfig --add mw')
        mw.execShell('which update-rc.d && update-rc.d -f mw defaults')

    # 获取系统IPV4
    mw.setHostAddr(mw.getLocalIp())


def initUserInfo():

    data = mw.M('users').where('id=?', (1,)).getField('password')
    if data == '21232f297a57a5a743894a0e4a801fc3':
        pwd = mw.getRandomString(8).lower()
        file_pw = mw.getRunDir() + '/data/default.pl'
        mw.writeFile(file_pw, pwd)
        mw.M('users').where('id=?', (1,)).setField(
            'password', mw.md5(pwd))
