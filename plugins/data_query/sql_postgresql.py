# coding:utf-8

import sys
import os
import re
import json
import time

import psycopg2
import psycopg2.extras

web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw

PG_SYSTEM_SCHEMAS = ('pg_catalog', 'information_schema', 'pg_toast')


def getPluginName():
    return 'postgresql'


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getConf():
    return getServerDir() + '/data/postgresql.conf'


def isInstalled():
    return os.path.exists(getConf())


def getPort():
    content = mw.readFile(getConf())
    if content:
        tmp = re.search(r'^[#\s]*port\s*=\s*(\d+)', content, re.M)
        if tmp:
            return int(tmp.groups()[0])
    return 5432


def getSocketDir():
    sock_name = '.s.PGSQL.' + str(getPort())
    for sock_dir in ['/tmp', getServerDir()]:
        if os.path.exists(sock_dir + '/' + sock_name):
            return sock_dir
    return ''


def quoteIdent(name):
    return '"' + str(name).replace('"', '""') + '"'


def quoteTable(name):
    return '.'.join(quoteIdent(x) for x in str(name).split('.'))


def fmtValue(value):
    if value is None:
        return None
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, default=str)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value).hex()
    if isinstance(value, (int, float, str, bool)):
        return value
    return str(value)


def fmtRows(rows):
    ret = []
    for row in rows:
        item = {}
        for k in row:
            item[k] = fmtValue(row[k])
        ret.append(item)
    return ret


class PgClient:

    def __init__(self, database='postgres'):
        self.database = database
        self.status = None
        self.error = None
        self.conn = None

    def connect(self):
        if not isInstalled():
            self.status = 'not_installed'
            return False

        try:
            host = getSocketDir()
            if host == '':
                host = '127.0.0.1'

            self.conn = psycopg2.connect(database=self.database,
                                         user='postgres',
                                         host=host,
                                         port=getPort(),
                                         connect_timeout=3)
            self.conn.autocommit = True
            return True
        except psycopg2.OperationalError as e:
            msg = str(e).strip()
            if 'does not exist' in msg:
                self.status = 'db_not_found'
            elif 'authentication' in msg or 'password' in msg:
                self.status = 'auth_error'
            else:
                self.status = 'not_running'
            self.error = msg
        except Exception as e:
            self.status = 'not_running'
            self.error = str(e)
        return False

    def query(self, sql, params=()):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            # 无参数时不能传空 tuple，否则 SQL 里的 % 会被当作占位符
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            rows = cur.fetchall()
            return [dict(x) for x in rows]
        finally:
            cur.close()

    def one(self, sql, params=()):
        rows = self.query(sql, params)
        if len(rows) == 0:
            return None
        return rows[0]

    def execute(self, sql, params=()):
        cur = self.conn.cursor()
        try:
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            return cur.rowcount
        finally:
            cur.close()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None


def openClient(args, database='postgres'):
    client = PgClient(database)
    if client.connect():
        return client, None

    if client.status == 'not_installed':
        msg = '未安装'
    elif client.status == 'not_running':
        msg = '未启动'
    elif client.status == 'db_not_found':
        msg = '数据库不存在'
    elif client.status == 'auth_error':
        msg = '连接失败，请检查数据库认证配置'
    else:
        msg = client.error or '连接失败'
    return None, mw.returnData(False, msg)


# 服务器列表
def get_server_list(args):
    data = []
    if isInstalled():
        data.append({'name': '本地服务器', 'val': 'postgresql'})
    return mw.returnData(True, 'ok', data)


# 数据库列表
def get_db_list(args):
    client, err = openClient(args)
    if err:
        return err

    try:
        rows = client.query("select datname from pg_database where datistemplate = false order by datname")
        result = {'list': [x['datname'] for x in rows]}
        return mw.returnData(True, 'ok', result)
    finally:
        client.close()


