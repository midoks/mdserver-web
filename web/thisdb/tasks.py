# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import core.mw as mw

__FIELD = 'id,name,type,start,end,cmd,status,add_time'

def getTaskCount(status = -1) -> int:
    return mw.M('tasks').where('status=?',(1,)).count()


# 未执行任务总数
def getTaskUnexecutedCount() -> int:
    return mw.M('tasks').where('status!=?',(1,)).count()

def addTaskByDownload(name = '下载文件',cmd = None,type = 'download',status = 0):
    '''
    添加后台任务
    :name -> str 类型
    :cmd -> str 日志内容 (必填)
    :type -> str 用户ID
    '''
    if cmd is None:
        return False

    add_time = mw.formatDate()
    insert_data = {
        'name':name,
        'type':type,
        'cmd':cmd,
        'start':0,
        'end':0,
        'status':status,
        'add_time':add_time,
    }
    mw.M('tasks').insert(insert_data)
    return True

def addTask(
    name = '常用任务',
    cmd = None,
    type = 'execshell',
    status = 0,
):
    '''
    添加后台任务
    :name -> str 类型
    :cmd -> str 日志内容 (必填)
    :type -> str 用户ID
    '''
    if cmd is None:
        return False

    add_time = mw.formatDate()
    insert_data = {
        'name':name,
        'type':type,
        'cmd':cmd,
        'start':0,
        'end':0,
        'status':status,
        'add_time':add_time,
    }
    mw.M('tasks').insert(insert_data)
    return True


def getTaskList(
    status = 1,
    page = 1,
    size = 10,
):
    start = (page - 1) * size
    limit = str(start) + ',' + str(size)
    task_list = mw.M('tasks').where('status=?', (status,)).field(__FIELD).limit(limit).order('id asc').select()
    return task_list

def getTaskPage(
    status = 1,
    page = 1,
    size = 10,
):
    start = (page - 1) * size
    limit = str(start) + ',' + str(size)
    task_list = mw.M('tasks').where('', ()).field(__FIELD).limit(limit).order('id desc').select()
    count = mw.M('tasks').where('', ()).count()

    rdata = {}
    rdata['list'] = task_list
    rdata['count'] = count
    return rdata

def getTaskFirstByRun() -> None:
    data = mw.M('tasks').where('status!=?', (1,)).field(__FIELD).order('id asc').find()
    if data is None:
        return None
    return data

def getTaskRunList(page = 1,size = 10):
    start = (page - 1) * size
    limit = str(start) + ',' + str(size)
    task_list = mw.M('tasks').where('status!=?', (1,)).field(__FIELD).limit(limit).order('id asc').select()
    return task_list

def getTaskRunAll():
    task_list = mw.M('tasks').where('status!=?', (1,)).field(__FIELD).order('id asc').select()
    return task_list

def getTaskRunPage(page = 1, size = 10):
    start = (page - 1) * size
    limit = str(start) + ',' + str(size)

    task_list = mw.M('tasks').where('status!=?', (1,)).field(__FIELD).limit(limit).order('id asc').select()
    count = mw.M('tasks').where('status!=?', (1,)).count()

    rdata = {}
    rdata['list'] = task_list
    rdata['count'] = count
    return rdata


def setTaskStatus(task_id,status = 0):
    mw.M('tasks').where('id=?',(task_id,)).update({'status':status})
    return True

def setTaskData(id, start = None,end = None):
    if start is not None:
        mw.M('tasks').where('id=?',(id,)).update({'start':start})
    if end is not None:
        mw.M('tasks').where('id=?',(id,)).update({'end':end})
    return True