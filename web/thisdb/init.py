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
    __dbfile = mw.getPanelDataDir() + '/panel.db'
    if os.path.exists(__dbfile):
        return True
    sql_file = mw.getPanelDir() + '/web/admin/setup/sql/default.sql'
    sql = mw.M().dbPos(mw.getPanelDataDir(),'panel')
    content = mw.readFile(sql_file)
    csql_data = content.split(';')
    for i in range(len(csql_data)):
        # print(csql_data[i])
        # print(sql.execute(csql_data[i], ()))
        sql.execute(csql_data[i], ())
    return True