# 数据表列表
def get_table_list(args):
    db = args.get('db', '')
    client, err = openClient(args, db)
    if err:
        return err

    try:
        sql = """
            select n.nspname as schemaname, c.relname as tablename
            from pg_class c
            join pg_namespace n on n.oid = c.relnamespace
            where c.relkind in ('r', 'p', 'v', 'm', 'f')
              and n.nspname not in ('pg_catalog', 'information_schema', 'pg_toast')
              and n.nspname not like 'pg_temp%'
            order by n.nspname, c.relname
        """
        rows = client.query(sql)

        table_list = []
        for x in rows:
            if x['schemaname'] == 'public':
                table_list.append(x['tablename'])
            else:
                table_list.append(x['schemaname'] + '.' + x['tablename'])

        result = {'list': table_list}
        return mw.returnData(True, 'ok', result)
    finally:
        client.close()


# 数据列表
def get_data_list(args):
    db = args.get('db', '')
    table = args.get('table', '')

    p = 1
    size = 10
    if 'p' in args:
        p = int(args['p'])
    if 'size' in args:
        size = int(args['size'])
    start_index = (p - 1) * size

    if table == '':
        page_args = {}
        page_args['count'] = 0
        page_args['tojs'] = 'pgGetDataList'
        page_args['p'] = 1
        page_args['row'] = size

        rdata = {}
        rdata['page'] = mw.getPage(page_args)
        rdata['list'] = []
        rdata['count'] = 0
        return mw.returnData(True, 'ok', rdata)

    where_sql = ''
    where_params = []
    args_where = {}
    if 'where' in args and isinstance(args['where'], dict):
        args_where = args['where']

    field = args_where.get('field', '')
    if field and field != '0':
        field_sql = quoteIdent(field)
        value = str(args_where.get('value', ''))
        if 'id' in field.lower():
            where_sql = ' where ' + field_sql + ' = %s'
            where_params.append(value)
        else:
            where_sql = ' where ' + field_sql + ' like %s'
            where_params.append('%' + value + '%')

    client, err = openClient(args, db)
    if err:
        return err

    try:
        try:
            sql = 'select count(*) as num from ' + quoteTable(table) + where_sql
            count_row = client.one(sql, tuple(where_params))
            count = int(count_row['num'])

            sql = 'select * from ' + quoteTable(table) + where_sql + ' limit %s offset %s'
            params = tuple(where_params) + (size, start_index)
            rows = client.query(sql, params)
            rows = fmtRows(rows)
        except psycopg2.errors.UndefinedTable:
            return mw.returnData(False, '数据表不存在：' + table)
        except psycopg2.errors.UndefinedColumn:
            return mw.returnData(False, '字段不存在，请刷新后重试')
        except psycopg2.Error as e:
            return mw.returnData(False, '查询失败：' + str(e).strip())

        page_args = {}
        page_args['count'] = count
        page_args['tojs'] = 'pgGetDataList'
        page_args['p'] = p
        page_args['row'] = size

        rdata = {}
        rdata['page'] = mw.getPage(page_args)
        rdata['list'] = rows
        rdata['count'] = count
        rdata['soso_field'] = ''
        if field and field != '0':
            rdata['soso_field'] = field

        return mw.returnData(True, 'ok', rdata)
    finally:
        client.close()


# 进程列表
def get_proccess_list(args):
    client, err = openClient(args)
    if err:
        return err

    try:
        sql = """
            select pid, usename as "user", datname as db,
                   coalesce(host(client_addr), '本地') as host,
                   application_name as command, state, query as info,
                   backend_start, xact_start, query_start,
                   wait_event_type, wait_event
            from pg_stat_activity
            where pid <> pg_backend_pid()
              and backend_type = 'client backend'
            order by pid
        """
        rows = fmtRows(client.query(sql))
        result = {'list': rows}
        return mw.returnData(True, 'ok', result)
    finally:
        client.close()


# 状态列表
def get_status_list(args):
    client, err = openClient(args)
    if err:
        return err

    try:
        sql = """
            select name, setting, coalesce(unit, '') as unit,
                   category, short_desc
            from pg_settings
            order by name
        """
        rows = fmtRows(client.query(sql))
        result = {'list': rows}
        return mw.returnData(True, 'ok', result)
    finally:
        client.close()


