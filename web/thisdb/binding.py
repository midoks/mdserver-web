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

def getBindingCountByDomain(name):
    # .debug(True)
    return mw.M('binding').where("domain=?", (name,)).count()

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
    # .debug(True)
    binding_list = mw.M('binding').field(__FIELD).where('pid=?', (site_id,)).select()
    return binding_list

def getBindingById(site_id):
    return mw.M('binding').where("id=?", (site_id,)).field(__FIELD).find()


def deleteBindingById(binding_id):
    return mw.M('binding').where("id=?", (binding_id,)).delete()

def deleteBindingBySiteId(site_id):
    return mw.M('binding').where("pid=?", (site_id,)).delete()
