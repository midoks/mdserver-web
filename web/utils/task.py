# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os
import pwd
import time

import core.mw as mw
import thisdb

def getTaskPage(page=1,size=10):
    info = thisdb.getTaskPage(page=page, size=size)

    rdata = {}
    rdata['data'] = info['list']
    rdata['count'] = info['count']
    rdata['page'] = mw.getPage({'count':info['count'],'tojs':'remind','p':page,'row':size})
    return rdata

# 删除进程下的所有进程
def removeTaskRecursion(pid):
    cmd = "ps -ef|grep %s | grep -v grep |sed -n '2,1p' | awk '{print $2}'" % pid
    sub_pid = mw.execShell(cmd)
    if sub_pid[0].strip() == '':
        return 'ok'

    if sub_pid[0].strip() == pid :
        return 'ok'

    removeTaskRecursion(sub_pid[0].strip())
    mw.execShell('kill -9 ' + sub_pid[0].strip())
    return sub_pid[0].strip()

# 删除任务
def removeTask(task_id):
    try:
        name = mw.M('tasks').where('id=?', (task_id,)).getField('name')
        status = mw.M('tasks').where('id=?', (task_id,)).getField('status')
        mw.M('tasks').delete(task_id)
        if str(status) == '-1':
            cmd = "ps aux | grep 'panel_task.py' | grep -v grep |awk '{print $2}'"
            task_pid = mw.execShell(cmd)
            task_list = task_pid[0].strip().split("\n")
            for i in range(len(task_list)):
                removeTaskRecursion(task_list[i])
                t = mw.execShell('kill -9 ' + task_list[i])
                print(t)
            mw.triggerTask()
            mw.restartTask()
    except Exception as e:
        mw.restartTask()

    # 删除日志
    task_log = mw.getPanelDir() + "/tmp/panelTask.pl"
    if os.path.exists(task_log):
        os.remove(task_log)
    return mw.returnData(True, '任务已删除!')