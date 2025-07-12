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
    is_reload = False
    sql_file = mw.getPanelDir() + '/web/admin/setup/sql/default.sql'
    sql_file_md5 = mw.getPanelDir() + '/web/admin/setup/sql/default.md5'
    content = mw.readFile(sql_file)
    content_md5 = mw.md5(content)
    if not os.path.exists(sql_file_md5):
        mw.writeFile(sql_file_md5, content_md5)

    sql = mw.M().dbPos(mw.getPanelDataDir(),'panel')
    csql_data = content.split(';')
    for i in range(len(csql_data)):
        sql.execute(csql_data[i], ())
    return True

def reinstallPanelData():
    is_reload = False
    sql_file = mw.getPanelDir() + '/web/admin/setup/sql/default.sql'
    sql_file_md5 = mw.getPanelDir() + '/web/admin/setup/sql/default.md5'
    content = mw.readFile(sql_file)
    content_md5 = mw.md5(content)
    if not os.path.exists(sql_file_md5):
        mw.writeFile(sql_file_md5, content_md5)

    content_src_md5 = mw.readFile(sql_file)
    if content_md5 != content_src_md5:
        is_reload = True

    __dbfile = mw.getPanelDataDir() + '/panel.db'
    if os.path.exists(__dbfile) and not is_reload:
        return True
    sql = mw.M().dbPos(mw.getPanelDataDir(),'panel')
    csql_data = content.split(';')
    for i in range(len(csql_data)):
        # print(csql_data[i])
        # print(sql.execute(csql_data[i], ()))
        sql.execute(csql_data[i], ())

    mw.writeFile(sql_file_md5, content_md5)
    return True