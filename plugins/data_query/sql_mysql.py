# coding:utf-8

import sys
import io
import os
import time
import re
import pymongo
import json

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

    __sid = None

    __DB_PASS = None
    __DB_USER = None
    __DB_PORT = 3306
    __DB_HOST = '127.0.0.1'
    __DB_CONN = None
    __DB_ERR = None
    __DB_STATUS = None
    __DB_SOCKET = None

    __DB_LOCAL = None

    def __init__(self):
        pass
        
    def setSid(self, sid):
        self.__sid = sid
        self.__config = self.get_options(sid=sid)

    def conn(self):

        if self.__sid is None:
            self.__DB_STATUS = 'not_installed'
            return False

        if self.__sid is not None:
            mycnf_path = "{}/{}/etc/my.cnf".format(mw.getServerDir(),self.__sid)
            if not os.path.exists(mycnf_path):
                self.__DB_STATUS = 'not_installed'
                return False

        if not self.__config:
            self.__DB_STATUS = 'not_installed'
            return False

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

            # 实际连通性检查：服务未启动或账号错误时返回 False，调用方统一提示
            db.query('select 1')
            self.__DB_STATUS = None
            return db
        except Exception:
            self.__DB_ERR = mw.getTracebackInfo()
        self.__DB_STATUS = 'not_running'
        return False

    # 连接状态：not_installed 未安装 / not_running 未启动 / None 正常
    def get_status(self):
        return self.__DB_STATUS

    def sqliteDb(self, db_pos_name, dbname='databases'):
        mydb_path = mw.getServerDir() +'/'+db_pos_name
        name = 'mysql'
        conn = mw.M(dbname).dbPos(mydb_path, name)
        return conn

    # 获取配置项
    def get_options(self, sid=None):
        result = {}
        result['socket'] = ''
        result['port'] = 3306
        result['host'] = '127.0.0.1'
        result['username'] = 'root'

        if sid in ['mysql', 'mysql-apt', 'mysql-yum', 'mysql-community','mariadb']:
            my_cnf_path = "{}/{}/etc/my.cnf".format(mw.getServerDir(),sid)
            if not os.path.exists(my_cnf_path):
                return False

            mydb_content = mw.readFile(my_cnf_path)
            if not mydb_content: return False

            mysql_pass = self.sqliteDb(sid, 'config').where('id=?', (1,)).getField('mysql_root')
            result['password'] = mysql_pass

            rep = r'port\s*=\s*(.*)'
            port_re = re.search(rep, mydb_content)
            if port_re:
                result['port'] = int(port_re.groups()[0].strip())
            socket_rep = r'socket\s*=\s*(.*)'
            socket_re = re.search(socket_rep, mydb_content)
            if socket_re:
                result['socket'] = socket_re.groups()[0].strip()
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

    def getServerList(self):
        my_cnf_path = "{}/mysql/etc/my.cnf".format(mw.getServerDir())
        data = []

        local_mysql = "{}/mysql/etc/my.cnf".format(mw.getServerDir())
        if os.path.exists(local_mysql):
            data.append({'name':'本地服务器', 'val':'mysql'})

        local_mysql_apt = "{}/mysql-apt/etc/my.cnf".format(mw.getServerDir())
        if os.path.exists(local_mysql_apt):
            data.append({'name':'本地服务器[apt]', 'val':'mysql-apt'})

        local_mysql_yum = "{}/mysql-yum/etc/my.cnf".format(mw.getServerDir())
        if os.path.exists(local_mysql_yum):
            data.append({'name':'本地服务器[yum]', 'val':'mysql-yum'})

        local_mysql_yum = "{}/mysql-community/etc/my.cnf".format(mw.getServerDir())
        if os.path.exists(local_mysql_yum):
            data.append({'name':'本地服务器[Tar]', 'val':'mysql-community'})

        local_mysql_yum = "{}/mariadb/etc/my.cnf".format(mw.getServerDir())
        if os.path.exists(local_mysql_yum):
            data.append({'name':'本地服务器[mariadb]', 'val':'mariadb'})
        return mw.returnData(True, 'ok', data)

