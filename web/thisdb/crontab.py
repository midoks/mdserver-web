# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os

import core.mw as mw

__field = 'id,name,type,where1,where_hour,where_minute,echo,status,save,backup_to,stype,sname,sbody,url_address,add_time,update_time'

def addCrontab(data):
    now_time = mw.formatDate()
    data['add_time'] = now_time
    data['update_time'] = now_time
    return mw.M('crontab').insert(data)

def getCronByName(name):
    return mw.M('crontab').where("name=?", (name,)).find()

def setCrontabData(cron_id, data):
    mw.M('crontab').where('id=?', (cron_id,)).update(data)
    return True

def setCrontabStatus(cron_id, status):
    mw.M('crontab').where('id=?', (cron_id,)).update({'status':status})
    return True

def getCrond(id):
    return mw.M('crontab').where('id=?', (id,)).field(__field).find()

def deleteCronById(cron_id):
    mw.M('crontab').where("id=?", (cron_id,)).delete()
    return True

def getCrontabList(
    page = 1,
    size = 10,
):
    start = (int(page) - 1) * size
    limit = str(start) + ',' + str(size)

    cron_list = mw.M('crontab').field(__field).limit(limit).order('id desc').select()
    count = mw.M('crontab').count()

    data = {}
    data['count'] = count
    data['list'] = cron_list
    return data

