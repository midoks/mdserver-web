# coding:utf-8

import sys
import os
import re
import json
import time
import threading

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


def getRootPwd():
    """从 sqlite config 表读取 postgres root 密码, 与 backup.py / index.py 同源."""
    db_path = getServerDir()
    db_name = 'pgsql'
    return mw.M('config').dbPos(db_path, db_name).where('id=?', (1,)).getField('pg_root')


# -------- 连接缓存: 同一 (host, port, database) 30 秒内复用 --------
# 前端 2s 轮询 × 多接口 = 每秒 10+ 次新建连接, 每次都做 scram-sha-256 认证,
# 用简单 TTL cache 把 90% 的连接开销吃掉.
_conn_cache = {}          # key=(host, port, database), value=(PgClient, expire_ts)
_conn_cache_ttl = 30      # 秒


def _cacheGetClient(database='postgres'):
    """从缓存取 (或新建) 一个 PgClient."""
    port = getPort()
    host = getSocketDir() or '127.0.0.1'
    key = (host, port, database)
    now = time.time()
    item = _conn_cache.get(key)
    if item and item[1] > now:
        client = item[0]
        # 快速探测: 发个 ping 确认还活着
        try:
            client.execute('select 1')
            return client
        except Exception:
            # 连接死了, 扔掉重建
            try:
                client.conn.close()
            except Exception:
                pass
            del _conn_cache[key]

    client = PgClient(database)
    if not client.connect():
        return None
    client._cached = True   # 标记为缓存连接, close() 时不真关
    _conn_cache[key] = (client, now + _conn_cache_ttl)
    return client


def _cacheClear():
    """进程退出前清所有连接."""
    for key, item in list(_conn_cache.items()):
        try:
            item[0].close()
        except Exception:
            pass
    _conn_cache.clear()


def openClient(args, database='postgres'):
    # 1) 缓存快速通道: 大部分情况下 30s 内直接复用, 零额外握手
    try:
        client = _cacheGetClient(database)
        if client is not None:
            return client, None
    except Exception:
        pass

    # 2) 缓存 miss / connect 失败: 走原来的 error 分类逻辑
    client = PgClient(database)
    if not client.connect():
        detail = (client.error or '').strip()
        if client.status == 'not_installed':
            msg = 'PostgreSQL 未安装'
        elif client.status == 'not_running':
            msg = 'PostgreSQL 未启动' + ('：' + detail if detail else '')
        elif client.status == 'db_not_found':
            msg = '数据库不存在' + ('：' + detail if detail else '')
        elif client.status == 'auth_error':
            msg = '连接失败，请检查数据库认证配置' + ('：' + detail if detail else '')
        else:
            msg = detail or '连接失败'
        return None, mw.returnData(False, msg)

    # 3) connect 成功但缓存里没有 —— 补进缓存 (理论上不会走到这里, 防御性代码)
    client._cached = True
    port = getPort()
    host = getSocketDir() or '127.0.0.1'
    key = (host, port, database)
    _conn_cache[key] = (client, time.time() + _conn_cache_ttl)
    return client, None


class PgClient:

    def __init__(self, database='postgres'):
        self.database = database
        self.status = None
        self.error = None
        self.conn = None
        self._cached = False   # True = 来自 _conn_cache, close() 时不真关连接

    def connect(self):
        if not isInstalled():
            self.status = 'not_installed'
            self.error = 'PostgreSQL 未安装'
            return False

        try:
            host = getSocketDir()
            if host == '':
                host = '127.0.0.1'

            pwd = getRootPwd()
            if not pwd:
                self.status = 'auth_error'
                self.error = '未找到 postgres root 密码 (sqlite config 表 pg_root 为空)'
                return False

            self.conn = psycopg2.connect(
                database=self.database,
                user='postgres',
                password=pwd,
                host=host,
                port=getPort(),
                connect_timeout=3)
            self.conn.autocommit = True
            return True
        except psycopg2.OperationalError as e:
            msg = str(e).strip()
            if 'does not exist' in msg:
                self.status = 'db_not_found'
                self.error = '数据库不存在: ' + msg
            elif 'authentication' in msg or 'password' in msg:
                self.status = 'auth_error'
                self.error = '认证失败: ' + msg
            elif 'could not connect' in msg or 'Connection refused' in msg or 'refused' in msg:
                self.status = 'not_running'
                self.error = 'PostgreSQL 未启动或端口不通: ' + msg
            else:
                self.status = 'not_running'
                self.error = msg
        except Exception as e:
            self.status = 'not_running'
            self.error = '连接异常: ' + str(e)
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
        if self._cached:
            # 缓存连接: 不真关, 只重置 TTL (同一次轮询里下次还能复用)
            port = getPort()
            host = getSocketDir() or '127.0.0.1'
            key = (host, port, self.database)
            _conn_cache[key] = (self, time.time() + _conn_cache_ttl)
            return
        if self.conn:
            self.conn.close()
            self.conn = None


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


