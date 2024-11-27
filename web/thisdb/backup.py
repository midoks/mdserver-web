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

__FIELD = 'id,type,name,pid,filename,size,add_time'

def getBackupPage(
    site_id = 1,
    page = 1,
    size = 10,
):
    start = (page - 1) * size
    limit = str(start) + ',' + str(size)
    bk_list = mw.M('backup').where('pid=?', (site_id,)).field(__FIELD).limit(limit).order('id desc').select()
    count = mw.M('backup').where('pid=?', (site_id,)).count()

    rdata = {}
    rdata['list'] = bk_list
    rdata['count'] = count
    return rdata
