# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import json


import core.mw as mw

def clearLog():
    mw.M('logs').where('id>?', (0,)).delete()
    mw.M('logs').execute("update sqlite_sequence set seq=0 where name='logs'")
    return True

def addLog(type, log, uid = 1) -> str:
    '''
    添加日志
    :type -> str 类型 (必填)
    :log -> str 日志内容 (必填)
    :uid -> int 用户ID
    '''
    add_time = mw.formatDate()
    insert_data = {
        'type':type,
        'log':log,
        'add_time':add_time,
    }
    mw.M('logs').insert(insert_data)
    return True

def getLogsList(page = 1,size = 10,search = ''):
    sql_where = ''
    if search != '' :
        sql_where = " type like '%" + search + "%' or log like '%" + search + "%' "

    field = 'id,type,log,uid,add_time'
    dbM = dbC = mw.M('logs').field(field)

    if sql_where != '':
        count = mw.M('logs').field(field).where(sql_where).count()
    else:
        count = mw.M('logs').field(field).count()

    start = (int(page) - 1) * (int(size))
    limit = str(start) + ',' +str(size)
    logs_list = mw.M('logs').field(field).limit(limit).order('id desc').select()

    data = {}
    data['list'] = logs_list
    data['count'] = count
    return data