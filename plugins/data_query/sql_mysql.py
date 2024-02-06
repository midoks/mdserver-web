# coding:utf-8

import sys
import io
import os
import time
import re
import pymongo
import json


sys.path.append(os.getcwd() + "/class/core")
import mw

def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner


@singleton
class nosqlMySQL():

    __DB_PASS = None
    __DB_USER = None
    __DB_PORT = 3306
    __DB_HOST = '127.0.0.1'
    __DB_CONN = None
    __DB_ERR = None
    __DB_SOCKET = None

    __DB_LOCAL = None

    def __init__(self):
        self.__config = self.get_options(None)


    def conn(self):

        if self.__DB_HOST in ['127.0.0.1', 'localhost']:
            my_path = "{}/mysql".format(mw.getServerDir())
            if not os.path.exists(my_path): return False

        if not self.__DB_LOCAL:
            # print(self.__config)
            self.__DB_PORT = int(self.__config['port'])
            self.__DB_USER = self.__config['username']
            self.__DB_PASS = self.__config['password']
            self.__DB_SOCKET = self.__config['socket']

        try:

            db = mw.getMyORM()
            db.setPort(self.__DB_PORT)
            db.setPwd(self.__DB_PASS)
            db.setUser(self.__DB_USER)
            if self.__DB_SOCKET != '':
                db.setSocket(self.__DB_SOCKET)

            return db
        except Exception:
            self.__DB_ERR = mw.get_error_info()
        return False

    def sqliteDb(self,dbname='databases'):
        my_root_path = mw.getServerDir() +'/mysql'
        name = 'mysql'
        conn = mw.M(dbname).dbPos(my_root_path, name)
        return conn

    # 获取配置项
    def get_options(self, get=None):
        result = {}


        my_cnf_path = "{}/mysql/etc/my.cnf".format(mw.getServerDir())
        my_content = mw.readFile(my_cnf_path)
        if not my_content: return False

        mysql_pass = self.sqliteDb('config').where('id=?', (1,)).getField('mysql_root')
        result['password'] = mysql_pass
        result['username'] = 'root'
        keys = ["bind_ip", "port"]

        result['host'] = '127.0.0.1'
        rep = 'port\s*=\s*(.*)'

        port_re = re.search(rep, my_content)
        if port_re:
            result['port'] = int(port_re.groups()[0].strip())
        else:
            result['port'] = 3306

        socket_rep = 'socket\s*=\s*(.*)'
        socket_re = re.search(socket_rep, my_content)
        if socket_re:
            result['socket'] = socket_re.groups()[0].strip()
        else:
            result['socket'] = ''

        return result

    def set_host(self, host, port, name, username, password, prefix=''):
        self.__DB_HOST = host
        self.__DB_PORT = int(port)
        self.__DB_NAME = name
        if self.__DB_NAME: self.__DB_NAME = str(self.__DB_NAME)
        self.__DB_USER = str(username)
        self._USER = str(username)
        self.__DB_PASS = str(password)
        self.__DB_PREFIX = prefix
        self.__DB_LOCAL = 1
        return self



