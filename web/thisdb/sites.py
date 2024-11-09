# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import core.mw as mw

__FIELD = 'id,name,path,status,ps,edate,type_id,add_time,update_time'

def getSitesCount():
    return mw.M('sites').count()


def getSitesById(site_id):
    return mw.M('sites').field(__FIELD).where("id=?", (site_id,)).find()

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

def getSitesList(
    page:int | None = 1,
    size:int | None = 10,
    type_id:int | None = 0,
    search: str | None = ''
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
    site_list = dbM.limit(limit).order('id desc').select()

    
    data = {}
    data['list'] = site_list
    data['count'] = count
    return data


def deleteSitesById(site_id):
    return mw.M('sites').where("id=?", (site_id,)).delete()

def setSitesData(site_id,
    edate: str | None = None,
    ps: str | None = None,
    path: str | None = None,
):
    update_data = {}
    if edate is not None:
        update_data['edate'] = edate
    if ps is not None:
        update_data['ps'] = ps

    if path is not None:
        update_data['path'] = path

    return mw.M('sites').where('id=?',(site_id,)).update(update_data)

