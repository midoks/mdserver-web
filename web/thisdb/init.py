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


def initPanelData():
    _dbfile = mw.getPanelDataDir() + '/panel.db'
    if os.path.exists(_dbfile):
        return True
    sql_file = mw.getPanelDataDir() + '/sql/default.sql'
    sql = mw.M().dbPos(mw.getPanelDataDir(),'panel')
    csql = mw.readFile(sql_file)
    csql_list = csql.split(';')
    for index in range(len(csql_list)):
        print(index)
        sql.execute(csql_list[index], ())
    return True