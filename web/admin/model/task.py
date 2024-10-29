# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

from admin.model import db, Tasks

import core.mw as mw

def getTaskCount(
        status: int | None = -1
    ) -> int:
    return Tasks.query.filter(Tasks.status==status).count()

# 未执行任务总数
def getTaskUnexecutedCount() -> int:
    return Tasks.query.filter(Tasks.status!=1).count()


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
    add_data = Tasks(
        name=name,
        cmd=cmd, 
        type=type,
        start=0,
        end=0,
        status=status,
        add_time=add_time)
    db.session.add(add_data)
    db.session.commit()
    db.session.close()
    return True

def getTaskFirstByRun() -> None:
    item =  Tasks.query.filter(Tasks.status==-1).order_by(Tasks.id.asc()).first()

    if item is None:
        return None
    row = {}
    row['id'] = item.id
    row['name'] = item.name
    row['type'] = item.type
    row['cmd'] = item.cmd
    row['start'] = item.start
    row['end'] = item.end
    row['status'] = item.status
    row['add_time'] = item.add_time
    return row

def getTaskList(
    status: int | None = 1,
    page: int | None = 1,
    size: int | None = 10,
):
    pagination = Tasks.query.filter(Tasks.status==status).order_by(Tasks.id.asc()).paginate(page=int(page), per_page=int(size))
  
    rows = []
    for item in pagination.items:
        t = {}
        t['id'] = item.id
        t['name'] = item.name
        t['type'] = item.type
        t['cmd'] = item.cmd
        t['start'] = item.start
        t['end'] = item.end
        t['status'] = item.status
        t['add_time'] = item.add_time
        rows.append(t)
    return rows




def setTaskStatus(id,
    status: int | None = 0
):
    Tasks.query.filter(Tasks.id==id).update({'status':status})
    db.session.commit()
    return True

def setTaskData(id,
    start: int | None = None,
    end: int | None = None,
):
    update_data = {}

    if start is not None:
        update_data['start'] = start
    if end is not None:
        update_data['end'] = end

    Tasks.query.filter(Tasks.id==id).update(update_data)
    db.session.commit()
    return True

