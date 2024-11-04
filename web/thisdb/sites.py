# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import core.mw as mw

def getSitesCount():
    return mw.M('sites').count()


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


    dbM = dbC = mw.M('sites').field('id,name,path,status,ps,edate,type_id,add_time,update_time')

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

