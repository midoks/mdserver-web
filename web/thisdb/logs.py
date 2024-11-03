# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------



import core.mw as mw

def clearLog():
    mw.M('logs').where('id>?', (0,)).delete()
    return True

def addLog(type, log,
    uid: int | None = 1
) -> str:
    '''
    添加日志
    :type -> str 类型 (必填)
    :log -> str 日志内容 (必填)
    :uid -> int 用户ID
    '''
    add_time = mw.formatDate()
    insert_data = {
        'name':name,
        'type':type,
        'log':log,
        'add_time':add_time,
    }
    mw.M('logs').insert(insert_data)
    return True