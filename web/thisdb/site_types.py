# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

__FIELD = 'id,name'

import core.mw as mw

def getSiteTypesList():
    # .debug(True)
    return mw.M('site_types').field(__FIELD).order("id asc").select()