@singleton
class nosqlMySQLCtr():

    def __init__(self):
        pass

    def getInstanceBySid(self, sid = 0):
        instance = nosqlMySQL()
        return instance

    def getDbList(self, args):
        sid = args['sid']
        my_instance = self.getInstanceBySid(sid).conn()
        if my_instance is False:
            return mw.returnData(False,'无法链接')

        result = {}
        db_list = my_instance.query('show databases')
        rlist = []
        for x in db_list:
            if not x['Database'] in ['information_schema', 'mysql', 'performance_schema','sys']:
                rlist.append(x['Database'])
        result['list'] = rlist
        return mw.returnData(True,'ok', result)

    def getTableList(self, args):
        sid = args['sid']
        db = args['db']

        my_instance = self.getInstanceBySid(sid).conn()
        if my_instance is False:
            return mw.returnData(False,'无法链接')

        sql = "select * from information_schema.tables where table_schema = '"+db+"'"
        table_list = my_instance.query(sql)
        # print(table_list)

        rlist = []
        for x in table_list:
            # print(x['TABLE_NAME'])
            rlist.append(x['TABLE_NAME'])
        result = {}
        result['list'] = rlist
        return mw.returnData(True,'ok', result)

    def getDataList(self, args):
        sid = args['sid']
        db = args['db']
        table = args['table']
        p = 1
        size = 10
        if 'p' in args:
            p = args['p']

        if 'size' in args:
            size = args['size']

        start_index = (p - 1) * size


        args_where = {}
        where_sql = ''
        if 'where' in args:
            args_where = args['where']
            if 'field' in args_where:
                if args_where['field'] == 'id' or args_where['field'].find('id')>-1:
                    where_sql = ' where '+args_where['field'] + " = '"+args_where['value']+"' "
                else:
                    where_sql = ' where '+args_where['field'] + " like '%"+args_where['value']+"%' "

        my_instance = self.getInstanceBySid(sid).conn()
        if my_instance is False:
            return mw.returnData(False,'无法链接')

        my_instance.setDbName(db)
        sql = 'select count(*) as num from ' + table + where_sql
        # print(sql)
        count_result = my_instance.query(sql)
        count = count_result[0]['num']


        sql = 'select * from ' + table + where_sql + ' limit '+str(start_index)+',10';
        # print(sql)
        result = my_instance.query(sql)

        for i in range(len(result)):
            for f in result[i]:
                result[i][f] = str(result[i][f])

        # print(result)

        page_args = {}
        page_args['count'] = count
        page_args['tojs'] = 'mysqlGetDataList'
        page_args['p'] = p
        page_args['row'] = size

        rdata = {}
        rdata['page'] = mw.getPage(page_args)
        rdata['list'] = result
        rdata['count'] = count

        rdata['soso_field'] = ''
        if 'field' in args_where:
            rdata['soso_field'] = args_where['field']
        return mw.returnData(True,'ok', rdata)

    def showProcessList(self,args):
        sql = 'show processlist';
        sid = args['sid']

        my_instance = self.getInstanceBySid(sid).conn()
        if my_instance is False:
            return mw.returnData(False,'无法链接')

        result = my_instance.query(sql)
        rdata = {}
        rdata['list'] = result
        return mw.returnData(True,'ok', rdata)

    def showStatusList(self,args):
        sql = 'show status';
        sid = args['sid']

        my_instance = self.getInstanceBySid(sid).conn()
        if my_instance is False:
            return mw.returnData(False,'无法链接')

        result = my_instance.query(sql)
        rdata = {}
        rdata['list'] = result
        return mw.returnData(True,'ok', rdata)

    def showStatsList(self, args):
        sql = "show status like 'Com_%'";
        sid = args['sid']

        my_instance = self.getInstanceBySid(sid).conn()
        if my_instance is False:
            return mw.returnData(False,'无法链接')

        result = my_instance.query(sql)
        rdata = {}
        rdata['list'] = result
        return mw.returnData(True,'ok', rdata)

# ---------------------------------- run ----------------------------------
# 获取 mysql 列表
def get_db_list(args):
    t = nosqlMySQLCtr()
    return t.getDbList(args)

# 获取 mysql 列表
def get_table_list(args):
    t = nosqlMySQLCtr()
    return t.getTableList(args)

def get_data_list(args):
    t = nosqlMySQLCtr()
    return t.getDataList(args)

def get_proccess_list(args):
    t = nosqlMySQLCtr()
    return t.showProcessList(args)

def get_status_list(args):
    t = nosqlMySQLCtr()
    return t.showStatusList(args)

def get_stats_list(args):
    t = nosqlMySQLCtr()
    return t.showStatsList(args)


# 测试
def test(args):
    sid = args['sid']
    t = nosqlMySQLCtr()
    print(t.get_options())
    print("test")
    return 'ok'