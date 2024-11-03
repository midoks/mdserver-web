# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import core.mw as mw

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