# 统计列表
def get_stats_list(args):
    client, err = openClient(args)
    if err:
        return err

    try:
        sql = """
            select datname as db,
                   numbackends as conn,
                   xact_commit as commit, xact_rollback as rollback,
                   blks_read, blks_hit,
                   tup_returned, tup_fetched, tup_inserted, tup_updated, tup_deleted,
                   deadlocks, conflicts, temp_files, temp_bytes,
                   round(100.0 * blks_hit / nullif(blks_hit + blks_read, 0), 2) as cache_hit_ratio
            from pg_stat_database
            where datname is not null
            order by datname
        """
        rows = fmtRows(client.query(sql))
        result = {'list': rows}
        return mw.returnData(True, 'ok', result)
    finally:
        client.close()


def _dbStatSnapshot(client):
    sql = """
        select coalesce(sum(tup_fetched), 0) as fetched,
               coalesce(sum(tup_inserted), 0) as inserted,
               coalesce(sum(tup_updated), 0) as updated,
               coalesce(sum(tup_deleted), 0) as deleted,
               coalesce(sum(xact_commit), 0) as commits
        from pg_stat_database
    """
    row = client.one(sql)
    return {
        'fetched': int(row['fetched']),
        'inserted': int(row['inserted']),
        'updated': int(row['updated']),
        'deleted': int(row['deleted']),
        'commits': int(row['commits']),
    }