@singleton
class nosqlMySQLCtr():

    def __init__(self):
        pass

    def getServerList(self, args):
        instance = nosqlMySQL()
        return instance.getServerList()

    def getInstanceBySid(self, sid):
        instance = nosqlMySQL()
        instance.setSid(sid)
        return instance

    def _connect(self, sid):
        obj = self.getInstanceBySid(sid)
        conn = obj.conn()
        if conn is False:
            if obj.get_status() == 'not_installed':
                return None, mw.returnData(False, '未安装')
            return None, mw.returnData(False, '未启动')
        return conn, None

    def getDbList(self, args):
        sid = args['sid']
        my_instance, err = self._connect(sid)
        if err:
            return err

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

        my_instance, err = self._connect(sid)
        if err:
            return err

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

        my_instance, err = self._connect(sid)
        if err:
            return err

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

        my_instance, err = self._connect(sid)
        if err:
            return err

        result = my_instance.query(sql)
        rdata = {}
        rdata['list'] = result
        return mw.returnData(True,'ok', rdata)

    def showStatusList(self,args):
        sql = 'show status';
        sid = args['sid']

        my_instance, err = self._connect(sid)
        if err:
            return err

        result = my_instance.query(sql)
        rdata = {}
        rdata['list'] = result
        return mw.returnData(True,'ok', rdata)

    def showStatsList(self, args):
        sql = "show status like 'Com_%'";
        sid = args['sid']

        my_instance, err = self._connect(sid)
        if err:
            return err

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
        """无阻塞 QPS/TPS/网络带宽指标: 用上次快照做差分, 不 sleep."""
        from datetime import datetime
        sid = args['sid']
        my_instance, err = self._connect(sid)
        if err:
            return err

        # 初始化快照存储 (按 sid 区分, 支持多实例)
        if not hasattr(self, '__net_snaps'):
            self.__net_snaps = {}   # {sid: (timestamp, row_dict)}

        curr = self.getNetRow(my_instance)
        now = time.time()
        snap = self.__net_snaps.get(sid)

        if snap is None or (now - snap[0]) < 0.5:
            # 第一次调用 / 间隔太短: 差分不可靠, 返回 0 并记录快照
            diff_select = diff_insert = diff_update = diff_delete = 0.0
            diff_recv = diff_send = 0.0
        else:
            prev_ts, prev = snap
            elapsed = now - prev_ts
            diff_select = round((int(curr['select']) - int(prev['select'])) / elapsed, 2)
            diff_insert = round((int(curr['insert']) - int(prev['insert'])) / elapsed, 2)
            diff_update = round((int(curr['update']) - int(prev['update'])) / elapsed, 2)
            diff_delete = round((int(curr['delete']) - int(prev['delete'])) / elapsed, 2)
            diff_recv = int(curr['recv_bytes']) - int(prev['recv_bytes'])
            diff_send = int(curr['send_bytes']) - int(prev['send_bytes'])

        self.__net_snaps[sid] = (now, curr)

        data = my_instance.find("SHOW GLOBAL VARIABLES LIKE 'max_connections'")
        max_conn = data['Value'] if data else '-'

        data = my_instance.find("SHOW GLOBAL STATUS LIKE 'Threads_connected'")
        conn = data['Value'] if data else '0'

        row = {}
        row['current_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row['select'] = diff_select
        row['insert'] = diff_insert
        row['update'] = diff_update
        row['delete'] = diff_delete
        row['conn'] = conn
        row['max_conn'] = max_conn
        row['recv_mbps'] = "{:.2f} MBit/s".format(diff_recv * 8 / 1000000)
        row['send_mbps'] = "{:.2f} MBit/s".format(diff_send * 8 / 1000000)

        return mw.returnData(True, 'ok', [row])


    def getTopnList(self, args):
        sid = args['sid']
        my_instance, err = self._connect(sid)
        if err:
            return err

        is_performance_schema = my_instance.find("SELECT @@performance_schema")
        if is_performance_schema is None:
            return mw.returnData(False,'异常中断,重试!')

        if is_performance_schema["@@performance_schema"] == 0:
            msg = "performance_schema参数未开启。\n"
            msg += "在my.cnf配置文件里添加performance_schema=1，并重启mysqld进程生效。"
            return mw.returnData(False, msg)

        my_instance.execute("SET @sys.statement_truncate_len=4096")
        data = my_instance.query("select query,db,last_seen,exec_count,max_latency,avg_latency from sys.statement_analysis order by exec_count desc, last_seen desc limit 20")
        if data is None:
            return mw.returnData(False, "查询失败!")

        filter_db = args['filter_db']
        if filter_db == 'yes':
            new_data = []
            for x in data:
                if x['db'] is not None:
                    new_data.append(x)
            return mw.returnData(True, 'ok', new_data)
        return mw.returnData(True, 'ok', data)

    # 查看重复或冗余的索引
    def getRedundantIndexes(self, args):
        sid = args['sid']
        my_instance, err = self._connect(sid)
        if err:
            return err

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
        my_instance, err = self._connect(sid)
        if err:
            return err

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

    def getTableInfo(self, args):
        from decimal import Decimal

        sid = args['sid']
        my_instance, err = self._connect(sid)
        if err:
            return err

        my_instance.execute("SET sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''))")

        # ANY_VALUE 是 MySQL 5.7+ 的函数,MariaDB 不支持(报 FUNCTION ANY_VALUE does not exist);
        # 上面已去掉 ONLY_FULL_GROUP_BY,MariaDB 可直接取非聚合字段
        ver = my_instance.find("SELECT @@version as db_version")
        is_mariadb = ver is not None and 'MariaDB' in str(ver.get('db_version', ''))

        def any_val(expr):
            return expr if is_mariadb else 'ANY_VALUE(' + expr + ')'

        data = my_instance.query(
            """
            SELECT t.TABLE_SCHEMA as TABLE_SCHEMA, t.TABLE_NAME as TABLE_NAME,
                {engine} as ENGINE,
                {data_length} as DATA_LENGTH,
                {index_length} as INDEX_LENGTH,
                {total_length} AS TOTAL_LENGTH,
                {column_name} AS COLUMN_NAME, {data_type} AS DATA_TYPE,
                {column_type} AS COLUMN_TYPE,
                {auto_increment} AS AUTO_INCREMENT,
                {is_signed} AS IS_SIGNED
            FROM information_schema.TABLES t
            JOIN information_schema.COLUMNS c ON t.TABLE_SCHEMA = c.TABLE_SCHEMA AND t.table_name=c.table_name
            WHERE t.TABLE_SCHEMA NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
            GROUP BY t.TABLE_SCHEMA, t.TABLE_NAME
            ORDER BY TOTAL_LENGTH DESC, AUTO_INCREMENT DESC
            """.format(
                engine=any_val("t.ENGINE"),
                data_length=any_val("IFNULL(t.DATA_LENGTH/1024/1024/1024, 0)"),
                index_length=any_val("IFNULL(t.INDEX_LENGTH/1024/1024/1024, 0)"),
                total_length=any_val("IFNULL((t.DATA_LENGTH+t.INDEX_LENGTH)/1024/1024/1024, 0)"),
                column_name=any_val("c.column_name"),
                data_type=any_val("c.data_type"),
                column_type=any_val("c.COLUMN_TYPE"),
                auto_increment=any_val("t.AUTO_INCREMENT"),
                is_signed=any_val("locate('unsigned', c.COLUMN_TYPE) = 0"),
            )
        )

        if data is None:
            return mw.returnData(True, 'ok', [])
        if isinstance(data, Exception):
            return mw.returnData(False, '查询失败: ' + str(data))

        for i in range(len(data)):
            row = data[i]

            data[i]['DATA_LENGTH'] = round(row['DATA_LENGTH'] or 0, 2)
            data[i]['INDEX_LENGTH'] = round(row['INDEX_LENGTH'] or 0, 2)
            data[i]['TOTAL_LENGTH'] = round(row['TOTAL_LENGTH'] or 0, 2)

            AUTO_INCREMENT = row['AUTO_INCREMENT']
            DATA_TYPE = row['DATA_TYPE']
            IS_SIGNED = row['IS_SIGNED']
            RESIDUAL_AUTO_INCREMENT = 0
            if AUTO_INCREMENT is not None:
                if DATA_TYPE == 'tinyint':
                    if IS_SIGNED == 0:
                        RESIDUAL_AUTO_INCREMENT = int(255 - AUTO_INCREMENT)
                    if IS_SIGNED == 1:
                        RESIDUAL_AUTO_INCREMENT = int(127 - AUTO_INCREMENT)

                if DATA_TYPE == 'smallint':
                    if IS_SIGNED == 0:
                        RESIDUAL_AUTO_INCREMENT = int(65535 - AUTO_INCREMENT)
                    if IS_SIGNED == 1:
                        RESIDUAL_AUTO_INCREMENT = int(32767 - AUTO_INCREMENT)

                if DATA_TYPE == 'int':
                    if IS_SIGNED == 0:
                        RESIDUAL_AUTO_INCREMENT = int(4294967295 - AUTO_INCREMENT)
                    if IS_SIGNED == 1:
                        RESIDUAL_AUTO_INCREMENT = int(2147483647 - AUTO_INCREMENT)

                if DATA_TYPE == 'mediumint':
                    if IS_SIGNED == 0:
                        RESIDUAL_AUTO_INCREMENT = int(16777215 - AUTO_INCREMENT)
                    if IS_SIGNED == 1:
                        RESIDUAL_AUTO_INCREMENT = int(8388607 - AUTO_INCREMENT)

                if DATA_TYPE == 'bigint':
                    if IS_SIGNED == 0:
                        RESIDUAL_AUTO_INCREMENT = Decimal("18446744073709551615") - Decimal(AUTO_INCREMENT)
                    if IS_SIGNED == 1:
                        RESIDUAL_AUTO_INCREMENT = Decimal("9223372036854775807") - Decimal(AUTO_INCREMENT)
            else:
                RESIDUAL_AUTO_INCREMENT = "主键非自增"
            data[i]['RESIDUAL_AUTO_INCREMENT'] = RESIDUAL_AUTO_INCREMENT
        return mw.returnData(True, 'ok', data)

    # 查看应用端IP连接数总和
    def getConnCount(self, args):
        sid = args['sid']
        my_instance, err = self._connect(sid)
        if err:
            return err

        data = my_instance.query(
            "SELECT user,db,substring_index(HOST,':',1) AS Client_IP,count(1) AS count FROM information_schema.PROCESSLIST "
            "GROUP BY user,db,substring_index(HOST,':',1) ORDER BY COUNT(1) DESC"
        )

        for i in range(len(data)):
            if data[i]['db'] is None:
                data[i]['db'] = '空'

            if data[i]['Client_IP'] == '':
                data[i]['Client_IP'] = '空'

        # data2 = my_instance.query("SELECT USER, COUNT(*) as nums FROM information_schema.PROCESSLIST GROUP BY USER ORDER BY COUNT(*) DESC")
        # print(data)
        # print(data2)
        return mw.returnData(True, 'ok', data)

    # 快速找出没有主键的表
    def getFpkInfo(self, args):
        sid = args['sid']
        my_instance, err = self._connect(sid)
        if err:
            return err

        data = my_instance.query(
            """
            SELECT t.table_schema,
                   t.table_name
            FROM information_schema.tables t
            LEFT JOIN information_schema.key_column_usage k
                 ON t.table_schema = k.table_schema
                    AND t.table_name = k.table_name
                    AND k.constraint_name = 'PRIMARY'
            WHERE t.table_schema NOT IN ('mysql', 'information_schema', 'sys', 'performance_schema')
              AND k.constraint_name IS NULL
              AND t.table_type = 'BASE TABLE';
            """
        )
        return mw.returnData(True, 'ok', data)

    def getLockSql(self, args):
        sid = args['sid']
        my_instance, err = self._connect(sid)
        if err:
            return err

        data = my_instance.query(
            """
            SELECT 
                a.trx_id AS trx_id, 
                a.trx_state AS trx_state, 
                a.trx_started AS trx_started, 
                b.id AS processlist_id, 
                b.info AS info, 
                b.user AS user, 
                b.host AS host, 
                b.db AS db, 
                b.command AS command, 
                b.state AS state, 
                CONCAT('KILL QUERY ', b.id) AS sql_kill_blocking_query
            FROM 
                information_schema.INNODB_TRX a, 
                information_schema.PROCESSLIST b 
            WHERE 
                a.trx_mysql_thread_id = b.id
            ORDER BY 
                a.trx_started
            """
        )
        return mw.returnData(True, 'ok', data)

    def killLockPid(self, args):
        sid = args['sid']
        my_instance, err = self._connect(sid)
        if err:
            return err

        pid = args['pid']
        my_instance.execute('kill %s' % pid)
        return mw.returnData(True, '执行成功!')

    def killAllLock(self, args):
        sid = args['sid']
        my_instance, err = self._connect(sid)
        if err:
            return err

        data = self.getLockSql(args)
        if data['status']:
            pid_data = data['data']
            for x in pid_data:
                cmd = 'kill %s' % x['processlist_id']
                # print(cmd)
                my_instance.execute(cmd)
        return mw.returnData(True, '执行成功!')

    

    def getDeadlockInfo(self, args):
        sid = args['sid']
        my_instance, err = self._connect(sid)
        if err:
            return err

        data = my_instance.find("SHOW ENGINE INNODB STATUS")
        if data is not None:
            innodb_status = data['Status']
            deadlock_info = re.search(r"LATEST DETECTED DEADLOCK.*?WE ROLL BACK TRANSACTION\s+\(\d+\)", innodb_status, re.DOTALL)
            if deadlock_info is None:
                return mw.returnData(True, 'ok', '无锁表')
            return mw.returnData(True, 'ok', deadlock_info.group(0))
        return mw.returnData(True, 'ok', '无锁表')

    def getSlaveStatus(self, args):
        sid = args['sid']
        my_instance, err = self._connect(sid)
        if err:
            return err

        # MySQL 8.0.22+ 使用 SHOW REPLICA STATUS，MySQL 9.0 已移除 SHOW SLAVE STATUS
        # 注意: ORM.query 失败会直接抛异常,不会返回 Exception 对象
        try:
            slave_data = my_instance.query('SHOW REPLICA STATUS')
        except Exception:
            # 兼容 MySQL 8.0.22 以下及旧版 MariaDB
            try:
                slave_data = my_instance.query('SHOW SLAVE STATUS')
            except Exception as e:
                return mw.returnData(False, '获取主从状态失败: ' + str(e))
        if slave_data is None or len(slave_data) == 0:
            return mw.returnData(True, 'ok', '未开启从库!')

        slave_info = slave_data[0]
        # 兼容新旧字段名: MySQL 8.0.22+ 将 Slave_*/Seconds_Behind_Master 重命名为 Replica_*/Seconds_Behind_Source
        io_running = slave_info.get('Replica_IO_Running', slave_info.get('Slave_IO_Running'))
        sql_running = slave_info.get('Replica_SQL_Running', slave_info.get('Slave_SQL_Running'))
        seconds_behind = slave_info.get('Seconds_Behind_Source', slave_info.get('Seconds_Behind_Master'))

        msg = ''
        if slave_info.get('Auto_Position') != 1:
            msg += '你没有开启基于GTID全局事务ID复制，请确保CHANGE MASTER TO MASTER_AUTO_POSITION = 1.\n'


        if io_running == 'Yes' and sql_running == 'Yes':
            if seconds_behind == 0:
                msg = "同步正常，无延迟"
                return mw.returnData(True, 'ok', msg)
            else:
                return mw.returnData(True, 'ok', '同步正常，但有延迟，延迟时间为：%s' % seconds_behind)
        else:
            msg = '主从复制报错，请检查\nSlave_IO_Running状态值是：%s, |  Slave_SQL_Running状态值是：%s\nLast_Error错误信息是：%s\nLast_SQL_Error错误信息是：%s\n' \
            % (io_running, sql_running, slave_info.get('Last_Error'), slave_info.get('Last_SQL_Error'))
            try:
                error_data = my_instance.query('select LAST_ERROR_NUMBER,LAST_ERROR_MESSAGE,LAST_ERROR_TIMESTAMP from performance_schema.replication_applier_status_by_worker ORDER BY LAST_ERROR_TIMESTAMP desc limit 1')
            except Exception:
                error_data = None
            if not error_data:
                msg += 'MySQL Replication Health is NOT OK!'
                return mw.returnData(True, 'ok', msg)
            error_dict = error_data[0]
            msg += '错误号是：%s \n' % error_dict['LAST_ERROR_NUMBER']
            msg += '错误信息是：%s \n' % error_dict['LAST_ERROR_MESSAGE']
            msg += '报错时间是：%s \n' % error_dict['LAST_ERROR_TIMESTAMP']
            msg += 'MySQL Replication Health is NOT OK!'
            return mw.returnData(True, 'ok', msg)

    def getSlaveRuntime(self, args):
        sid = args['sid']
        my_instance, err = self._connect(sid)
        if err:
            return err

        try:
            slave_data = my_instance.query('SHOW REPLICA STATUS')
        except Exception:
            # 兼容 MySQL 8.0.22 以下及旧版 MariaDB
            try:
                slave_data = my_instance.query('SHOW SLAVE STATUS')
            except Exception as e:
                return mw.returnData(False, '获取主从状态失败: ' + str(e))
        if slave_data is None or len(slave_data) == 0:
            return mw.returnData(False, 'ok', '未开启从库!')
        # print(slave_data)

        time_unix = mw.getDate()
        data = {
            'time':time_unix,
            'data':slave_data[0],
        }
        return mw.returnData(True, 'ok', data)

    def _get_var_or_status(self, my_instance, sql, default=0):
        """执行一条 SHOW GLOBAL STATUS / VARIABLES LIKE 'xxx' 语句, 返回 Value 字段(int)."""
        try:
            row = my_instance.find(sql)
            if row is None:
                return default
            v = list(row.values())[-1] if isinstance(row, dict) else row[1]
            try:
                return int(v)
            except (ValueError, TypeError):
                try:
                    return float(v)
                except (ValueError, TypeError):
                    return default
        except Exception:
            return default

    def _get_var_str(self, my_instance, sql, default=''):
        try:
            row = my_instance.find(sql)
            if row is None:
                return default
            v = list(row.values())[-1] if isinstance(row, dict) else row[1]
            return str(v) if v is not None else default
        except Exception:
            return default

    def getHealth(self, args):
        """综合 MySQL 健康检查 + 可操作优化建议.
        返回结构化文本, 前端直接放到 textarea 展示."""
        sid = args['sid']
        my_instance, err = self._connect(sid)
        if err:
            return err

        lines = []
        issues = 0

        def section(title):
            lines.append('')
            lines.append('━━━ %s ━━━' % title)

        def ok(msg):
            lines.append('  ✅ ' + msg)

        def warn(msg):
            nonlocal issues
            issues += 1
            lines.append('  ⚠️  ' + msg)

        def info(msg):
            lines.append('  ℹ️   ' + msg)

        # ---------- 0. 基础信息 ----------
        section('基础信息')
        ver = self._get_var_str(my_instance, "SELECT @@version")
        uptime = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Uptime'")
        pfs = self._get_var_or_status(my_instance, "SELECT @@performance_schema")
        # 解析版本号: 5.7.39-log / 8.0.36-log / 8.4.2 / 11.4.4-MariaDB
        _m = re.match(r'^(\d+)\.(\d+)', ver)
        _major = int(_m.group(1)) if _m else 0
        _minor = int(_m.group(2)) if _m else 0
        _is_mariadb = 'mariadb' in ver.lower()
        if uptime >= 86400:
            uptime_txt = '%d天%02d:%02d:%02d' % (
                uptime // 86400, (uptime % 86400) // 3600,
                (uptime % 3600) // 60, uptime % 60)
        elif uptime >= 3600:
            uptime_txt = '%d小时%02d分钟' % (uptime // 3600, (uptime % 3600) // 60)
        else:
            uptime_txt = '%d分钟' % max(uptime // 60, 1)
        info('版本: %s' % ver)
        info('已运行: %s' % uptime_txt)
        if pfs:
            ok('performance_schema 已开启 (可识别热点 SQL / 冗余索引)')
        else:
            warn('performance_schema 未开启, 建议 my.cnf 里加 performance_schema=1 并重启')

        # ---------- 1. 连接数水位 ----------
        section('连接数 / 线程缓存')
        tc = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Threads_connected'")
        mc = self._get_var_or_status(my_instance, "SHOW GLOBAL VARIABLES LIKE 'max_connections'")
        tc_rate = (tc / mc * 100) if mc else 0
        info('当前连接 %d / max_connections=%d (%.1f%%)' % (tc, mc, tc_rate))
        if tc_rate >= 80:
            warn('连接数已接近上限, 应用层可能出现 "too many connections" 拒绝')
            warn('建议: 1) 应用端检查连接泄露  2) max_connections 适度上调  3) 检查 thread_cache_size')
        elif tc_rate >= 50:
            warn('连接数水位偏高, 建议持续关注')
        else:
            ok('连接数水位正常')

        tc_total = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Threads_created'")
        conn_total = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Connections'")
        t_created_rate = (tc_total / conn_total * 100) if conn_total else 0
        info('Threads_created=%d / Connections=%d (%.2f%%)' % (tc_total, conn_total, t_created_rate))
        if t_created_rate >= 10:
            warn('Thread 创建比例偏高, thread_cache_size 可能过小 (每个新连接都创建新线程)')
            warn('建议: my.cnf 里设置 thread_cache_size = %d (CPU 核数的 2~4 倍)' % (
                os.cpu_count() * 3 if os.cpu_count() else 16))
        else:
            ok('线程缓存命中率正常')

        ac = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Aborted_connects'")
        if ac > 0:
            warn('Aborted_connects=%d (客户端认证失败 / 超时 / 连接被意外关闭)' % ac)
            warn('建议: 排查应用端账号密码、wait_timeout 配置、网络抖动')

        # ---------- 2. InnoDB Buffer Pool ----------
        section('InnoDB Buffer Pool')
        br = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_reads'")
        brr = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_read_requests'")
        hit = (1 - br / brr) * 100 if brr else 100
        info('命中率: %.2f%% (物理读 %d / 总请求 %d)' % (hit, br, brr))

        bpsize = self._get_var_or_status(my_instance, "SHOW GLOBAL VARIABLES LIKE 'innodb_buffer_pool_size'")
        bpsize_mb = bpsize / 1024 / 1024

        import psutil
        try:
            total_mem_mb = psutil.virtual_memory().total / 1024 / 1024
            bpsize_pct = bpsize / (total_mem_mb * 1024 * 1024) * 100
            info('innodb_buffer_pool_size=%.0fMB (%.1f%% of total memory %.0fMB)' % (bpsize_mb, bpsize_pct, total_mem_mb))
        except Exception:
            bpsize_pct = -1
            info('innodb_buffer_pool_size=%.0fMB' % bpsize_mb)

        if hit >= 99:
            ok('命中率极佳')
        elif hit >= 95:
            ok('命中率良好, 可维持现状')
        else:
            warn('命中率偏低 (%.2f%%), 磁盘读多会拖慢响应' % hit)
            if bpsize_pct >= 0 and bpsize_pct < 50:
                warn('建议调大 innodb_buffer_pool_size 到物理内存的 50~75%% (当前 %.0fMB, 可调到 %.0fMB~%.0fMB)' % (
                    bpsize_mb, total_mem_mb * 0.5, total_mem_mb * 0.75))
            else:
                warn('建议调大 innodb_buffer_pool_size, 或检查是否有大量全表扫描')

        ilw = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Innodb_log_waits'")
        if ilw > 0:
            warn('Innodb_log_waits=%d (Redo Log buffer 写满导致的等待)' % ilw)
            warn('建议: 增大 innodb_log_buffer_size (默认 16MB, 可尝试 64MB), 或增大 innodb_redo_log_capacity (MySQL 8.0)')

        rlw = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Innodb_row_lock_waits'")
        rla = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Innodb_row_lock_time_avg'")
        rlt = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Innodb_row_lock_time'")
        if rlw > 0:
            warn('锁等待累计: Innodb_row_lock_waits=%d, 总等待=%.0fms, avg=%.0fms' % (rlw, rlt, rla))
            warn('建议: 应用层排查热点行 (短事务、合理索引、避免长 SELECT ... FOR UPDATE)')
        else:
            ok('行锁等待为 0')

        # 死锁: MySQL 8.0+ 有 Innodb_deadlocks, MariaDB 有 Innodb_deadlock_detect, MySQL 5.7 无全局计数
        deadlocks = -1
        if _is_mariadb:
            deadlocks = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Innodb_deadlock_detect'")
        elif _major >= 8:
            deadlocks = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Innodb_deadlocks'")
        if deadlocks < 0:
            info('(MySQL %d.%d 无全局死锁计数器, 可用 SHOW ENGINE INNODB STATUS 查最近死锁)' % (_major, _minor))
        elif deadlocks > 0:
            warn('Innodb 死锁累计 %d 次, 应用层有事务并发冲突' % deadlocks)
            warn('建议: SHOW ENGINE INNODB STATUS 查最近死锁, 应用按固定顺序获取锁、缩短事务、加 retry 逻辑')
        else:
            ok('未检测到死锁')

        # ---------- 2.5 文件描述符 / 表缓存 ----------
        section('文件与表缓存')
        ofl = self._get_var_or_status(my_instance, "SHOW GLOBAL VARIABLES LIKE 'open_files_limit'")
        of = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Opened_files'")
        opn = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Open_files'")
        opn_pct = (opn / ofl * 100) if ofl else 0
        info('open_files_limit=%d, Open_files=%d, Opened_files(total)=%d' % (ofl, opn, of))
        if opn_pct >= 80:
            warn('当前打开文件数已达 open_files_limit 的 %.1f%%, 可能无法再打开新表 / 日志' % opn_pct)
            warn('my.cnf: open_files_limit=65535 (需同时在 OS 层 ulimit -n 调大)')
        else:
            ok('文件描述符水位正常 (%.1f%%)' % opn_pct)

        toc = self._get_var_or_status(my_instance, "SHOW GLOBAL VARIABLES LIKE 'table_open_cache'")
        ot = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Opened_tables'")
        oft = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Open_tables'")
        table_hit = ((1 - ot / (ot + oft)) * 100) if (ot + oft) else 100
        info('table_open_cache=%d, Open_tables=%d, Opened_tables(total)=%d (命中率 %.2f%%)' % (
            toc, oft, ot, table_hit))
        if ot > 0 and table_hit < 85:
            warn('表缓存命中率 %.1f%% 偏低, 每次查询都重新打开 .frm 文件' % table_hit)
            warn('my.cnf: table_open_cache = %d (CPU 核数 × 2048 或更大)' % toc)

        # ---------- 2.6 字符集 ----------
        section('字符集 / 排序规则')
        cs = self._get_var_str(my_instance, "SHOW GLOBAL VARIABLES LIKE 'character_set_server'")
        coll = self._get_var_str(my_instance, "SHOW GLOBAL VARIABLES LIKE 'collation_server'")
        info('character_set_server=%s, collation_server=%s' % (cs, coll))
        if cs.lower() == 'utf8mb4':
            ok('server 字符集 utf8mb4 (完整 Unicode, 含 emoji)')
        else:
            warn('server 字符集是 %s, 建议 my.cnf 改为 utf8mb4 以支持完整 emoji 和 4 字节汉字' % cs)
            warn('my.cnf: character-set-server=utf8mb4, collation-server=utf8mb4_unicode_ci')
        # 业务表是否有非 utf8mb4
        try:
            non_utf8mb4 = my_instance.query(
                "SELECT table_schema, table_name, table_collation FROM information_schema.tables "
                "WHERE table_schema NOT IN ('mysql','information_schema','performance_schema','sys') "
                "AND table_collation LIKE 'utf8%' AND table_collation NOT LIKE 'utf8mb4%' LIMIT 20"
            )
            if non_utf8mb4:
                warn('发现 %d 张业务表仍在用 utf8 (3 字节, 存不下 emoji)' % len(non_utf8mb4))
                for r in non_utf8mb4[:5]:
                    warn('  %s.%s  collation=%s' % (r['table_schema'], r['table_name'], r['table_collation']))
                warn('升级方式: ALTER TABLE t CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        except Exception:
            pass

        # ---------- 2.7 Binlog / 持久化安全 ----------
        section('Binlog / Durability')
        sync_b = self._get_var_or_status(my_instance, "SHOW GLOBAL VARIABLES LIKE 'sync_binlog'")
        flc = self._get_var_or_status(my_instance, "SHOW GLOBAL VARIABLES LIKE 'innodb_flush_log_at_trx_commit'")
        bl_fmt = self._get_var_str(my_instance, "SHOW GLOBAL VARIABLES LIKE 'binlog_format'")
        log_bin = self._get_var_str(my_instance, "SHOW GLOBAL VARIABLES LIKE 'log_bin'")
        gtid = self._get_var_str(my_instance, "SHOW GLOBAL VARIABLES LIKE 'gtid_mode'")
        info('sync_binlog=%d, innodb_flush_log_at_trx_commit=%d' % (sync_b, flc))
        if sync_b == 1 and flc == 1:
            ok('双 1 组合, ACID 安全 (每次事务都 fsync, 性能略低)')
        elif sync_b == 0 and flc == 2:
            warn('sync_binlog=0 + innodb_flush_log_at_trx_commit=2, 崩溃时可能丢最后 ~1s 的事务')
            warn('单机开发环境可接受, 生产建议至少 innodb_flush_log_at_trx_commit=1 或 sync_binlog=1')
        else:
            info('sync_binlog=%d / innodb_flush_log_at_trx_commit=%d, 请按业务可接受的数据丢失窗口调整' % (sync_b, flc))

        info('binlog_format=%s, log_bin=%s, gtid_mode=%s' % (bl_fmt, log_bin, gtid))
        if log_bin.lower() != 'on':
            warn('log_bin 未开启, 无法做 point-in-time recovery / 主从 / binlog 审计')
            warn('my.cnf: log_bin=mysql-bin, binlog_format=ROW')
        elif bl_fmt == 'STATEMENT':
            warn('binlog_format=STATEMENT, 非确定性函数 (NOW/RAND/LIMIT) 可能导致主从不一致')
            warn('my.cnf: binlog_format=ROW (或 MIXED)')
        if gtid.lower() == 'off':
            warn('gtid_mode=OFF, 主从切换 / 重建副本操作较繁琐, 建议开启 GTID')
            warn('my.cnf: gtid_mode=ON, enforce_gtid_consistency=ON')
        # Binlog 过期策略: MySQL 8.0+ / MariaDB 10.6+ 用 binlog_expire_logs_seconds, 否则 expire_logs_days
        try:
            use_seconds = (_major >= 8 and not _is_mariadb) or (_is_mariadb and _major >= 10 and _minor >= 6)
            if use_seconds:
                bex = self._get_var_str(my_instance, "SHOW GLOBAL VARIABLES LIKE 'binlog_expire_logs_seconds'")
                info('binlog_expire_logs_seconds=%s' % bex)
                if not bex or bex in ('0', ''):
                    warn('binlog 未设置过期策略 (binlog_expire_logs_seconds=0), 长期运行会撑满磁盘')
                    warn('my.cnf: binlog_expire_logs_seconds=604800 (保留 7 天)')
                else:
                    ok('binlog 过期策略: binlog_expire_logs_seconds=%s' % bex)
            else:
                eld = self._get_var_or_status(my_instance, "SHOW GLOBAL VARIABLES LIKE 'expire_logs_days'")
                info('expire_logs_days=%d' % eld)
                if eld == 0:
                    warn('binlog 永不过期 (expire_logs_days=0), 长期运行会撑满磁盘')
                    warn('my.cnf: expire_logs_days=7 (保留 7 天)')
                else:
                    ok('binlog 过期策略: expire_logs_days=%d' % eld)
        except Exception as ex:
            info('(binlog 过期策略检查异常: %s)' % str(ex))

        # ---------- 3. 慢查询 ----------
        section('慢查询 / SQL 健康')
        slow_total = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Slow_queries'")
        sql_log = self._get_var_str(my_instance, "SHOW GLOBAL VARIABLES LIKE 'slow_query_log'")
        lqt = self._get_var_or_status(my_instance, "SHOW GLOBAL VARIABLES LIKE 'long_query_time'")
        info('Slow_queries=%d, slow_query_log=%s, long_query_time=%.1fs' % (slow_total, sql_log, lqt))

        if sql_log.lower() == 'on' and lqt <= 2:
            ok('慢查询已开启且阈值合理 (%.1fs)' % lqt)
        elif sql_log.lower() == 'on':
            warn('慢查询已开启但 long_query_time=%.1fs 偏高, 建议调低到 1~2s' % lqt)
            warn('my.cnf: long_query_time=2, slow_query_log=1')
        else:
            warn('slow_query_log 未开启, 无法定位慢 SQL')
            warn('my.cnf: slow_query_log=1, long_query_time=2, log_queries_not_using_indexes=1')

        # 表级 SQL 健康: 冗余索引
        try:
            red = my_instance.query(
                "select table_schema,table_name,redundant_index_name,sql_drop_index "
                "from sys.schema_redundant_indexes limit 50"
            )
            if red and len(red) > 0:
                warn('发现 %d 组冗余索引: (取前 3 组)' % len(red))
                for r in red[:3]:
                    warn('  %s.%s → %s' % (r['table_schema'], r['table_name'], r['redundant_index_name']))
                    warn('  可执行: %s' % r['sql_drop_index'])
            else:
                ok('未发现冗余索引')
        except Exception:
            ok('(当前环境无法检测冗余索引, 需要 MySQL 5.7+ sys schema 或 MariaDB 10.1+)')

        # 未使用索引 (performance_schema 必须开启, sys.schema_unused_indexes 才有数据)
        if pfs:
            try:
                unused = my_instance.query(
                    "SELECT object_schema, object_name, index_name "
                    "FROM sys.schema_unused_indexes LIMIT 50"
                )
                if unused and len(unused) > 0:
                    warn('发现 %d 个从未被查询命中的索引 (取前 3 个):' % len(unused))
                    for r in unused[:3]:
                        warn('  %s.%s → %s (可考虑 DROP, 节省写入开销)' % (
                            r['object_schema'], r['object_name'], r['index_name']))
                else:
                    ok('索引都在被使用 (或 performance_schema 采集尚未覆盖足够查询)')
            except Exception:
                pass

        # 无主键表
        try:
            nopk = my_instance.query(
                "SELECT t.table_schema, t.table_name FROM information_schema.tables t "
                "LEFT JOIN information_schema.key_column_usage k "
                "ON t.table_schema=k.table_schema AND t.table_name=k.table_name AND k.constraint_name='PRIMARY' "
                "WHERE t.table_schema NOT IN ('mysql','information_schema','sys','performance_schema') "
                "AND k.constraint_name IS NULL AND t.table_type='BASE TABLE'"
            )
            if nopk and len(nopk) > 0:
                warn('发现 %d 张无主键表 (全表扫描 + Replication 都会有问题)' % len(nopk))
                for r in nopk[:5]:
                    warn('  %s.%s' % (r['table_schema'], r['table_name']))
            else:
                ok('所有业务表都有主键')
        except Exception:
            pass

        # ---------- 4. 磁盘 / Tmp 表 ----------
        section('磁盘与 Tmp 表')
        ctd = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Created_tmp_disk_tables'")
        ctm = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Created_tmp_tables'")
        ctd_pct = (ctd / ctm * 100) if ctm else 0
        info('Created_tmp_disk_tables=%d / Created_tmp_tables=%d (%.2f%%)' % (ctd, ctm, ctd_pct))
        if ctd_pct >= 20:
            warn('有 %.1f%% 的临时表落盘, 排序/分组查询性能会差' % ctd_pct)
            warn('建议: tmp_table_size / max_heap_table_size 调大 (例如 64MB ~ 256MB)')
            warn('my.cnf: tmp_table_size=128M, max_heap_table_size=128M')
        else:
            ok('Tmp 表几乎不落盘 (%.2f%%)' % ctd_pct)

        bcd = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Binlog_cache_disk_use'")
        bcu = self._get_var_or_status(my_instance, "SHOW GLOBAL STATUS LIKE 'Binlog_cache_use'")
        if bcu > 0:
            bcd_pct = bcd / bcu * 100
            info('Binlog_cache_disk_use=%d / Binlog_cache_use=%d (%.2f%%)' % (bcd, bcu, bcd_pct))
            if bcd_pct >= 10:
                warn('Binlog 缓存落盘比例 %.1f%% 偏高, 较大事务会写磁盘' % bcd_pct)
                warn('建议: my.cnf 调大 binlog_cache_size=2M / max_binlog_size=512M')
            else:
                ok('Binlog 缓存几乎不落盘')
        else:
            info('Binlog 无事务压力 (Binlog_cache_use=0)')

        # ---------- 5. 大表 / AUTO_INCREMENT 余量 ----------
        section('大表 / AUTO_INCREMENT 余量')
        try:
            big_tables = my_instance.query(
                """SELECT t.table_schema, t.table_name, t.table_rows,
                          ROUND((t.data_length + t.index_length)/1024/1024, 2) AS total_mb,
                          t.auto_increment, c.data_type,
                          LOCATE('unsigned', c.column_type) > 0 AS is_unsigned
                   FROM information_schema.tables t
                   LEFT JOIN information_schema.columns c
                     ON t.table_schema=c.table_schema AND t.table_name=c.table_name AND c.extra='auto_increment'
                   WHERE t.table_schema NOT IN ('mysql','information_schema','performance_schema','sys')
                     AND t.table_type = 'BASE TABLE'
                   ORDER BY t.data_length + t.index_length DESC
                   LIMIT 500"""
            )
            if big_tables:
                big = [r for r in big_tables if r['total_mb'] is not None and r['total_mb'] >= 100]
                if big:
                    warn('共 %d 张 ≥100MB 的大表 (最大 %.1fMB):' % (len(big), max(x['total_mb'] for x in big)))
                    for r in big[:3]:
                        warn('  %s.%s  [%.1fMB, rows=%s]' % (
                            r['table_schema'], r['table_name'],
                            r['total_mb'], r['table_rows'] or '-'))
                    warn('建议: 大表定期 OPTIMIZE TABLE / 按日期分表 / 冷热分离')
                else:
                    ok('业务表都 <100MB, 无需要重点关注的大表')

                # 全表 AUTO_INCREMENT 余量: 按 data_type + signed/unsigned 算真实上限
                type_max = {
                    'tinyint':    (127, 255),
                    'smallint':   (32767, 65535),
                    'mediumint':  (8388607, 16777215),
                    'int':        (2147483647, 4294967295),
                    'integer':    (2147483647, 4294967295),
                    'bigint':     (9223372036854775807, 18446744073709551615),
                }
                ai_risks = []
                for r in big_tables:
                    if not r.get('auto_increment'):
                        continue
                    dt = (r.get('data_type') or '').lower()
                    is_unsigned = bool(r.get('is_unsigned'))
                    lim = type_max.get(dt)
                    if lim is None:
                        continue
                    mx = lim[1] if is_unsigned else lim[0]
                    ai = int(r['auto_increment'])
                    pct_used = ai / mx * 100
                    if pct_used >= 50:
                        ai_risks.append((pct_used, r, mx))
                if ai_risks:
                    ai_risks.sort(reverse=True)
                    warn('发现 %d 张表 AUTO_INCREMENT 已用 ≥50%%, 有耗尽风险 (取前 3 张):' % len(ai_risks))
                    for pct, r, mx in ai_risks[:3]:
                        warn('  %s.%s 当前 %d / max %s (%.1f%%)' % (
                            r['table_schema'], r['table_name'],
                            r['auto_increment'], mx, pct))
                else:
                    ok('AUTO_INCREMENT 余量都在 50% 以上, 无耗尽风险')
        except Exception:
            pass

        # ---------- 6. 账户安全 ----------
        section('账户安全')
        try:
            users = my_instance.query("SELECT user, host FROM mysql.user")
            root_remote = [u for u in users if u['user'] == 'root' and u['host'] not in ('localhost', '127.0.0.1', '::1')]
            anonymous = [u for u in users if u['user'] == '']
            system_users = ('mysql.session', 'mysql.sys', 'root', 'localhost')
            weak_host_users = [u for u in users if u['host'] == '%' and u['user'] not in system_users]
            if root_remote:
                warn('root 账号允许远程登录: %s (可被爆破)' % ', '.join(u['host'] for u in root_remote))
                warn('建议: DELETE FROM mysql.user WHERE user="root" AND host NOT IN ("localhost","127.0.0.1","::1"); FLUSH PRIVILEGES;')
            else:
                ok('root 账号仅限本机登录')
            if anonymous:
                warn('存在匿名账号 user="", 建议删除')
            else:
                ok('无匿名账号')
            if weak_host_users:
                info('以下账号 host="%%" (允许任意来源, 请确保密码强度):')
                for u in weak_host_users[:5]:
                    info('  user=%s host=%%' % u['user'])
        except Exception as ex:
            info('(账户安全检查异常: %s)' % str(ex))

        # ---------- 7. 主从 ----------
        section('主从复制')
        try:
            slave_data = None
            try:
                slave_data = my_instance.query('SHOW REPLICA STATUS')
            except Exception:
                try:
                    slave_data = my_instance.query('SHOW SLAVE STATUS')
                except Exception:
                    pass
            if slave_data and len(slave_data) > 0:
                s = slave_data[0]
                io_running = s.get('Replica_IO_Running', s.get('Slave_IO_Running'))
                sql_running = s.get('Replica_SQL_Running', s.get('Slave_SQL_Running'))
                sec_behind = s.get('Seconds_Behind_Source', s.get('Seconds_Behind_Master'))
                if io_running == 'Yes' and sql_running == 'Yes':
                    if sec_behind == 0:
                        ok('主从复制正常, 无延迟')
                    else:
                        warn('主从复制正常但延迟 %s 秒' % sec_behind)
                else:
                    warn('主从异常! IO=%s, SQL=%s, Last_Error=%s' % (
                        io_running, sql_running,
                        s.get('Last_Error') or s.get('Last_IO_Error') or '无'))
            else:
                ok('当前实例不是从库, 未开启主从复制')
        except Exception as ex:
            info('(检查主从时出现异常: %s)' % str(ex))

        # ---------- 总结 ----------
        lines.append('')
        lines.append('━━━ 总结 ━━━')
        if issues == 0:
            lines.append('  🎉 本次检查共发现 0 个可优化点, MySQL 健康状况良好!')
        elif issues <= 3:
            lines.append('  📌 本次检查共发现 %d 个可优化点 (建议逐项处理)' % issues)
        else:
            lines.append('  🚨 本次检查共发现 %d 个可优化点, 建议优先处理连接数/Buffer Pool/主从等核心项' % issues)
        lines.append('  ℹ️   每项建议 my.cnf 修改后需重启 MySQL 或动态执行 SET GLOBAL, 具体参数请查阅官方文档')

        return mw.returnData(True, 'ok', '\n'.join(lines))

# ---------------------------------- run ----------------------------------

def get_server_list(args):
    t = nosqlMySQLCtr()
    return t.getServerList(args)

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

# 删除重复或冗余的索引
def redundant_indexes_cmd(args):
    t = nosqlMySQLCtr()
    return t.redundantIndexesCmd(args)

# 统计库里每个表的大小
def get_table_info(args):
    t = nosqlMySQLCtr()
    return t.getTableInfo(args)

# 查看应用端IP连接数总和
def get_conn_count(args):
    t = nosqlMySQLCtr()
    return t.getConnCount(args)

# 快速找出没有主键的表
def get_fpk_info(args):
    t = nosqlMySQLCtr()
    return t.getFpkInfo(args)

# 查看当前锁阻塞的SQL
def get_lock_sql(args):
    t = nosqlMySQLCtr()
    return t.getLockSql(args)

# KILL阻塞SQL
def kill_lock_pid(args):
    t = nosqlMySQLCtr()
    return t.killLockPid(args)

# KILL阻塞SQL
def kill_all_lock(args):
    t = nosqlMySQLCtr()
    return t.killAllLock(args)

# 查看死锁信息
def get_deadlock_info(args):
    t = nosqlMySQLCtr()
    return t.getDeadlockInfo(args)

# 查看主从复制信息
def get_slave_status(args):
    t = nosqlMySQLCtr()
    return t.getSlaveStatus(args)

def get_slave_runtime(args):
    t = nosqlMySQLCtr()
    return t.getSlaveRuntime(args)

# MySQL 健康检查
def get_health(args):
    t = nosqlMySQLCtr()
    return t.getHealth(args)






# 测试
def test(args):
    sid = args['sid']
    t = nosqlMySQLCtr()
    print(t.get_options())
    print("test")
    return 'ok'