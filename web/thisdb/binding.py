# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import core.mw as mw

# 站点-子目录绑定

__FIELD = 'id,pid,domain,port,path,add_time'

def addBinding(pid, domain, port, path):
    now_time = mw.getDateFromNow()
    insert_data = {
        'pid': pid,
        'domain': domain,
        'port':port,
        'path':path,
        'add_time': now_time,
    }
    return mw.M('binding').insert(insert_data)


def getBindingListBySiteId(site_id):
    task_list = mw.M('binding').where('pid=?', (site_id,)).field(__FIELD).select()
    return task_list



def deleteBindingId(domain_id):
    return mw.M('binding').where("id=?", (domain_id,)).delete()

def deleteBindingBySiteId(site_id):
    return mw.M('binding').where("pid=?", (site_id,)).delete()