# QPS/TPS 指标
def get_net_list(args):
    from datetime import datetime

    client, err = openClient(args)
    if err:
        return err

    try:
        row1 = _dbStatSnapshot(client)
        time.sleep(1)
        row2 = _dbStatSnapshot(client)

        max_conn = client.one("select setting from pg_settings where name = 'max_connections'")
        conn_row = client.one("select count(*) as num from pg_stat_activity where backend_type = 'client backend'")

        row = {}
        row['current_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row['select'] = row2['fetched'] - row1['fetched']
        row['insert'] = row2['inserted'] - row1['inserted']
        row['update'] = row2['updated'] - row1['updated']
        row['delete'] = row2['deleted'] - row1['deleted']
        row['conn'] = conn_row['num']
        row['max_conn'] = max_conn['setting']
        # PostgreSQL 的 pg_stat 不提供网络字节计数器
        row['recv_mbps'] = '-'
        row['send_mbps'] = '-'

        rdata = []
        rdata.append(row)
        return mw.returnData(True, 'ok', rdata)
    finally:
        client.close()


# 查询执行次数最频繁的前N条SQL语句
def get_topn_list(args):
    client, err = openClient(args)
    if err:
        return err

    try:
        avail = client.one("""
            select default_version, installed_version
            from pg_available_extensions
            where name = 'pg_stat_statements'
        """)
        if avail is None:
            return mw.returnData(False, '当前 PostgreSQL 未提供 pg_stat_statements 扩展（缺少 contrib 模块），无法使用该功能。')

        ext = client.one("select to_regclass('pg_stat_statements') as v")
        if ext is None or ext['v'] is None:
            preload = client.one("select setting from pg_settings where name = 'shared_preload_libraries'")
            libs = (preload or {}).get('setting', '') or ''
            msg = "pg_stat_statements 扩展已可用，但尚未启用。\n"
            if 'pg_stat_statements' not in libs:
                msg += "1. 在 postgresql.conf 添加 shared_preload_libraries = 'pg_stat_statements'\n"
                msg += "2. 重启 PostgreSQL 服务\n"
                msg += "3. 在当前数据库执行 CREATE EXTENSION pg_stat_statements;"
            else:
                msg += "在当前数据库执行 CREATE EXTENSION pg_stat_statements;"
            return mw.returnData(False, msg)

        version_num = int(client.one('show server_version_num')['server_version_num'])
        if version_num >= 130000:
            total_col = 'total_exec_time'
            max_col = 'max_exec_time'
            mean_col = 'mean_exec_time'
        else:
            total_col = 'total_time'
            max_col = 'max_time'
            mean_col = 'mean_time'

        sql = """
            select s.query,
                   coalesce(d.datname, '-') as db,
                   '-' as last_seen,
                   s.calls as exec_count,
                   round(s.{max_col}::numeric, 2) as max_latency,
                   round(s.{mean_col}::numeric, 2) as avg_latency
            from pg_stat_statements s
            left join pg_database d on d.oid = s.dbid
        """.format(max_col=max_col, mean_col=mean_col)

        filter_db = args.get('filter_db', 'no')
        if filter_db == 'yes':
            sql += ' where d.datname is not null '

        sql += ' order by s.calls desc limit 20'
        rows = fmtRows(client.query(sql))
        return mw.returnData(True, 'ok', rows)
    finally:
        client.close()


def _redundantIndexes(client):
    sql = """
        select n.nspname as table_schema,
               t.relname as table_name,
               ic.relname as redundant_index_name,
               coalesce((
                   select string_agg(a.attname, ',' order by k.ord)
                   from unnest(i.indkey) with ordinality as k(attnum, ord)
                   join pg_attribute a on a.attrelid = i.indrelid and a.attnum = k.attnum
               ), '') as redundant_index_columns,
               'DROP INDEX ' || quote_ident(n.nspname) || '.' || quote_ident(ic.relname) as sql_drop_index
        from pg_index i
        join pg_class t on t.oid = i.indrelid
        join pg_namespace n on n.oid = t.relnamespace
        join pg_class ic on ic.oid = i.indexrelid
        where n.nspname not in ('pg_catalog', 'information_schema', 'pg_toast')
          and not exists (
              select 1 from pg_constraint con where con.conindid = i.indexrelid
          )
          and exists (
              select 1
              from pg_index i2
              join pg_class ic2 on ic2.oid = i2.indexrelid
              where i2.indrelid = i.indrelid
                and i2.indkey = i.indkey
                and i2.indclass = i.indclass
                and i2.indcollation = i.indcollation
                and i2.indpred is not distinct from i.indpred
                and i2.indexprs is not distinct from i.indexprs
                and i2.indexrelid <> i.indexrelid
                and ic2.relname < ic.relname
          )
        order by 1, 2, 3
    """
    return fmtRows(client.query(sql))


# 查看重复或冗余的索引
def get_redundant_indexes(args):
    client, err = openClient(args)
    if err:
        return err

    try:
        rows = _redundantIndexes(client)
        return mw.returnData(True, 'ok', rows)
    finally:
        client.close()


# 删除重复或冗余的索引
def redundant_indexes_cmd(args):
    client, err = openClient(args)
    if err:
        return err

    try:
        rows = _redundantIndexes(client)
        index = int(args['index'])
        if index >= len(rows):
            return mw.returnData(False, '索引不存在，请刷新后重试')

        client.execute(rows[index]['sql_drop_index'])
        return mw.returnData(True, '执行成功!')
    finally:
        client.close()


# 统计库里每个表的大小
def get_table_info(args):
    client, err = openClient(args)
    if err:
        return err

    try:
        sql = """
            select n.nspname as "TABLE_SCHEMA",
                   c.relname as "TABLE_NAME",
                   case c.relkind
                       when 'r' then 'table'
                       when 'p' then 'partitioned table'
                       when 'v' then 'view'
                       when 'm' then 'materialized view'
                       else c.relkind::text
                   end as "ENGINE",
                   c.reltuples as rows_estimate,
                   pg_relation_size(c.oid) as data_bytes,
                   pg_indexes_size(c.oid) as index_bytes,
                   pg_total_relation_size(c.oid) as total_bytes,
                   coalesce((
                       select string_agg(a.attname, ',' order by k.ord)
                       from pg_index i
                       join unnest(i.indkey) with ordinality as k(attnum, ord) on true
                       join pg_attribute a on a.attrelid = i.indrelid and a.attnum = k.attnum
                       where i.indrelid = c.oid and i.indisprimary
                   ), '-') as "COLUMN_NAME",
                   coalesce((
                       select string_agg(format_type(a.atttypid, a.atttypmod), ',' order by k.ord)
                       from pg_index i
                       join unnest(i.indkey) with ordinality as k(attnum, ord) on true
                       join pg_attribute a on a.attrelid = i.indrelid and a.attnum = k.attnum
                       where i.indrelid = c.oid and i.indisprimary
                   ), '-') as "COLUMN_TYPE"
            from pg_class c
            join pg_namespace n on n.oid = c.relnamespace
            where c.relkind in ('r', 'p', 'v', 'm')
              and n.nspname not in ('pg_catalog', 'information_schema', 'pg_toast')
              and n.nspname not like 'pg_temp%'
            order by total_bytes desc
        """
        rows = client.query(sql)

        for i in range(len(rows)):
            row = rows[i]
            row['DATA_LENGTH'] = round(float(row['data_bytes'] or 0) / 1024 / 1024 / 1024, 2)
            row['INDEX_LENGTH'] = round(float(row['index_bytes'] or 0) / 1024 / 1024 / 1024, 2)
            row['TOTAL_LENGTH'] = round(float(row['total_bytes'] or 0) / 1024 / 1024 / 1024, 2)
            # PostgreSQL 没有 AUTO_INCREMENT，使用 SEQUENCE / IDENTITY
            row['AUTO_INCREMENT'] = '-'
            row['RESIDUAL_AUTO_INCREMENT'] = '使用 SEQUENCE/IDENTITY'
            row['ROWS_ESTIMATE'] = int(row['rows_estimate'] or 0)
            del row['data_bytes']
            del row['index_bytes']
            del row['total_bytes']

        return mw.returnData(True, 'ok', fmtRows(rows))
    finally:
        client.close()


# 查看应用端IP连接数总和
def get_conn_count(args):
    client, err = openClient(args)
    if err:
        return err

    try:
        sql = """
            select usename as "user",
                   coalesce(datname, '空') as db,
                   coalesce(host(client_addr), '本地') as "Client_IP",
                   count(*) as count
            from pg_stat_activity
            where backend_type = 'client backend'
            group by usename, datname, client_addr
            order by count desc
        """
        rows = fmtRows(client.query(sql))
        return mw.returnData(True, 'ok', rows)
    finally:
        client.close()


# 快速找出没有主键的表
def get_fpk_info(args):
    client, err = openClient(args)
    if err:
        return err

    try:
        sql = """
            select n.nspname as table_schema, c.relname as table_name
            from pg_class c
            join pg_namespace n on n.oid = c.relnamespace
            where c.relkind in ('r', 'p')
              and n.nspname not in ('pg_catalog', 'information_schema', 'pg_toast')
              and not exists (
                  select 1 from pg_index i
                  where i.indrelid = c.oid and i.indisprimary
              )
            order by n.nspname, c.relname
        """
        rows = fmtRows(client.query(sql))
        return mw.returnData(True, 'ok', rows)
    finally:
        client.close()


# 查看当前锁阻塞的SQL
def get_lock_sql(args):
    client, err = openClient(args)
    if err:
        return err

    try:
        sql = """
            select coalesce(a.backend_xid::text, '-') as trx_id,
                   '等待锁' as trx_state,
                   a.xact_start as trx_started,
                   a.pid as processlist_id,
                   a.query as info,
                   a.usename as "user",
                   coalesce(host(a.client_addr), '本地') as host,
                   a.datname as db,
                   coalesce(a.wait_event_type, '-') as command,
                   a.state,
                   'SELECT pg_cancel_backend(' || a.pid || ')' as sql_kill_blocking_query,
                   pg_blocking_pids(a.pid) as blocking_pids
            from pg_stat_activity a
            where cardinality(pg_blocking_pids(a.pid)) > 0
              and a.backend_type = 'client backend'
            order by a.xact_start
        """
        rows = fmtRows(client.query(sql))
        return mw.returnData(True, 'ok', rows)
    finally:
        client.close()


# 终止阻塞会话
def kill_lock_pid(args):
    client, err = openClient(args)
    if err:
        return err

    try:
        pid = int(args['pid'])
        data = client.one('select pg_terminate_backend(%s) as ok', (pid,))
        if data is None or data['ok'] is not True:
            return mw.returnData(False, '结束会话失败，请检查会话是否存在')
        return mw.returnData(True, '执行成功!')
    finally:
        client.close()


# 终止所有阻塞会话
def kill_all_lock(args):
    client, err = openClient(args)
    if err:
        return err

    try:
        sql = """
            select distinct unnest(pg_blocking_pids(pid)) as pid
            from pg_stat_activity
            where cardinality(pg_blocking_pids(pid)) > 0
              and backend_type = 'client backend'
        """
        rows = client.query(sql)
        count = 0
        for x in rows:
            data = client.one('select pg_terminate_backend(%s) as ok', (x['pid'],))
            if data is not None and data['ok'] is True:
                count += 1
        return mw.returnData(True, '执行成功，已结束 %s 个阻塞会话' % count)
    finally:
        client.close()


# 查看死锁信息
def get_deadlock_info(args):
    client, err = openClient(args)
    if err:
        return err

    try:
        deadlocks = client.one('select coalesce(sum(deadlocks), 0) as num from pg_stat_database')
        locks = client.query("""
            select pid, usename as "user", datname as db, state,
                   coalesce(wait_event_type, '-') as wait_event_type,
                   query
            from pg_stat_activity
            where cardinality(pg_blocking_pids(pid)) > 0
              and backend_type = 'client backend'
        """)

        msg = 'PostgreSQL 不保存历史死锁明细，仅提供累计次数与当前锁等待。\n'
        msg += '数据库累计死锁次数：%s\n' % deadlocks['num']
        if len(locks) == 0:
            msg += '当前没有处于锁等待的会话。'
        else:
            msg += '当前锁等待会话：\n'
            for x in locks:
                msg += 'pid=%s user=%s db=%s state=%s wait=%s\nquery=%s\n' % (
                    x['pid'], x['user'], x['db'], x['state'], x['wait_event_type'], x['query'])
        return mw.returnData(True, 'ok', msg)
    finally:
        client.close()


# 查看主从复制信息
def get_slave_status(args):
    client, err = openClient(args)
    if err:
        return err

    try:
        recovery = client.one('select pg_is_in_recovery() as recovery')['recovery']

        if recovery is False:
            reps = client.query("""
                select client_addr, application_name, state, sync_state,
                       sent_lsn, write_lsn, flush_lsn, replay_lsn,
                       coalesce(replay_lag::text, '-') as replay_lag
                from pg_stat_replication
            """)
            if len(reps) == 0:
                return mw.returnData(True, 'ok', '未开启主从复制：当前为主库，且没有复制的从库连接。')

            msg = '当前为主库，从库复制状态：\n'
            for x in reps:
                msg += '从库地址：%s 应用：%s\n' % (x['client_addr'], x['application_name'])
                msg += '状态：%s  同步模式：%s\n' % (x['state'], x['sync_state'])
                msg += 'sent_lsn=%s write_lsn=%s flush_lsn=%s replay_lsn=%s\n' % (
                    x['sent_lsn'], x['write_lsn'], x['flush_lsn'], x['replay_lsn'])
                msg += 'replay_lag=%s\n\n' % x['replay_lag']
            return mw.returnData(True, 'ok', msg)

        # 当前为从库
        lag = client.one("""
            select coalesce(extract(epoch from (now() - pg_last_xact_replay_timestamp()))::int, 0) as lag
        """)
        lsn = client.one("""
            select pg_last_wal_receive_lsn() as receive_lsn,
                   pg_last_wal_replay_lsn() as replay_lsn,
                   pg_last_xact_replay_timestamp() as replay_time
        """)

        msg = '当前为从库，复制状态：\n'
        msg += 'receive_lsn=%s\n' % lsn['receive_lsn']
        msg += 'replay_lsn=%s\n' % lsn['replay_lsn']
        msg += '最近回放时间=%s\n' % lsn['replay_time']
        msg += '延迟时间：%s 秒' % lag['lag']
        return mw.returnData(True, 'ok', msg)
    finally:
        client.close()
