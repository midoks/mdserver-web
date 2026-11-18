# coding:utf-8

import sys
import io
import os
import time
import re
import pymongo
import json
import yaml

from bson.objectid import ObjectId
from bson.json_util import dumps


# -------- MongoDB Extended JSON 展平: 把嵌套单键特殊类型转成可读值 --------
# bson.json_util.dumps 输出的 Extended JSON 里日期/ObjectId/Decimal 等都是嵌套 dict,
# 前端直接拼接字符串会显示 [object Object]. 这里递归展平成标准类型.
_BSON_SPECIAL_KEYS = {
    '$oid', '$date', '$numberLong', '$numberDecimal', '$numberInt',
    '$numberDouble', '$binary', '$regex', '$minKey', '$maxKey',
    '$timestamp', '$code', '$symbol', '$ref',
}


def _flatten_bson(obj):
    """递归把 MongoDB Extended JSON 的特殊嵌套结构展平为可前端直接展示的值."""
    if isinstance(obj, dict):
        # 单键且是 BSON 特殊类型 → 提取其值
        if len(obj) == 1:
            key = next(iter(obj))
            if key == '$oid':
                return obj[key]
            if key == '$date':
                # 已是 ISO 字符串, 直接返回
                return obj[key]
            if key in ('$numberLong', '$numberInt'):
                try:
                    return int(obj[key])
                except (ValueError, TypeError):
                    return obj[key]
            if key == '$numberDecimal':
                try:
                    return float(obj[key])
                except (ValueError, TypeError):
                    return obj[key]
            if key == '$numberDouble':
                try:
                    return float(obj[key])
                except (ValueError, TypeError):
                    return obj[key]
            if key == '$minKey':
                return '<minKey>'
            if key == '$maxKey':
                return '<maxKey>'
            if key == '$timestamp':
                ts = obj[key]
                if isinstance(ts, dict) and 't' in ts:
                    import datetime
                    try:
                        return datetime.datetime.utcfromtimestamp(ts['t']).strftime('%Y-%m-%d %H:%M:%S')
                    except Exception:
                        return str(ts)
                return str(obj[key])
            if key == '$binary':
                b = obj[key]
                if isinstance(b, dict):
                    return b.get('base64', '') + ' (base64)'
                return str(b)
            if key == '$regex':
                pattern = obj[key]
                opts = obj.get('$options', '')
                return '/' + pattern + '/' + opts
            if key == '$code':
                return '<code> ' + str(obj[key])
            if key == '$symbol':
                return str(obj[key])
            if key == '$ref':
                return obj.get('$ref', '')
            # 不是特殊键, 继续递归普通 dict
            return {k: _flatten_bson(v) for k, v in obj.items()}
        # 多键 dict: 全部递归
        return {k: _flatten_bson(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_flatten_bson(item) for item in obj]
    return obj

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

def getPluginName():
    return 'mongodb'
    
def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()

def getConf():
    path = getServerDir() + "/mongodb.conf"
    return path


def getConfTpl():
    path = getPluginDir() + "/config/mongodb.conf"
    return path

def pSqliteDb(dbname='users'):
    file = getServerDir() + '/mongodb.db'
    name = 'mongodb'

    sql_file = getPluginDir() + '/config/mongodb.sql'
    import_sql = mw.readFile(sql_file)
    # print(sql_file,import_sql)
    md5_sql = mw.md5(import_sql)

    import_sign = False
    save_md5_file = getServerDir() + '/import_mongodb.md5'
    if os.path.exists(save_md5_file):
        save_md5_sql = mw.readFile(save_md5_file)
        if save_md5_sql != md5_sql:
            import_sign = True
            mw.writeFile(save_md5_file, md5_sql)
    else:
        mw.writeFile(save_md5_file, md5_sql)

    if not os.path.exists(file) or import_sql:
        conn = mw.M(dbname).dbPos(getServerDir(), name)
        csql_list = import_sql.split(';')
        for index in range(len(csql_list)):
            conn.execute(csql_list[index], ())

    conn = mw.M(dbname).dbPos(getServerDir(), name)
    return conn

def getConfigData():
    cfg = getConf()
    # print(cfg)
    config_data = mw.readFile(cfg)
    try:
        config = yaml.safe_load(config_data)
    except:
        config = {
            "systemLog": {
                "destination": "file",
                "logAppend": True,
                "path": mw.getServerDir()+"/mongodb/log/mongodb.log"
            },
            "storage": {
                "dbPath": mw.getServerDir()+"/mongodb/data",
                "directoryPerDB": True,
                "journal": {
                    "enabled": True
                }
            },
            "processManagement": {
                "fork": True,
                "pidFilePath": mw.getServerDir()+"/mongodb/log/mongodb.pid"
            },
            "net": {
                "port": 27017,
                "bindIp": "0.0.0.0"
            },
            "security": {
                "authorization": "disabled",
                "javascriptEnabled": False
            }
        }
    return config

def getConfPort():
    data = getConfigData()
    return data['net']['port']

def getConfAuth():
    data = getConfigData()
    return data['security']['authorization']

@singleton
class nosqlMongodb():

    __DB_PASS = None
    __DB_USER = None
    __DB_PORT = 6379
    __DB_HOST = '127.0.0.1'
    __DB_CONN = None
    __DB_ERR = None
    __DB_STATUS = None

    __DB_LOCAL = None

    def __init__(self):
        self.__config = self.get_options(None)


    def mgdb_conn(self):

        if self.__DB_HOST in ['127.0.0.1', 'localhost']:
            mgdb_path = "{}/mongodb".format(mw.getServerDir())
            if not os.path.exists(mgdb_path):
                self.__DB_STATUS = 'not_installed'
                return False

        if not self.__DB_LOCAL:
            if not self.__config:
                self.__DB_STATUS = 'not_installed'
                return False
            self.__DB_PORT = int(self.__config['port'])

        auth = getConfAuth()
        port = getConfPort()
        mg_root = pSqliteDb('config').where('id=?', (1,)).getField('mg_root')
        try:
            if auth == 'disabled':
                self.__DB_CONN = pymongo.MongoClient(host=self.__DB_HOST, port=port, directConnection=True, serverSelectionTimeoutMS=3000)
            else:
                self.__DB_CONN = pymongo.MongoClient(host=self.__DB_HOST, port=port, directConnection=True, username='root',password=mg_root, serverSelectionTimeoutMS=3000)
            self.__DB_CONN.admin.command('ping')
            # 节点处于 recovering/startup 时 ping 仍会成功，但读写会抛 NotPrimaryError
            try:
                hello = self.__DB_CONN.admin.command('hello')
            except Exception:
                # MongoDB < 5.0 没有 hello 命令
                hello = self.__DB_CONN.admin.command('isMaster')
            if not (hello.get('isWritablePrimary') or hello.get('ismaster') or hello.get('secondary')):
                self.__DB_ERR = 'MongoDB 节点当前不是 primary 或 secondary 状态'
                return False
            self.__DB_STATUS = None
            self.__DB_ERR = None
            return self.__DB_CONN
        except pymongo.errors.ConnectionFailure:
            self.__DB_STATUS = 'not_running'
            return False
        except Exception:
            self.__DB_STATUS = 'not_running'
        return False

    # 连接状态：not_installed 未安装 / not_running 未启动 / None 正常
    def get_status(self):
        return self.__DB_STATUS

    def get_err(self):
        return self.__DB_ERR

    # 获取配置项
    def get_options(self, get=None):
        result = {}
        mgdb_content = mw.readFile("{}/mongodb/mongodb.conf".format(mw.getServerDir()))
        if not mgdb_content: return False

        keys = ["bind_ip", "port"]

        result['host'] = '127.0.0.1'
        rep = r'port\s*=\s*(.*)'
        ip_re = re.search(rep, mgdb_content)
        if ip_re:
            result['port'] = int(ip_re.groups()[0].strip())
        else:
            result['port'] = 27017
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
class nosqlMongodbCtr():

    def __init__(self):
        pass

    def getInstanceBySid(self, sid = 0):
        instance = nosqlMongodb()
        return instance

    def _connect(self, sid):
        obj = self.getInstanceBySid(sid)
        conn = obj.mgdb_conn()
        if conn is False:
            if obj.get_status() == 'not_installed':
                return None, mw.returnData(False, '未安装')
            err = obj.get_err()
            if err:
                return None, mw.returnData(False, err)
            return None, mw.returnData(False, '未启动')
        return conn, None

    def getDbList(self, args):
        sid = args['sid']
        mgdb_instance, err = self._connect(sid)
        if err:
            return err

        result = {}
        doc_list = mgdb_instance.list_database_names()
        rlist = []
        for x in doc_list:
            if not x in ['admin', 'config', 'local']:
                rlist.append(x)
        result['list'] = rlist
        return mw.returnData(True,'ok', result)

    def getCollectionsList(self, args):
        sid = args['sid']
        name = args['name']

        mgdb_instance, err = self._connect(sid)
        if err:
            return err

        result = {}
        collections = mgdb_instance[name].list_collection_names()
        result['collections'] = collections
        return mw.returnData(True,'ok', result)

    def getDataList(self, args):
        sid = args['sid']
        db = args['db']
        collection = args['collection']
        p = 1
        size = 10
        if 'p' in args:
            p = args['p']

        if 'size' in args:
            size = args['size']

        mgdb_instance, err = self._connect(sid)
        if err:
            return err

        db_instance = mgdb_instance[db]
        collection_instance = db_instance[collection]

        start_index = (p - 1) * size
        end_index = p * size
        args_where = args['where']

        where = {}
        if 'field' in args_where:
            mg_field = args_where['field']

            if mg_field == '_id':
                mg_value = ObjectId(args_where['value'])
                where[mg_field] = mg_value
            else:
                mg_value = args_where['value']
                where[mg_field] = re.compile(mg_value)

        # print(where)
        result = collection_instance.find(where).skip(start_index).limit(size).sort('_id',-1)
        if where:
            count = collection_instance.count_documents(where)
        else:
            collection_stats = db_instance.command("collStats", collection)
            count = collection_stats.get("count")

        d = []
        for document in result:
            d.append(document)

        doc_str_json = dumps(d)
        raw_result = json.loads(doc_str_json)
        result = _flatten_bson(raw_result)


        page_args = {}
        page_args['count'] = count
        page_args['tojs'] = 'mongodbDataList'
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

    def delById(self,args):
        sid = args['sid']
        db = args['db']
        collection = args['collection']

        mgdb_instance, err = self._connect(sid)
        if err:
            return err

        db_instance = mgdb_instance[db]
        collection_instance = db_instance[collection]

        _id = args['_id']
        result = collection_instance.delete_one({"_id": ObjectId(_id)})

        return mw.returnData(True,'文档删除【%d】个成功!' % result.deleted_count)

# ---------------------------------- run ----------------------------------
# 获取 mongodb databases 列表
def get_db_list(args):
    t = nosqlMongodbCtr()
    return t.getDbList(args)

# 获取 mongodb collections 列表
def get_collections_list(args):
    t = nosqlMongodbCtr()
    return t.getCollectionsList(args)

def get_data_list(args):
    t = nosqlMongodbCtr()
    return t.getDataList(args)

def set_kv(args):
    t = nosqlMongodbCtr()
    return t.setKv(args)


def del_val(args):
    t = nosqlMongodbCtr()
    return t.delVal(args)

def batch_del_val(args):
    t = nosqlMongodbCtr()
    return t.batchDelVal(args)

def clear_flushdb(args):
    t = nosqlMongodbCtr()
    return t.clearFlushDB(args)

def del_by_id(args):
    t = nosqlMongodbCtr()
    return t.delById(args)


# ---------------- MongoDB 健康检查 ----------------
def get_health(args):
    sid = args.get('sid', 0)
    ctr = nosqlMongodbCtr()
    client, err = ctr._connect(sid)
    if err: return err

    lines = []
    issues = []
    cur_section = ''

    def section(title):
        nonlocal cur_section
        cur_section = title
        lines.append(''); lines.append('━━━ %s ━━━' % title)
    def ok(msg):       lines.append('  ✅ ' + msg)
    def critical(msg): issues.append((2, cur_section, '🚨 ' + msg)); lines.append('  🚨 ' + msg)
    def warn(msg):     issues.append((1, cur_section, '⚠️  ' + msg)); lines.append('  ⚠️  ' + msg)
    def tip(msg):      issues.append((0, cur_section, '💡 ' + msg)); lines.append('  💡 ' + msg)
    def info(msg):   lines.append('  ℹ️   ' + msg)

    try:
        ss = client.admin.command('serverStatus')

        # ---------- 0. 基础信息 ----------
        section('基础信息')
        info('MongoDB %s' % ss.get('version'))
        upt = int(ss.get('uptime', 0))
        info('已运行: %s' % ('%d天%02d:%02d' % (upt//86400, (upt%86400)//3600, (upt%3600)//60)))
        info('存储引擎: %s' % ss.get('storageEngine', {}).get('name', 'unknown'))

        try:
            hi = client.admin.command('hostInfo')
            host_mem_mb = hi.get('system', {}).get('memSizeMB', 0)
            host_cores = hi.get('system', {}).get('numCores', 0)
            info('主机: %d核 / %dMB' % (host_cores, host_mem_mb))
        except Exception:
            host_mem_mb = 0

        # ---------- 1. 连接 ----------
        section('连接')
        cc = ss.get('connections', {})
        cur_conn = cc.get('current', 0)
        avail = cc.get('available', 0)
        total = cur_conn + avail
        conn_pct = cur_conn / total * 100 if total else 0
        info('连接: current=%d, available=%d, reused/totalCreated=%d' % (
            cur_conn, avail, cc.get('totalCreated', 0)))
        if conn_pct >= 80:
            warn('连接数水位 %.1f%% 偏高' % conn_pct)
        elif cc.get('rejected', 0) > 0:
            critical('已拒绝 %d 次新连接, maxConns 不够' % cc['rejected'])
        else:
            ok('连接数水位正常')

        # ---------- 2. 内存 ----------
        section('内存 / WiredTiger')
        mem = ss.get('mem', {})
        resident_mb = mem.get('resident', 0)
        virt_mb = mem.get('virtual', 0)
        info('mem.resident=%dMB, virtual=%dMB' % (resident_mb, virt_mb))

        try:
            wt = ss.get('wiredTiger', {})
            if wt:
                cache = wt.get('cache', {})
                max_bytes = cache.get('size max bytes configured', 0)
                cur_bytes = cache.get('size in bytes', 0)
                dirty = cache.get('size dirty in bytes', 0)
                pages_read = wt.get('statistics', {}).get('pages read into cache', 0)
                pages_written = wt.get('statistics', {}).get('pages written from cache', 0)
                info('WT cache max=%.0fMB, current=%.0fMB, dirty=%.0fMB (%.1f%%)' % (
                    max_bytes/1024/1024, cur_bytes/1024/1024, dirty/1024/1024,
                    dirty/cur_bytes*100 if cur_bytes else 0))
                if max_bytes > 0 and host_mem_mb > 0:
                    cache_pct = max_bytes / (host_mem_mb*1024*1024) * 100
                    if cache_pct < 40:
                        warn('WT cache sizeOnly 只占物理内存 %.1f%%, 建议调到 50%%' % cache_pct)
                        warn('mongod.conf: storage.wiredTiger.engineConfig.cacheSizeMB = %d' % int(host_mem_mb * 0.5))
                if pages_read + pages_written > 0:
                    cache_hit = (1 - pages_read / (pages_read + pages_written)) * 100
                    info('WT cache hit rate (近似): %.2f%%' % cache_hit)
        except Exception:
            pass

        # ---------- 3. opcounters / QPS ----------
        section('opcounters / 操作')
        oc = ss.get('opcounters', {})
        total_ops = sum(int(v) for v in oc.values())
        info('累计操作: insert=%d query=%d update=%d delete=%d command=%d getmore=%d' % (
            oc.get('insert',0), oc.get('query',0), oc.get('update',0),
            oc.get('delete',0), oc.get('command',0), oc.get('getmore',0)))
        # 每 10 秒算 diff 取 QPS (简化: 用 total_ops / uptime 估算)
        qps_est = total_ops / max(upt, 1)
        info('QPS 估算 (累计平均): %.1f' % qps_est)

        net = ss.get('network', {})
        info('网络: bytesIn=%d, bytesOut=%d' % (net.get('bytesIn',0), net.get('bytesOut',0)))
        if net.get('numSlowDNSOperations', 0) > 0 or net.get('numSlowSSLOperations', 0) > 0:
            warn('有慢速 DNS / SSL 操作, 检查网络环境')

        # ---------- 4. 锁 / 死锁 ----------
        section('锁 / 死锁')
        try:
            locks = ss.get('locks', {})
            wait_total = 0
            for mode in ('Write','Read'):
                lk = locks.get('acquireWaitCount', {}).get(mode, {})
                wait_total += sum(int(v) for v in lk.values())
            info('累计锁等待次数: %d' % wait_total)
            if wait_total > 100:
                warn('锁等待较多, 应用层有热点文档/长事务')
                warn('排查: db.currentOp({"waitingForLock": true})')
            else:
                ok('锁等待正常')
        except Exception:
            ok('(锁指标在当前版本不可用)')

        # ---------- 5. 持久化 / journal ----------
        section('持久化 / Checkpoint')
        try:
            dur = ss.get('dur', {})
            jcommits = dur.get('journaledCommits', 0)
            ccommits = dur.get('commitsInWriteLock', 0)
            info('journal commits=%d, commitsInWriteLock=%d' % (jcommits, ccommits))
            if ccommits > 0:
                tip('有 commits 在 writeLock 中完成, journal 可能成为瓶颈')
                tip('mongod.conf: storage.journal.commitIntervalMs 可适当调大 (默认 300ms)')
        except Exception:
            info('(dur 指标不可用)')

        # storageEngine readOnly?
        if ss.get('storageEngine', {}).get('readOnly'):
            critical('storageEngine 是 readOnly! 磁盘可能只读 / fsync 锁')

        # ---------- 6. Profiling ----------
        section('Profiling / system.profile')
        try:
            for dn in client.list_database_names():
                if dn in ('admin','config','local'): continue
                try:
                    lv = client[dn].command('profile', -1).get('was', 0)
                    if lv > 0:
                        info('%s profiling level=%d' % (dn, lv))
                        try:
                            pc = client[dn].command('collStats', 'system.profile').get('count', 0)
                            if pc > 10000:
                                warn('%s.system.profile 已有 %d 条慢查询, 建议清理或调 profile threshold' % (dn, pc))
                        except Exception: pass
                except Exception: pass
        except Exception: pass

        # ---------- 7. 索引 / schema ----------
        section('索引 / schema')
        unused_idx_count = 0
        try:
            for dn in client.list_database_names():
                if dn in ('admin','config','local'): continue
                try:
                    for coll_stats, data in client[dn].command({'$indexStats': {}}).items():
                        ns = data.get('ns', coll_stats) if isinstance(data, dict) else coll_stats
                        for idx_name, idx_info in (data.get('indexes', {}) if isinstance(data, dict) else {}).items():
                            if idx_info.get('accesses', {}).get('ops', 0) == 0 and idx_name != '_id_':
                                unused_idx_count += 1
                                if unused_idx_count <= 3:
                                    coll_name = ns.split('.', 1)[1] if '.' in ns else ns
                                    tip('%s.%s 索引 %s 从未命中 (可考虑 DROP)' % (dn, coll_name, idx_name))
                except Exception: pass
        except Exception: pass
        if unused_idx_count == 0:
            ok('暂无从未命中的索引')

        # ---------- 8. 大集合 / 膨胀 ----------
        section('大集合 / 膨胀')
        big_colls = []
        total_size_mb = 0
        for dn in client.list_database_names():
            if dn in ('admin','config','local'): continue
            try:
                ds = client[dn].command('dbStats')
                total_size_mb += ds.get('storageSize', 0) / 1024 / 1024
                for cname in client[dn].list_collection_names():
                    if cname == 'system.profile': continue
                    try:
                        cs = client[dn].command('collStats', cname)
                        sz = cs.get('storageSize', 0) / 1024 / 1024
                        if sz >= 50:
                            big_colls.append((dn, cname, sz, cs.get('count', 0)))
                    except Exception: pass
            except Exception: pass
        if big_colls:
            big_colls.sort(key=lambda x: -x[2])
            warn('共 %d 个 ≥50MB 的大集合 (取前 3):' % len(big_colls))
            for dn, cn, sz, cnt in big_colls[:3]:
                warn('  %s.%s [%.1fMB, %d 文档]' % (dn, cn, sz, cnt))
        else:
            ok('业务集合都 <50MB')
        info('总存储大小: %.1fMB' % total_size_mb)

        # ---------- 总结 ----------
        lines.append(''); lines.append('━━━ 总结 ━━━')
        nc = sum(1 for x in issues if x[0] == 2)
        nw = sum(1 for x in issues if x[0] == 1)
        nt = sum(1 for x in issues if x[0] == 0)
        if not issues:
            lines.append('  🎉 MongoDB 健康状况良好!')
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
        return mw.returnData(True, 'ok', '\n'.join(lines))
    finally:
        pass  # MongoDB client 是单例复用, 不关


# 测试
def test(args):
    sid = args['sid']
    t = nosqlMongodbCtr()
    print(t.get_options())
    print("test")
    return 'ok'
