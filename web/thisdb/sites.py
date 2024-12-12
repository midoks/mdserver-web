# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import core.mw as mw

from .option  import getOption

__FIELD = 'id,name,path,status,ps,edate,type_id,add_time,update_time'

def checkSitesDomainIsExist(domain, port):
    nums = mw.M('domain').where("name=? AND port=?", (domain, port,)).count()
    if nums>0:
        return True

    nums = mw.M('binding').where("name=? AND port=?", (domain, port,)).count()
    if nums>0:
        return True
    return False

def getSitesCount():
    return mw.M('sites').count()

def getSitesById(site_id):
    return mw.M('sites').field(__FIELD).where("id=?", (site_id,)).find()

def getSitesByName(site_name):
    return mw.M('sites').field(__FIELD).where("name=?", (site_name,)).find()

def getSitesDomainById(site_id):
    data = {}
    domains = mw.M('domain').where('pid=?', (site_id,)).field('name,id').select()
    binding = mw.M('binding').where('pid=?', (site_id,)).field('domain,id').select()
    for b in binding:
        t = {}
        t['name'] = b['domain']
        t['id'] = b['id']
        domains.append(t)
    data['domains'] = domains
    data['email'] = getOption('ssl_email', default='')
    return data

def addSites(name, path):
    now_time = mw.getDateFromNow()
    insert_data = {
        'name': name,
        'path': path,
        'status': 1,
        'ps':name,
        'type_id':0,
        'edate':'0000-00-00',
        'add_time': now_time,
        'update_time': now_time
    }
    return mw.M('sites').insert(insert_data)


def isSitesExist(name):
    if mw.M('sites').where("name=?", (name,)).count() > 0:
        return True
    return False

def getSitesEdateList(edate):
    elist = mw.M('sites').field(__FIELD).where('edate>? AND edate<? AND status=?', ('0000-00-00', edate, 1,)).select()
    return elist

def getSitesList(
    page = 1,
    size = 10,
    type_id = 0,
    search = '',
    order = None,
):
    sql_where = ''
    if search != '' :
        sql_where = " name like '%" + search + "%' or ps like '%" + search + "%' "
    if type_id != '' and int(type_id) >= 0 and search != '' :
        sql_where = sql_where + " and type_id=" + str(type_id) + ""
    if type_id != '' and int(type_id) >= 0:
        sql_where = " type_id=" + str(type_id)


    dbM = dbC = mw.M('sites').field(__FIELD)

    if sql_where != '':
        count = dbC.where(sql_where).count()
    else:
        count = dbC.count()

    start = (int(page) - 1) * (int(size))
    limit = str(start) + ',' +str(size)

    if order is not None:
        site_list = dbM.limit(limit).order(order).select()
    else:
        site_list = dbM.limit(limit).order('id desc').select()

    
    data = {}
    data['list'] = site_list
    data['count'] = count
    return data


def deleteSitesById(site_id):
    return mw.M('sites').where("id=?", (site_id,)).delete()

def setSitesData(site_id, edate = None, ps = None, path = None,status = None):
    update_data = {}
    if edate is not None:
        update_data['edate'] = edate
    if ps is not None:
        update_data['ps'] = ps

    if path is not None:
        update_data['path'] = path

    if status is not None:
        update_data['status'] = status

    return mw.M('sites').where('id=?',(site_id,)).update(update_data)

