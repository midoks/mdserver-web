# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import core.mw as mw

__FIELD = 'id,app_id,app_secret,status,add_time,update_time'

def addApp(app_id,app_secret):
	now_time = mw.getDateFromNow()
    add_data = {
        'app_id': app_id,
        'app_secret': app_secret,
        'status': 1,
        'add_time': now_time,
        'update_time': now_time
    }
    return mw.M('app').insert(add_data)

def getAppList(
	page:int | None = 1,
    size:int | None = 10,
):	
	m = mw.M('app').field(__FIELD)

	start = (int(page) - 1) * (int(size))
    limit = str(start) + ',' +str(size)
	app_list = m.limit(limit).order('id desc').select()
	count = m.count()

	data = {}
    data['list'] = app_list
    data['count'] = count
    return data

def getAppById(aid):
	return mw.M('app').field(__FIELD).where("id=?", (aid,)).find()

def deleteAppById(aid):
    return mw.M('app').where("id=?", (aid,)).delete()

def setAppData(aid,
    status: str | None = None,
    app_id: str | None = None,
    app_secret: str | None = None,
):
    up_data = {}
    if status is not None:
        up_data['status'] = status
    if app_id is not None:
        up_data['app_id'] = app_id
    if app_secret is not None:
        up_data['app_secret'] = app_secret
    return mw.M('app').where('id=?',(aid,)).update(up_data)