# get_net_list 用的差分缓存: 存上一次快照, 本次调用 - 上次 = QPS/TPS, 不需要 sleep
_net_last_snap = None  # (timestamp, dict snapshot)


# QPS/TPS 指标 (无阻塞: 用上次快照做差分, 不 sleep)
def get_net_list(args):
    from datetime import datetime

    client, err = openClient(args)
    if err:
        return err

    try:
        global _net_last_snap
        now = time.time()
        curr = _dbStatSnapshot(client)

        max_conn = client.one("select setting from pg_settings where name = 'max_connections'")
        conn_row = client.one("select count(*) as num from pg_stat_activity where backend_type = 'client backend'")

        if _net_last_snap is None or (now - _net_last_snap[0]) < 0.5:
            # 第一次调用 / 间隔太短: 差分不可靠, 返回 0 并记录快照
            diff_select = diff_insert = diff_update = diff_delete = diff_commit = 0
        else:
            prev_ts, prev = _net_last_snap
            elapsed = now - prev_ts
            diff_select = round((curr['fetched'] - prev['fetched']) / elapsed, 2)
            diff_insert = round((curr['inserted'] - prev['inserted']) / elapsed, 2)
            diff_update = round((curr['updated'] - prev['updated']) / elapsed, 2)
            diff_delete = round((curr['deleted'] - prev['deleted']) / elapsed, 2)
            diff_commit = round((curr['commits'] - prev['commits']) / elapsed, 2)

        _net_last_snap = (now, curr)

        row = {}
        row['current_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row['select'] = diff_select
        row['insert'] = diff_insert
        row['update'] = diff_update
        row['delete'] = diff_delete
        row['commit'] = diff_commit
        row['conn'] = conn_row['num']
        row['max_conn'] = max_conn['setting']
        row['recv_mbps'] = '-'
        row['send_mbps'] = '-'

        rdata = [row]
        return mw.returnData(True, 'ok', rdata)
    finally:
        # client 在连接缓存里, 不 close
        pass


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

        # 先检查 shared_preload_libraries —— pg_stat_statements 必须预加载
        preload = client.one("select setting from pg_settings where name = 'shared_preload_libraries'")
        libs = (preload or {}).get('setting', '') or ''
        if 'pg_stat_statements' not in libs:
            return mw.returnData(False, "pg_stat_statements 扩展必须在启动时预加载。\n"
                "请在 postgresql.conf 添加 shared_preload_libraries = 'pg_stat_statements' 后重启 PostgreSQL。")

        # 再检查扩展是否已 CREATE
        ext = client.one("select to_regclass('pg_stat_statements') as v")
        if ext is None or ext['v'] is None:
            return mw.returnData(False, "pg_stat_statements 扩展已预加载，但尚未启用。\n"
                "请在当前数据库执行 CREATE EXTENSION pg_stat_statements;")

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


# ---------------- PostgreSQL 健康检查 ----------------

_PG_QUERY_FAILED = object()
_PG_HEALTH_SNAPSHOTS = {}
_PG_HEALTH_SNAPSHOT_LOCK = threading.Lock()
_PG_HEALTH_SNAPSHOT_TTL = 6 * 3600
_PG_HEALTH_SNAPSHOT_CAPACITY = 256


def _pg_health_counter_snapshot(key, counters):
    """保存轻量计数基线, 返回首轮/重置状态及间隔增量和速率."""
    now = time.time()
    current = {str(k): float(v) for k, v in counters.items() if isinstance(v, (int, float))}
    with _PG_HEALTH_SNAPSHOT_LOCK:
        expired = [k for k, v in _PG_HEALTH_SNAPSHOTS.items()
                   if now - v['time'] > _PG_HEALTH_SNAPSHOT_TTL]
        for old_key in expired:
            _PG_HEALTH_SNAPSHOTS.pop(old_key, None)
        if key not in _PG_HEALTH_SNAPSHOTS and len(_PG_HEALTH_SNAPSHOTS) >= _PG_HEALTH_SNAPSHOT_CAPACITY:
            oldest = min(_PG_HEALTH_SNAPSHOTS, key=lambda k: _PG_HEALTH_SNAPSHOTS[k]['time'])
            _PG_HEALTH_SNAPSHOTS.pop(oldest, None)
        previous = _PG_HEALTH_SNAPSHOTS.get(key)
        _PG_HEALTH_SNAPSHOTS[key] = {'time': now, 'counters': current}

    if previous is None:
        return {'first': True, 'reset': False, 'elapsed': 0, 'delta': {}, 'rate': {}}
    elapsed = now - previous['time']
    old = previous['counters']
    reset = elapsed <= 0 or any(k in old and current[k] < old[k] for k in current)
    if reset:
        return {'first': False, 'reset': True, 'elapsed': max(elapsed, 0), 'delta': {}, 'rate': {}}
    delta = {k: v - old.get(k, v) for k, v in current.items()}
    rate = {k: v / elapsed for k, v in delta.items()}
    return {'first': False, 'reset': False, 'elapsed': elapsed, 'delta': delta, 'rate': rate}


def get_health(args):
    client, err = openClient(args)
    if err:
        return err

    lines = []
    issues = []  # [(level, section, text)]  level: 2=critical 1=warn 0=tip
    cur_section = ''

    def section(title):
        nonlocal cur_section
        cur_section = title
        lines.append('')
        lines.append('━━━ %s ━━━' % title)

    def ok(msg):   lines.append('  ✅ ' + msg)
    def critical(msg): issues.append((2, cur_section, '🚨 ' + msg)); lines.append('  🚨 ' + msg)
    def warn(msg):     issues.append((1, cur_section, '⚠️  ' + msg)); lines.append('  ⚠️  ' + msg)
    def tip(msg):      issues.append((0, cur_section, '💡 ' + msg)); lines.append('  💡 ' + msg)
    def unknown(msg):  issues.append((-1, cur_section, '❓ ' + msg)); lines.append('  ❓ ' + msg)
    def skipped(msg):  unknown('已跳过: ' + msg)
    def info(msg):   lines.append('  ℹ️   ' + msg)

    def one(sql):
        try:
            row = client.one(sql)
            if not row:
                return None
            return list(row.values())[0]
        except Exception:
            return _PG_QUERY_FAILED

    def find(sql):
        try:
            return client.query(sql)
        except Exception:
            return _PG_QUERY_FAILED

    instance_key = '%s:%s' % (args.get('sid', 0), getattr(client, 'database', 'postgres'))

    def counters(name, values):
        return _pg_health_counter_snapshot(instance_key + ':' + name, values)

    try:
        # ---------- 0. 基础信息 ----------
        section('基础信息')
        ver = one('SELECT version()')
        if ver is _PG_QUERY_FAILED:
            unknown('版本查询失败或权限不足')
        else:
            info('版本: %s' % str(ver or '').split(',')[0].strip()[:60])

        version_num = one('SHOW server_version_num')
        try:
            version_num = int(version_num)
        except (TypeError, ValueError):
            if version_num is _PG_QUERY_FAILED:
                unknown('server_version_num 查询失败或权限不足')
            else:
                unknown('无法识别 server_version_num: %s' % version_num)
            version_num = None

        uptime_sec = one("SELECT EXTRACT(EPOCH FROM (now() - pg_postmaster_start_time()))::int")
        if uptime_sec is _PG_QUERY_FAILED:
            unknown('运行时间查询失败或权限不足')
        elif uptime_sec is not None:
            uptime_sec = int(uptime_sec)
            if uptime_sec >= 86400:
                info('已运行: %d天%02d:%02d:%02d' % (uptime_sec//86400, (uptime_sec%86400)//3600, (uptime_sec%3600)//60, uptime_sec%60))
            else:
                info('已运行: %d分钟' % max(uptime_sec//60, 1))

        sp = one("SHOW shared_preload_libraries")
        if sp is _PG_QUERY_FAILED:
            pgss = False
            unknown('shared_preload_libraries 查询失败或权限不足')
        else:
            sp = str(sp or '')
            pgss = 'pg_stat_statements' in sp.lower()
            info('shared_preload_libraries: %s' % sp)
            if pgss:
                ok('pg_stat_statements 已预加载 (可识别热点 SQL)')
            else:
                warn('pg_stat_statements 未预加载, 无法识别热点 SQL')
                warn('postgresql.conf: shared_preload_libraries = pg_stat_statements')

        # ---------- 1. 连接 ----------
        section('连接')
        conn_rows = find("""
            SELECT current_setting('max_connections')::int AS max_conn,
                   current_setting('superuser_reserved_connections')::int AS super_res,
                   (SELECT count(*) FROM pg_stat_activity) AS total_conn,
                   (SELECT count(*) FROM pg_stat_activity WHERE state='active') AS active,
                   (SELECT count(*) FROM pg_stat_activity WHERE state='idle') AS idle
        """)
        if conn_rows is _PG_QUERY_FAILED:
            unknown('连接统计查询失败或权限不足')
        elif not conn_rows:
            unknown('连接统计未返回数据')
        else:
            r = conn_rows[0]
            max_conn = int(r['max_conn'])
            total_conn = int(r['total_conn'])
            active = int(r['active'])
            idle = int(r['idle'])
            conn_pct = total_conn / max_conn * 100 if max_conn else 0
            info('连接数: active=%d, idle=%d, total=%d / max_connections=%d (%.1f%%), superuser_reserved=%d' % (
                active, idle, total_conn, max_conn, conn_pct, int(r['super_res'])))
            if conn_pct >= 90:
                critical('连接数 %d/%d (%.1f%%), 即将耗尽' % (total_conn, max_conn, conn_pct))
            elif conn_pct >= 70:
                warn('连接数水位 %.1f%%, 建议关注' % conn_pct)
            else:
                ok('连接数水位正常')

        lock_wait = one("SELECT count(*) FROM pg_stat_activity WHERE wait_event_type='Lock'")
        if lock_wait is _PG_QUERY_FAILED:
            unknown('锁等待连接统计查询失败或权限不足')
        elif lock_wait is None:
            unknown('锁等待连接统计未返回数据')
        elif int(lock_wait) > 0:
            warn('当前有 %d 个等待锁的连接 (可能有热点行/慢事务)' % int(lock_wait))
        else:
            ok('无连接等待锁')

        # ---------- 2. XID 回卷风险 (关键!) ----------
        section('事务 ID / 回卷风险')
        xid_table = find("""
            SELECT datname, age(datfrozenxid) AS age,
                   pg_size_pretty(pg_database_size(datname)) AS size
            FROM pg_database WHERE datistemplate=false ORDER BY age DESC LIMIT 10
        """)
        if xid_table is _PG_QUERY_FAILED:
            unknown('XID 年龄查询失败或权限不足')
        elif not xid_table:
            info('当前可见范围没有非模板数据库')
        else:
            for r in xid_table[:5]:
                if r.get('age') is None:
                    unknown('%s 的 XID 年龄未知' % r.get('datname'))
                    continue
                age = int(r['age'])
                dbn = r['datname']
                if age >= 1500000000:
                    critical('XID 回卷临界! %s age=%d, 必须立即检查 VACUUM FREEZE / autovacuum' % (dbn, age))
                elif age >= 1200000000:
                    warn('XID 偏高: %s age=%d, 请检查 autovacuum 是否跟上' % (dbn, age))
                elif age >= 1000000000:
                    tip('XID 中高: %s age=%d, 建议关注 autovacuum 运行情况' % (dbn, age))
                else:
                    ok('%s age=%d (正常)' % (dbn, age))

        # ---------- 3. WAL / Checkpoint ----------
        section('WAL / Checkpoint')
        if version_num is None:
            skipped('版本未知, 无法选择兼容的 checkpoint 统计视图')
            cp_rows = _PG_QUERY_FAILED
        elif version_num >= 170000:
            cp_rows = find("SELECT num_timed AS timed, num_requested AS requested FROM pg_stat_checkpointer")
        else:
            cp_rows = find("SELECT checkpoints_timed AS timed, checkpoints_req AS requested FROM pg_stat_bgwriter")

        if cp_rows is not _PG_QUERY_FAILED and cp_rows:
            cp = cp_rows[0]
            cp_timed = int(cp.get('timed') or 0)
            cp_req = int(cp.get('requested') or 0)
            cp_total = cp_timed + cp_req
            cp_req_pct = cp_req / cp_total * 100 if cp_total else 0
            info('累计 checkpoints: timed=%d, requested=%d (requested %.1f%%)' % (cp_timed, cp_req, cp_req_pct))
            snap = counters('checkpoint', {'timed': cp_timed, 'requested': cp_req})
            if snap['first']:
                info('已建立 checkpoint 计数基线, 下次检查分析间隔增量')
            elif snap['reset']:
                info('checkpoint 计数回退或时间间隔异常, 已重建基线')
            else:
                dt = int(snap['delta'].get('timed', 0))
                dr = int(snap['delta'].get('requested', 0))
                total = dt + dr
                req_pct = dr / total * 100 if total else 0
                info('本间隔 checkpoints: timed=%d, requested=%d, elapsed=%.1fs' % (dt, dr, snap['elapsed']))
                if req_pct >= 20 and total >= 10:
                    warn('本间隔 checkpoint 压力大, %d 次是请求触发 (可能 max_wal_size 太小)' % dr)
                    warn('结合 WAL 生成速率评估 max_wal_size 和 checkpoint_completion_target, 不要直接套用固定值')
                else:
                    ok('本间隔未发现 checkpoint 压力 (requested %.1f%%)' % req_pct)
        elif cp_rows is not _PG_QUERY_FAILED:
            unknown('checkpoint 统计未返回数据')
        elif version_num is not None:
            unknown('checkpoint 统计查询失败、权限不足或当前版本不支持')

        wal_level = one('SHOW wal_level')
        max_wal = one('SHOW max_wal_size')
        cct = one('SHOW checkpoint_completion_target')
        for name, value in [('wal_level', wal_level), ('max_wal_size', max_wal), ('checkpoint_completion_target', cct)]:
            if value is _PG_QUERY_FAILED:
                unknown('%s 查询失败或权限不足' % name)
        if wal_level is not _PG_QUERY_FAILED:
            info('wal_level=%s, max_wal_size=%s, checkpoint_completion_target=%s' % (
                wal_level, max_wal if max_wal is not _PG_QUERY_FAILED else 'unknown',
                cct if cct is not _PG_QUERY_FAILED else 'unknown'))
            if wal_level in ('replica', 'logical'):
                ok('WAL 级别 %s 支持 PITR / 主从' % wal_level)
            else:
                warn('wal_level=%s 过低, 不支持 Point-In-Time Recovery' % wal_level)
                warn('评估 Point-In-Time Recovery 需求后再调整 wal_level; 修改需重启')

        # ---------- 4. Buffer Pool / BGWriter ----------
        section('Buffer Pool / BGWriter')
        sb = one('SHOW shared_buffers')
        ecs = one('SHOW effective_cache_size')
        if sb is _PG_QUERY_FAILED or ecs is _PG_QUERY_FAILED:
            unknown('Buffer Pool 配置查询失败或权限不足')
        else:
            info('shared_buffers=%s, effective_cache_size=%s' % (sb, ecs))
            sb_text = str(sb or '')
            sb_mb = 0
            try:
                sb_mb = int(float(sb_text.replace('GB', '').replace('MB', '')) * (1024 if 'GB' in sb_text else 1))
            except (TypeError, ValueError):
                unknown('无法解析 shared_buffers: %s' % sb_text)
            total_mem_mb = 16384
            try:
                import psutil
                total_mem_mb = psutil.virtual_memory().total / 1024 / 1024
            except Exception:
                pass
            if sb_mb:
                sb_pct = sb_mb / total_mem_mb * 100
                info('shared_buffers=%.0fMB (%.1f%% of total memory %.0fMB)' % (sb_mb, sb_pct, total_mem_mb))
                if sb_pct < 25:
                    tip('shared_buffers 低于物理内存 25%%, 请结合工作集、连接数和其他服务内存占用评估')

        # 缓存命中率也按检查间隔计算, 避免实例启动以来的历史值掩盖当前问题。
        db_hit = find("""
            SELECT datname, blks_read, blks_hit
            FROM pg_stat_database WHERE datname NOT IN ('template0','template1','postgres')
            ORDER BY blks_read DESC LIMIT 5
        """)
        if db_hit is _PG_QUERY_FAILED:
            unknown('Buffer Pool 命中率统计查询失败或权限不足')
        elif not db_hit:
            info('当前可见范围没有业务数据库缓存统计')
        else:
            for r in db_hit:
                reads = int(r.get('blks_read') or 0)
                hits = int(r.get('blks_hit') or 0)
                snap = counters('buffer:' + str(r['datname']), {'read': reads, 'hit': hits})
                if snap['first']:
                    info('%s 已建立缓存计数基线 (累计 read=%d, hit=%d)' % (r['datname'], reads, hits))
                elif snap['reset']:
                    info('%s 缓存计数回退或时间间隔异常, 已重建基线' % r['datname'])
                else:
                    dr = snap['delta'].get('read', 0)
                    dh = snap['delta'].get('hit', 0)
                    if dr + dh <= 0:
                        info('%s 本间隔没有缓存块访问, 不计算命中率' % r['datname'])
                        continue
                    hr = dh / (dr + dh) * 100
                    if hr < 95:
                        warn('%s 本间隔 Buffer Pool 命中率 %.2f%% 偏低, 请结合工作集和内存评估' % (r['datname'], hr))
                    else:
                        ok('%s 本间隔缓存命中率 %.2f%%' % (r['datname'], hr))

        # ---------- 5. 死锁 ----------
        section('死锁 / 锁等待')
        total_deadlocks = one("SELECT coalesce(sum(deadlocks), 0) FROM pg_stat_database")
        if total_deadlocks is _PG_QUERY_FAILED:
            unknown('死锁统计查询失败或权限不足')
        elif total_deadlocks is None:
            unknown('死锁统计未返回数据')
        else:
            total_deadlocks = int(total_deadlocks)
            info('累计死锁: %d' % total_deadlocks)
            snap = counters('deadlocks', {'count': total_deadlocks})
            if snap['first']:
                info('已建立死锁计数基线, 下次检查分析间隔增量')
            elif snap['reset']:
                info('死锁计数回退或时间间隔异常, 已重建基线')
            elif snap['delta'].get('count', 0) > 0:
                warn('本间隔新增 %d 次死锁, 应用层事务存在冲突' % int(snap['delta']['count']))
                warn("排查: SELECT query, query_start, state FROM pg_stat_activity WHERE wait_event_type='Lock'")
                warn('建议应用端按固定顺序获取锁, 缩短事务并增加有限重试')
            else:
                ok('本间隔未检测到新增死锁')

        # ---------- 6. 慢查询 / 热点 SQL ----------
        section('热点 SQL / 慢查询')
        if not pgss:
            skipped('pg_stat_statements 未预加载或状态未知, 无法识别热点 SQL')
        elif version_num is None:
            skipped('版本未知, 无法选择 pg_stat_statements 的兼容时间列')
        else:
            total_col = 'total_exec_time' if version_num >= 130000 else 'total_time'
            mean_col = 'mean_exec_time' if version_num >= 130000 else 'mean_time'
            topq = find("""
                SELECT query, calls, %s AS total_time, %s AS mean_time,
                       rows, blk_read_time, blk_write_time
                FROM pg_stat_statements ORDER BY %s DESC LIMIT 5
            """ % (total_col, mean_col, total_col))
            if topq is _PG_QUERY_FAILED:
                unknown('pg_stat_statements 查询失败、权限不足或扩展未在当前数据库安装')
            elif not topq:
                ok('pg_stat_statements 暂无数据 (刚开启或样本不足)')
            else:
                for r in topq[:3]:
                    q = str(r.get('query') or '')[:120]
                    info('热点: calls=%d mean=%.1fms total=%.0fms rows=%s  %s' % (
                        int(r.get('calls') or 0), float(r.get('mean_time') or 0),
                        float(r.get('total_time') or 0), r.get('rows'), q.replace('\n', ' ')))

        # 无主键表: 同时返回可见总数和有限样本, 不把 LIMIT 后的数量当总数。
        nopk = find("""
            WITH no_pk AS (
                SELECT tc.table_schema, tc.table_name
                FROM information_schema.tables tc
                WHERE tc.table_schema NOT IN ('pg_catalog','information_schema')
                  AND tc.table_type='BASE TABLE'
                  AND NOT EXISTS (
                      SELECT 1 FROM information_schema.table_constraints tco
                      WHERE tco.table_schema=tc.table_schema AND tco.table_name=tc.table_name
                        AND tco.constraint_type='PRIMARY KEY')
            )
            SELECT count(*) OVER() AS total_count, table_schema, table_name FROM no_pk LIMIT 10
        """)
        if nopk is _PG_QUERY_FAILED:
            unknown('无主键表扫描失败或权限不足')
        elif not nopk:
            ok('当前可见业务表都有主键')
        else:
            total_nopk = int(nopk[0].get('total_count') or len(nopk))
            critical('发现至少 %d 张无主键表 (最多展示 10 个样本)' % total_nopk)
            for r in nopk[:5]:
                info('无主键样本: %s.%s' % (r['table_schema'], r['table_name']))

        # ---------- 7. 表扫描 / 未使用索引 ----------
        section('表扫描 / 未使用索引')
        seq_scan_tables = find("""
            SELECT schemaname, relname, relid, seq_scan, seq_tup_read, idx_scan,
                   pg_size_pretty(pg_total_relation_size(relid)) AS total
            FROM pg_stat_user_tables WHERE seq_scan > 100
            ORDER BY seq_scan DESC LIMIT 10
        """)
        if seq_scan_tables is _PG_QUERY_FAILED:
            unknown('表扫描统计查询失败或权限不足')
        elif not seq_scan_tables:
            ok('统计周期内没有累计 seq_scan>100 的业务表')
        else:
            seq_hot = 0
            seq_ready = False
            for r in seq_scan_tables[:5]:
                seq_scan = int(r.get('seq_scan') or 0)
                idx_scan = int(r.get('idx_scan') or 0)
                snap = counters('seq:' + str(r['relid']), {'seq': seq_scan, 'idx': idx_scan})
                label = '%s.%s' % (r['schemaname'], r['relname'])
                if snap['first']:
                    info('%s 已建立表扫描基线 (累计 seq=%d, idx=%d, total=%s)' % (
                        label, seq_scan, idx_scan, r.get('total')))
                elif snap['reset']:
                    info('%s 表扫描计数回退或时间间隔异常, 已重建基线' % label)
                else:
                    seq_ready = True
                    ds = int(snap['delta'].get('seq', 0))
                    di = int(snap['delta'].get('idx', 0))
                    if ds > 100:
                        seq_hot += 1
                        warn('%s 本间隔 seq_scan=%d, idx_scan=%d, total=%s; 请用 EXPLAIN (ANALYZE, BUFFERS) 核实执行计划、行数和缓冲区后再决定是否调整索引' % (
                            label, ds, di, r.get('total')))
            if seq_ready and seq_hot == 0:
                ok('本间隔未发现明显全表扫描热点')

        unused_idx = find("""
            SELECT schemaname, tablename, indexname, idx_scan
            FROM pg_stat_user_indexes WHERE idx_scan=0
              AND schemaname NOT IN ('pg_catalog','information_schema')
            LIMIT 10
        """)
        if unused_idx is _PG_QUERY_FAILED:
            unknown('索引使用统计查询失败或权限不足')
        elif not unused_idx:
            ok('当前统计周期未发现 idx_scan=0 的业务索引样本')
        else:
            tip('发现至少 %d 个自统计重置以来 idx_scan=0 的索引样本 (最多 10 个):' % len(unused_idx))
            for r in unused_idx[:3]:
                info('低使用索引样本: %s.%s.%s' % (r['schemaname'], r['tablename'], r['indexname']))
            tip('需覆盖完整业务周期并排除约束/稀有任务用途, 不要仅凭本报告删除索引')

        # ---------- 8. autovacuum ----------
        section('autovacuum / 膨胀')
        av = one('SHOW autovacuum')
        av_workers = one('SHOW autovacuum_max_workers')
        if av is _PG_QUERY_FAILED or av_workers is _PG_QUERY_FAILED:
            unknown('autovacuum 配置查询失败或权限不足')
        else:
            info('autovacuum=%s, max_workers=%s' % (av, av_workers))
            if str(av).lower() == 'off':
                critical('autovacuum 被关闭! 表会膨胀, XID 会耗尽')

        # 大表 / 膨胀: 使用稳定 relid, 避免 schema/table 拼接和标识符引用错误。
        big = find("""
            SELECT schemaname, relname, relid,
                   pg_size_pretty(pg_total_relation_size(relid)) AS total,
                   n_live_tup, n_dead_tup,
                   last_vacuum, last_autovacuum, last_analyze, last_autoanalyze
            FROM pg_stat_user_tables
            ORDER BY pg_total_relation_size(relid) DESC LIMIT 10
        """)
        if big is _PG_QUERY_FAILED:
            unknown('大表和死元组统计查询失败或权限不足')
        elif not big:
            info('当前可见范围没有业务表统计')
        else:
            for r in big[:3]:
                dead = int(r.get('n_dead_tup') or 0)
                live = int(r.get('n_live_tup') or 0)
                dead_pct = dead / live * 100 if live else (100 if dead else 0)
                if dead_pct >= 200 and dead >= 1000:
                    warn('%s.%s total=%s 死元组 n_dead_tup=%d (占 live %d%%, autovacuum 可能跟不上)' % (
                        r['schemaname'], r['relname'], r['total'], dead, dead_pct))
                elif dead >= 10000 and dead_pct >= 50:
                    tip('%s.%s 死元组较多 n_dead_tup=%d (占 live %d%%)' % (
                        r['schemaname'], r['relname'], dead, dead_pct))

        # ---------- 9. 主从 ----------
        section('主从复制')
        recovery = one('SELECT pg_is_in_recovery()')
        if recovery is _PG_QUERY_FAILED or recovery is None:
            unknown('主从角色查询失败或权限不足')
        elif recovery:
            lag_sec = one("SELECT extract(epoch from (now() - pg_last_xact_replay_timestamp()))::int")
            if lag_sec is _PG_QUERY_FAILED:
                unknown('从库复制延迟查询失败或权限不足')
            elif lag_sec is None:
                unknown('从库尚无回放事务时间, 无法计算复制延迟')
            else:
                lag_sec = int(lag_sec)
                info('当前为从库, 复制延迟: %d 秒' % lag_sec)
                if lag_sec > 0:
                    warn('复制存在 %d 秒延迟' % lag_sec)
                else:
                    ok('主从复制无延迟')
        else:
            slots = find("SELECT slot_name, slot_type, active, restart_lsn, pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS lag FROM pg_replication_slots")
            if slots is _PG_QUERY_FAILED:
                unknown('复制槽查询失败或权限不足, 无法确认主库复制状态')
            elif not slots:
                ok('当前为主库, 未配置复制槽')
            else:
                for r in slots:
                    if not r['active']:
                        warn('复制槽 %s 非 active, retained WAL lag=%s' % (r['slot_name'], r['lag']))
                    else:
                        info('复制槽 %s active, retained WAL lag=%s' % (r['slot_name'], r['lag']))

        # ---------- 总结 ----------
        lines.append('')
        lines.append('━━━ 总结 ━━━')
        nc = sum(1 for x in issues if x[0] == 2)
        nw = sum(1 for x in issues if x[0] == 1)
        nt = sum(1 for x in issues if x[0] == 0)
        nu = sum(1 for x in issues if x[0] == -1)
        if not issues:
            lines.append('  🎉 PostgreSQL 健康状况良好!')
        else:
            lines.append('  📊 严重 🚨 %d / 警告 ⚠️  %d / 建议 💡 %d / 未知 ❓ %d (共 %d)' % (
                nc, nw, nt, nu, len(issues)))
            if nu > 0:
                lines.append('  ❓ 存在查询失败、权限不足或不支持的检查, 不能据此判定整体健康')
            if nc > 0:
                lines.append(''); lines.append('  ── 最严重 Top %d ──' % min(nc, 5))
                for idx, (lv, sec, txt) in enumerate([x for x in issues if x[0] == 2]):
                    if idx >= 5: break
                    lines.append('  %s  [%s]' % (txt, sec))
            lines.append(''); lines.append('  ── 完整清单 (按严重度排序) ──')
            for lv, sec, txt in sorted(issues, key=lambda x: (-x[0], x[1])):
                lines.append('  %s  [%s]' % (txt, sec))
        lines.append('')
        lines.append('  ℹ️   配置建议仅供评估; 本报告不会执行 SQL 优化、删除对象或修改配置')

        return mw.returnData(True, 'ok', '\n'.join(lines))
    finally:
        client.close()

