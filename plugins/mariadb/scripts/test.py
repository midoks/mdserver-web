# coding:utf-8

import sys
import io
import os
import time
import subprocess
import re
import json

cur_dir = os.getcwd()
plugin_dir = os.path.dirname(cur_dir)

# print(plugin_dir)
root_dir = os.path.dirname(os.path.dirname(plugin_dir))
# print(root_dir)

sys.path.append(root_dir + "/class/core")
import mw

os.chdir(root_dir)


def getPluginName():
    return 'mariadb'


def getPluginDir():
    return root_dir + '/plugins/' + getPluginName()


def getServerDir():
    return os.path.dirname(root_dir) + '/' + getPluginName()


def pSqliteDb(dbname='databases'):
    file = getServerDir() + '/mariadb.db'
    name = 'mysql'
    if not os.path.exists(file):
        conn = mw.M(dbname).dbPos(getServerDir(), name)
        csql = mw.readFile(getPluginDir() + '/conf/mariadb.sql')
        csql_list = csql.split(';')
        for index in range(len(csql_list)):
            conn.execute(csql_list[index], ())
    else:
        conn = mw.M(dbname).dbPos(getServerDir(), name)
    return conn


def getConf():
    path = getServerDir() + '/etc/my.cnf'
    return path


def pMysqlDb():
    db = mw.getMyORM()
    db.setDbConf(getConf())
    db.__DB_SOCKET = mw.getServerDir() + '/mysql/mysql.socket'

    print(mw.getServerDir() + '/mysql/mysql.socket')
    db.setPwd(pSqliteDb('config').where('id=?', (1,)).getField('mysql_root'))
    return db

if __name__ == '__main__':
    p = pMysqlDb()
    print(p.query("select User,Host from mysql.user where User!='root' AND Host!='localhost' AND Host!=''"))
