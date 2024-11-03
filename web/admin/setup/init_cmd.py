# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os
import shutil

import core.mw as mw

def contentReplace(src, dst):
    content = mw.readFile(src)
    content = content.replace("{$SERVER_PATH}", mw.getFatherDir())

    content += "\n# make:{0}".format(mw.formatDate())
    mw.writeFile(dst, content)


def init_cmd():
    script = mw.getPanelDir() + '/scripts/init.d/mw.tpl'
    script_bin = mw.getPanelDir() + '/scripts/init.d/mw'
    contentReplace(script, script_bin)
    mw.execShell('chmod +x ' + script_bin)

    # 在linux系统中,确保/etc/init.d存在
    if not mw.isAppleSystem() and not os.path.exists("/etc/rc.d/init.d"):
        mw.execShell('mkdir -p /etc/rc.d/init.d')

    if not mw.isAppleSystem() and not os.path.exists("/etc/init.d"):
        mw.execShell('mkdir -p /etc/init.d')

    # initd
    if os.path.exists('/etc/rc.d/init.d'):
        initd_bin = '/etc/rc.d/init.d/mw'
        shutil.copyfile(script_bin, initd_bin)
        mw.execShell('chmod +x ' + initd_bin)


        # 加入自启动
        mw.execShell('which chkconfig && chkconfig --add mw')

    if os.path.exists('/etc/init.d'):
        initd_bin = '/etc/init.d/mw'
        shutil.copyfile(script_bin, initd_bin)
        mw.execShell('chmod +x ' + initd_bin)
        # 加入自启动
        mw.execShell('which update-rc.d && update-rc.d -f mw defaults')
    return True