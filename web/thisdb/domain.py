# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import core.mw as mw

__FIELD = 'id,pid,name,port,add_time'

def getDomainCountByName(name):
    # .debug(True)
    return mw.M('domain').where("name=?", (name,)).count()

def getDomainCountBySiteId(site_id):
    # .debug(True)
    return mw.M('domain').where("pid=?", (site_id,)).count()

def addDomain(site_id, name, port):
    now_time = mw.getDateFromNow()
    insert_data = {
        'pid': site_id,
        'name': name,
        'port':port,
        'add_time': now_time,
    }
    return mw.M('domain').insert(insert_data)
    
def getDomainBySiteId(site_id):
    # .debug(True)
    return mw.M('domain').field(__FIELD).where("pid=?", (site_id,)).select()
    

def deleteDomainId(domain_id):
    return mw.M('domain').where("id=?", (domain_id,)).delete()

def deleteDomainBySiteId(site_id):
    return mw.M('domain').where("pid=?", (site_id,)).delete()
