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
    def info(msg):   lines.append('  ℹ️   ' + msg)

    def one(sql, default=None):
        try:
            r = client.one(sql)
            if not r: return default
            return list(r.values())[0]
        except Exception: return default

    def find(sql, default=[]):
        try: return client.find(sql)
        except Exception: return default

    try:
        # ---------- 0. 基础信息 ----------
        section('基础信息')
        ver = one('SELECT version()') or ''
        info('版本: %s' % ver.split(',')[0].strip()[:60])
        uptime_sec = one("SELECT (EXTRACT(EPOCH FROM (now() - pg_postmaster_start_time()))::int)") or 0
        if uptime_sec >= 86400:
            info('已运行: %d天%02d:%02d:%02d' % (uptime_sec//86400, (uptime_sec%86400)//3600, (uptime_sec%3600)//60, uptime_sec%60))
        else:
            info('已运行: %d分钟' % max(uptime_sec//60, 1))

        sp = one("SHOW shared_preload_libraries") or ''
        pgss = 'pg_stat_statements' in sp.lower()
        info('shared_preload_libraries: %s' % sp)
        if pgss:
            ok('pg_stat_statements 已预加载 (可识别热点 SQL)')
        else:
            warn('pg_stat_statements 未预加载, 无法识别热点 SQL')
            warn('postgresql.conf: shared_preload_libraries = pg_stat_statements')

        # ---------- 1. 连接 ----------
        section('连接')
        max_conn = int(one('SHOW max_connections') or 0)
        super_res = int(one('SHOW superuser_reserved_connections') or 0)
        total_conn = int(one('SELECT count(*) FROM pg_stat_activity') or 0)
        active = int(one("SELECT count(*) FROM pg_stat_activity WHERE state='active'") or 0)
        idle = int(one("SELECT count(*) FROM pg_stat_activity WHERE state='idle'") or 0)
        conn_pct = total_conn / max_conn * 100 if max_conn else 0
        info('连接数: active=%d, idle=%d, total=%d / max_connections=%d (%.1f%%)' % (active, idle, total_conn, max_conn, conn_pct))
        if conn_pct >= 90:
            critical('连接数 %d/%d (%.1f%%), 即将耗尽' % (total_conn, max_conn, conn_pct))
        elif conn_pct >= 70:
            warn('连接数水位 %.1f%%, 建议关注' % conn_pct)
        else:
            ok('连接数水位正常')

        lock_wait = int(one("SELECT count(*) FROM pg_stat_activity WHERE wait_event_type='Lock'") or 0)
        if lock_wait > 0:
            warn('当前有 %d 个等待锁的连接 (可能有热点行/慢事务)' % lock_wait)
        else:
            ok('无连接等待锁')

        # ---------- 2. XID 回卷风险 (关键!) ----------
        section('事务 ID / 回卷风险')
        xid_table = find("""
            SELECT datname, age(datfrozenxid) AS age,
                   pg_size_pretty(pg_database_size(datname)) AS size
            FROM pg_database WHERE datistemplate=false ORDER BY age DESC LIMIT 10
        """)
        if xid_table:
            for r in xid_table[:5]:
                age = int(r['age']) if r.get('age') else 0
                dbn = r['datname']
                if age >= 1500000000:
                    critical('XID 回卷临界! %s age=%d (≥ 2^31 - 500000000, 必须立刻 VACUUM FREEZE / autovacuum_max_workers 调大)' % (dbn, age))
                elif age >= 1200000000:
                    warn('XID 偏高: %s age=%d, autovacuum 可能太慢, 建议调大 autovacuum_max_workers / autovacuum_vacuum_scale_factor' % (dbn, age))
                elif age >= 1000000000:
                    tip('XID 中高: %s age=%d, 建议关注 autovacuum 运行情况' % (dbn, age))
                else:
                    ok('%s age=%d (正常)' % (dbn, age))
        else:
            ok('所有数据库 XID 年龄都正常')

        # autovacuum 状态
        av = one('SHOW autovacuum')
        info('autovacuum: %s, max_workers: %s' % (av, one('SHOW autovacuum_max_workers')))

        # ---------- 3. WAL / Checkpoint ----------
        section('WAL / Checkpoint')
        cp_timed = int(one("SELECT checkpoints_timed FROM pg_stat_bgwriter") or 0)
        cp_req = int(one("SELECT checkpoints_req FROM pg_stat_bgwriter") or 0)
        total_cp = cp_timed + cp_req
        req_pct = cp_req / total_cp * 100 if total_cp else 0
        info('checkpoints: timed=%d, requested=%d (requested %.1f%%)' % (cp_timed, cp_req, req_pct))
        if req_pct >= 20 and total_cp >= 10:
            warn('checkpoint 压力大, %d 次是请求触发 (可能 WAL max_wal_size 太小)' % cp_req)
            warn('postgresql.conf: max_wal_size=8GB, min_wal_size=2GB, checkpoint_completion_target=0.9')
        elif total_cp == 0:
            ok('暂无 checkpoint 压力')
        else:
            ok('checkpoint 压力正常 (requested %.1f%%)' % req_pct)

        wal_level = one('SHOW wal_level')
        max_wal = one('SHOW max_wal_size')
        cct = one('SHOW checkpoint_completion_target')
        info('wal_level=%s, max_wal_size=%s, checkpoint_completion_target=%s' % (wal_level, max_wal, cct))
        if wal_level in ('replica', 'logical'):
            ok('WAL 级别 %s 支持 PITR / 主从' % wal_level)
        else:
            warn('wal_level=%s 过低, 不支持 Point-In-Time Recovery' % wal_level)
            warn('postgresql.conf: wal_level=replica (或 logical 如需逻辑复制)')

        # ---------- 4. Buffer Pool / BGWriter ----------
        section('Buffer Pool / BGWriter')
        sb = one('SHOW shared_buffers')
        ecs = one('SHOW effective_cache_size')
        info('shared_buffers=%s, effective_cache_size=%s' % (sb, ecs))
        sb_mb = 0
        try: sb_mb = int(float(sb.replace('GB','').replace('MB','')) * (1024 if 'GB' in sb else 1)) if sb else 0
        except: pass
        total_mem_mb = 16384  # 兜底; 真实环境可以 psutil
        try:
            import psutil; total_mem_mb = psutil.virtual_memory().total / 1024 / 1024
        except Exception: pass
        sb_pct = sb_mb / total_mem_mb * 100 if sb_mb else 0
        info('shared_buffers=%.0fMB (%.1f%% of total memory %.0fMB)' % (sb_mb, sb_pct, total_mem_mb))
        if sb_pct < 25:
            warn('shared_buffers 偏低, 建议调到物理内存的 25~50%%')
            warn('postgresql.conf: shared_buffers=%dMB' % int(total_mem_mb * 0.3))

        # 命中率
        db_hit = find("""
            SELECT datname,
                   blks_read, blks_hit,
                   round((1 - blks_read::numeric / nullif(blks_read + blks_hit, 0)) * 100, 2) AS hit_rate
            FROM pg_stat_database WHERE datname NOT IN ('template0','template1','postgres')
            ORDER BY blks_read DESC LIMIT 5
        """)
        if db_hit:
            for r in db_hit:
                hr = float(r['hit_rate'] or 100)
                if hr < 95:
                    warn('%s Buffer Pool 命中率 %.2f%% 偏低, 建议调大 shared_buffers' % (r['datname'], hr))
                else:
                    ok('%s 命中率 %.2f%%' % (r['datname'], hr))

        # ---------- 5. 死锁 ----------
        section('死锁 / 锁等待')
        deadlocks = int(one("SELECT deadlocks FROM pg_stat_database WHERE datname='postgres'") or 0)
        total_deadlocks = 0
        try:
            for r in find("SELECT deadlocks FROM pg_stat_database"):
                total_deadlocks += int(r['deadlocks'] or 0)
        except Exception: pass
        info('累计死锁: %d' % total_deadlocks)
        if total_deadlocks > 0:
            warn('累计出现 %d 次死锁, 应用层事务冲突' % total_deadlocks)
            warn('排查: SELECT query, query_start, state FROM pg_stat_activity WHERE wait_event_type=%sLock%s' % ("'", "'"))
            warn('建议应用端按固定顺序获取锁, 缩短事务, 加 retry')
        else:
            ok('未检测到死锁')

        # ---------- 6. 慢查询 / 热点 SQL ----------
        section('热点 SQL / 慢查询')
        if pgss:
            try:
                topq = find("""
                    SELECT query, calls, total_exec_time, mean_exec_time,
                           rows, blk_read_time, blk_write_time
                    FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 5
                """)
                if topq:
                    for r in topq[:3]:
                        q = (r['query'] or '')[:120]
                        warn('热点: calls=%d mean=%.1fms total=%.0fms rows=%s  %s' % (
                            r['calls'] or 0, r['mean_exec_time'] or 0, r['total_exec_time'] or 0,
                            r.get('rows'), q.replace('\n',' ')))
                else:
                    ok('pg_stat_statements 暂无数据 (刚开启或样本不足)')
            except Exception as e:
                info('pg_stat_statements 查询异常: %s' % str(e))
        else:
            info('(pg_stat_statements 未预加载, 无法识别热点 SQL)')

        # 无主键表
        nopk = find("""
            SELECT tc.table_schema, tc.table_name
            FROM information_schema.tables tc
            WHERE tc.table_schema NOT IN ('pg_catalog','information_schema')
              AND tc.table_type='BASE TABLE'
              AND NOT EXISTS (
                  SELECT 1 FROM information_schema.table_constraints tco
                  WHERE tco.table_schema=tc.table_schema AND tco.table_name=tc.table_name AND tco.constraint_type='PRIMARY KEY')
            LIMIT 10
        """)
        if nopk:
            critical('发现 %d 张无主键表' % len(nopk))
            for r in nopk[:5]: critical('  %s.%s' % (r['table_schema'], r['table_name']))
        else:
            ok('所有业务表都有主键')

        # ---------- 7. 表扫描 / 未使用索引 ----------
        section('表扫描 / 未使用索引')
        seq_scan_tables = find("""
            SELECT schemaname, relname, seq_scan, seq_tup_read, idx_scan
            FROM pg_stat_user_tables WHERE seq_scan > 100
            ORDER BY seq_scan DESC LIMIT 10
        """)
        if seq_scan_tables:
            for r in seq_scan_tables[:5]:
                warn('%s.%s seq_scan=%d, idx_scan=%d (考虑加索引)' % (
                    r['schemaname'], r['relname'], r['seq_scan'], r['idx_scan']))
        else:
            ok('业务表无明显全表扫描热点')

        unused_idx = find("""
            SELECT schemaname, tablename, indexname, idx_scan
            FROM pg_stat_user_indexes WHERE idx_scan=0
              AND schemaname NOT IN ('pg_catalog','information_schema')
            LIMIT 10
        """)
        if unused_idx:
            tip('发现 %d 个从未命中的索引 (取前 3):' % len(unused_idx))
            for r in unused_idx[:3]:
                tip('  %s.%s.%s (可考虑 DROP)' % (r['schemaname'], r['tablename'], r['indexname']))

        # ---------- 8. autovacuum ----------
        section('autovacuum / 膨胀')
        av = one('SHOW autovacuum')
        av_workers = one('SHOW autovacuum_max_workers')
        info('autovacuum=%s, max_workers=%s' % (av, av_workers))
        if av.lower() == 'off':
            critical('autovacuum 被关闭! 表会膨胀, XID 会耗尽')

        # 大表 / 膨胀
        big = find("""
            SELECT schemaname, relname,
                   pg_size_pretty(pg_total_relation_size(schemaname||'.'||relname)) AS total,
                   n_live_tup, n_dead_tup,
                   last_vacuum, last_autovacuum, last_analyze, last_autoanalyze
            FROM pg_stat_user_tables
            ORDER BY pg_total_relation_size(schemaname||'.'||relname) DESC LIMIT 10
        """)
        if big:
            for r in big[:3]:
                dead = int(r['n_dead_tup'] or 0)
                live = int(r['n_live_tup'] or 1)
                dead_pct = dead / live * 100 if live else 0
                if dead_pct >= 200 and dead >= 1000:
                    warn('%s.%s total=%s 死元组 n_dead_tup=%d (占 live %d%%, autovacuum 跟不上)' % (
                        r['schemaname'], r['relname'], r['total'], dead, dead_pct))
                elif dead >= 10000 and dead_pct >= 50:
                    tip('%s.%s 死元组较多 n_dead_tup=%d (占 live %d%%)' % (
                        r['schemaname'], r['relname'], dead, dead_pct))

        # ---------- 9. 主从 ----------
        section('主从复制')
        recovery = one('SELECT pg_is_in_recovery()')
        if recovery:
            lag_sec = int(one("SELECT coalesce(extract(epoch from (now() - pg_last_xact_replay_timestamp()))::int, 0)") or 0)
            info('当前为从库, 复制延迟: %d 秒' % lag_sec)
            if lag_sec > 0:
                warn('复制存在 %d 秒延迟' % lag_sec)
            else:
                ok('主从复制无延迟')
        else:
            # 主库复制槽
            try:
                slots = find("SELECT slot_name, slot_type, active, restart_lsn, pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS lag FROM pg_replication_slots")
                if slots:
                    for r in slots:
                        if not r['active']:
                            warn('复制槽 %s 非 active, 但还有 lag=%s' % (r['slot_name'], r['lag']))
                        else:
                            info('复制槽 %s active, lag=%s' % (r['slot_name'], r['lag']))
                else:
                    ok('当前为主库, 未配置复制槽')
            except Exception:
                ok('当前为主库')

        # ---------- 总结 ----------
        lines.append('')
        lines.append('━━━ 总结 ━━━')
        nc = sum(1 for x in issues if x[0] == 2)
        nw = sum(1 for x in issues if x[0] == 1)
        nt = sum(1 for x in issues if x[0] == 0)
        if not issues:
            lines.append('  🎉 PostgreSQL 健康状况良好!')
        else:
            lines.append('  📊 严重 🚨 %d / 警告 ⚠️  %d / 建议 💡 %d (共 %d)' % (nc, nw, nt, len(issues)))
            if nc > 0:
                lines.append(''); lines.append('  ── 最严重 Top %d ──' % min(nc, 5))
                for idx, (lv, sec, txt) in enumerate([x for x in issues if x[0] == 2]):
                    if idx >= 5: break
                    lines.append('  %s  [%s]' % (txt, sec))
            lines.append(''); lines.append('  ── 完整清单 (按严重度排序) ──')
            for lv, sec, txt in sorted(issues, key=lambda x: (-x[0], x[1])):
                lines.append('  %s  [%s]' % (txt, sec))
        lines.append('')
        lines.append('  ℹ️   postgresql.conf 修改后需重启, WAL/部分参数可用 pg_reload_conf()')

        return mw.returnData(True, 'ok', '\n'.join(lines))
    finally:
        client.close()

