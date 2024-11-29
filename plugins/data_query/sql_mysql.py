# coding:utf-8

import sys
import io
import os
import time
import re
import pymongo
import json

web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw

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
        rep = r'port\s*=\s*(.*)'

        port_re = re.search(rep, my_content)
        if port_re:
            result['port'] = int(port_re.groups()[0].strip())
        else:
            result['port'] = 3306

        socket_rep = r'socket\s*=\s*(.*)'
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
        if table == '':
            page_args = {}
            page_args['count'] = 0
            page_args['tojs'] = 'mysqlGetDataList'
            page_args['p'] = 1
            page_args['row'] = 10

            rdata = {}
            rdata['page'] = mw.getPage(page_args)
            rdata['list'] = []
            rdata['count'] = 0
            return mw.returnData(True,'ok', rdata)

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

    def getNetRow(self, my_instance):
        row = {}

        data = my_instance.find("SHOW GLOBAL STATUS LIKE 'Com_select'")
        row['select'] = data['Value']

        data = my_instance.find("SHOW GLOBAL STATUS LIKE 'Com_insert'")
        row['insert'] = data['Value']

        data = my_instance.find("SHOW GLOBAL STATUS LIKE 'Com_update'")
        row['update'] = data['Value']

        data = my_instance.find("SHOW GLOBAL STATUS LIKE 'Com_delete'")
        row['delete']  = data['Value']

        

        data = my_instance.find("SHOW GLOBAL STATUS LIKE 'Bytes_received'")
        row['recv_bytes']  = data['Value']

        data = my_instance.find("SHOW GLOBAL STATUS LIKE 'Bytes_sent'")
        row['send_bytes']  = data['Value']
        return row


    def getNetList(self, args):
        from datetime import datetime
        sid = args['sid']
        my_instance = self.getInstanceBySid(sid).conn()
        if my_instance is False:
            return mw.returnData(False,'无法链接')

        rdata = []
        row = {}
        row1 = self.getNetRow(my_instance)
        # 等待1秒
        time.sleep(1)
        row2 = self.getNetRow(my_instance)

        data = my_instance.find("SHOW GLOBAL VARIABLES LIKE 'max_connections'")
        row['max_conn'] = data['Value']

        data = my_instance.find("SHOW GLOBAL STATUS LIKE 'Threads_connected'")
        row['conn']  = data['Value']

        current_time = datetime.now()
        row['current_time'] = current_time.strftime("%Y-%m-%d %H:%M:%S")

        row['select'] = int(row2['select']) - int(row1['select'])
        row['insert'] = int(row2['insert']) - int(row1['insert'])
        row['update'] = int(row2['update']) - int(row1['update'])
        row['delete'] = int(row2['delete']) - int(row1['delete'])

        recv_per_second = int(row2['recv_bytes']) - int(row1['recv_bytes'])
        send_per_second = int(row2['send_bytes']) - int(row1['send_bytes'])

        # 将每秒接收和发送数据量从字节转换为兆比特
        row['recv_mbps'] = "{:.2f}".format(recv_per_second * 8 / 1000000) + " MBit/s" 
        row['send_mbps'] = "{:.2f}".format(send_per_second * 8 / 1000000) + " MBit/s"

        rdata.append(row)
        return mw.returnData(True, 'ok', rdata)


    def getTopnList(self, args):
        sid = args['sid']
        my_instance = self.getInstanceBySid(sid).conn()
        if my_instance is False:
            return mw.returnData(False,'无法链接')

        is_performance_schema = my_instance.find("SELECT @@performance_schema")
        if is_performance_schema["@@performance_schema"] == 0:
            msg = "performance_schema参数未开启。\n"
            msg += "在my.cnf配置文件里添加performance_schema=1，并重启mysqld进程生效。"
            return mw.returnData(False, msg)

        my_instance.execute("SET @sys.statement_truncate_len=4096")
        data = my_instance.query("select query,db,last_seen,exec_count,max_latency,avg_latency from sys.statement_analysis order by exec_count desc, last_seen desc limit 10")
        if data is None:
            return mw.returnData(False, "查询失败!")
        return mw.returnData(True, 'ok', data)

    # 查看重复或冗余的索引
    def getRedundantIndexes(self, args):
        sid = args['sid']
        my_instance = self.getInstanceBySid(sid).conn()
        if my_instance is False:
            return mw.returnData(False,'无法链接')

        is_performance_schema = my_instance.find("SELECT @@performance_schema")
        if is_performance_schema["@@performance_schema"] == 0:
            msg = "performance_schema参数未开启。\n"
            msg += "在my.cnf配置文件里添加performance_schema=1，并重启mysqld进程生效。"
            return mw.returnData(False, msg)

        data = my_instance.query("select table_schema,table_name,redundant_index_name,redundant_index_columns,sql_drop_index from sys.schema_redundant_indexes")
        if data is None:
            return mw.returnData(False, "查询失败!")
        # print(data)
        return mw.returnData(True, 'ok', data)

    def redundantIndexesCmd(self, args):
        sid = args['sid']
        my_instance = self.getInstanceBySid(sid).conn()
        if my_instance is False:
            return mw.returnData(False,'无法链接')

        is_performance_schema = my_instance.find("SELECT @@performance_schema")
        if is_performance_schema["@@performance_schema"] == 0:
            msg = "performance_schema参数未开启。\n"
            msg += "在my.cnf配置文件里添加performance_schema=1，并重启mysqld进程生效。"
            return mw.returnData(False, msg)

        data = my_instance.query("select table_schema,table_name,redundant_index_name,redundant_index_columns,sql_drop_index from sys.schema_redundant_indexes")
        if data is None:
            return mw.returnData(False, "查询失败!")

        index = int(args['index'])

        cmd = data[index]['sql_drop_index']

        my_instance.execute(cmd)
        return mw.returnData(True, '执行成功!')
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

# 查询执行次数最频繁的前N条SQL语句
def get_topn_list(args):
    t = nosqlMySQLCtr()
    return t.getTopnList(args)

# MySQL服务器的QPS/TPS/网络带宽指标
def get_net_list(args):
    t = nosqlMySQLCtr()
    return t.getNetList(args)

# 查看重复或冗余的索引
def get_redundant_indexes(args):
    t = nosqlMySQLCtr()
    return t.getRedundantIndexes(args)

# 查看重复或冗余的索引
def redundant_indexes_cmd(args):
    t = nosqlMySQLCtr()
    return t.redundantIndexesCmd(args)





# 测试
def test(args):
    sid = args['sid']
    t = nosqlMySQLCtr()
    print(t.get_options())
    print("test")
    return 'ok'