# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import core.mw as mw

def getTaskCount(
        status: int | None = -1
    ) -> int:
    return mw.M('tasks').where('status=?',(1,)).count()


# 未执行任务总数
def getTaskUnexecutedCount() -> int:
    return mw.M('tasks').where('status!=?',(1,)).count()

def addTask(
    name: str | None = '常用任务',
    cmd: str | None = None,
    type: str | None = 'execshell',
    status: int | None = 0,
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
    status: int | None = 1,
    page: int | None = 1,
    size: int | None = 10,
):
    start = (page - 1) * size
    limit = str(start) + ',' + str(size)

    field = 'id,name,type,start,end,status,add_time'
    task_list = mw.M('tasks').where('', ()).field(field).limit(limit).order('id asc').select()
    return task_list

def getTaskPage(
    status: int | None = 1,
    page: int | None = 1,
    size: int | None = 10,
):
    start = (page - 1) * size
    limit = str(start) + ',' + str(size)

    field = 'id,name,type,start,end,status,add_time'
    task_list = mw.M('tasks').where('', ()).field(field).limit(limit).order('id asc').select()
    count = mw.M('tasks').where('', ()).count()

    rdata = {}
    rdata['list'] = task_list
    rdata['count'] = count
    return rdata

def getTaskFirstByRun() -> None:
    field = 'id,name,type,start,end,status,add_time'
    data = mw.M('tasks').where('status=?', (-1,)).field(field).order('id asc').find()
    if item is None:
        return None
    return data

def getTaskRunList(
    page: int | None = 1,
    size: int | None = 10,
):
    start = (page - 1) * size
    limit = str(start) + ',' + str(size)

    field = 'id,name,type,start,end,status,add_time'
    task_list = mw.M('tasks').where('', ()).field(field).limit(limit).order('id desc').select()
    count = mw.M('tasks').where('', ()).count()

    rdata = {}
    rdata['list'] = task_list
    rdata['count'] = count
    return rdata


def setTaskStatus(id,
    status: int | None = 0
):
    mw.M('tasks').where('id=?',(id,)).update({'status':status})
    return True

def setTaskData(id,
    start: int | None = None,
    end: int | None = None,
):
    if start is not None:
        mw.M('tasks').where('id=?',(id,)).update({'start':start})
    if end is not None:
        mw.M('tasks').where('id=?',(id,)).update({'end':end})
    return True