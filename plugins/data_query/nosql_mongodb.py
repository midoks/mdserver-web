# coding:utf-8

import sys
import io
import os
import time
import re
import pymongo
import json
import yaml
import threading

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
    _lock = threading.RLock()

    def inner():
        if cls not in _instance:
            with _lock:
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


def _close_mongo_client(client):
    if client is not None:
        try:
            client.close()
        except Exception:
            pass


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
        self.__DB_CONN = None
        self.__DB_CONN_KEY = None
        self.__DB_CONN_ID = None
        self.__DB_CONN_LOCK = threading.RLock()


    def mgdb_conn(self):
        with self.__DB_CONN_LOCK:
            if self.__DB_HOST in ['127.0.0.1', 'localhost']:
                mgdb_path = "{}/mongodb".format(mw.getServerDir())
                if not os.path.exists(mgdb_path):
                    self.__DB_STATUS = 'not_installed'
                    return False

            params = {
                'host': self.__DB_HOST,
                'directConnection': True,
                'serverSelectionTimeoutMS': 3000,
            }
            if self.__DB_LOCAL:
                params['port'] = int(self.__DB_PORT)
                if self.__DB_USER and self.__DB_USER != 'None':
                    params['username'] = self.__DB_USER
                    params['password'] = self.__DB_PASS
                identity = '%s@%s:%s' % (self.__DB_USER or 'anonymous', self.__DB_HOST, self.__DB_PORT)
            else:
                if not self.__config:
                    self.__DB_STATUS = 'not_installed'
                    return False
                self.__DB_PORT = int(getConfPort())
                params['port'] = self.__DB_PORT
                if getConfAuth() != 'disabled':
                    mg_root = pSqliteDb('config').where('id=?', (1,)).getField('mg_root')
                    params['username'] = 'root'
                    params['password'] = mg_root
                identity = 'root@%s:%s' % (self.__DB_HOST, self.__DB_PORT) if 'username' in params else '%s:%s' % (self.__DB_HOST, self.__DB_PORT)

            conn_key = tuple(sorted(params.items()))
            if self.__DB_CONN is not None and self.__DB_CONN_KEY == conn_key:
                self.__DB_STATUS = None
                self.__DB_ERR = None
                return self.__DB_CONN

            new_client = None
            self.__DB_ERR = None
            try:
                new_client = pymongo.MongoClient(**params)
                new_client.admin.command('ping')
                # 节点处于 recovering/startup 时 ping 仍会成功，但读写会抛 NotPrimaryError
                try:
                    hello = new_client.admin.command('hello')
                except Exception:
                    # MongoDB < 5.0 没有 hello 命令
                    hello = new_client.admin.command('isMaster')
                if not isinstance(hello, dict) or not (hello.get('isWritablePrimary') or hello.get('ismaster') or hello.get('secondary')):
                    self.__DB_ERR = 'MongoDB 节点当前不是 primary 或 secondary 状态'
                    self.__DB_STATUS = 'not_running'
                    _close_mongo_client(new_client)
                    return False
            except pymongo.errors.ConnectionFailure:
                self.__DB_STATUS = 'not_running'
                if new_client is not None:
                    _close_mongo_client(new_client)
                return False
            except Exception:
                self.__DB_STATUS = 'not_running'
                if new_client is not None:
                    _close_mongo_client(new_client)
                return False

            old_client = self.__DB_CONN
            self.__DB_CONN = new_client
            self.__DB_CONN_KEY = conn_key
            self.__DB_CONN_ID = identity
            self.__DB_STATUS = None
            self.__DB_ERR = None
            if old_client is not None and old_client is not new_client:
                _close_mongo_client(old_client)
            return self.__DB_CONN

    def get_connection_id(self):
        with self.__DB_CONN_LOCK:
            return self.__DB_CONN_ID or '%s:%s' % (self.__DB_HOST, self.__DB_PORT)

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
        with self.__DB_CONN_LOCK:
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
_HEALTH_SNAPSHOT_TTL = 3600
_HEALTH_SNAPSHOT_CAPACITY = 128
_HEALTH_MAX_DATABASES = 20
_HEALTH_MAX_COLLECTIONS_PER_DB = 50
_HEALTH_MAX_COLLECTIONS = 200
_health_snapshot_lock = threading.RLock()
_health_snapshots = {}


def _counter_value(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError('计数器不是数值')
    result = int(value)
    if result < 0:
        raise ValueError('计数器不能为负数')
    return result


def _update_health_snapshot(instance_key, counters):
    current = {}
    for name, value in counters.items():
        try:
            current[name] = _counter_value(value)
        except (ValueError, TypeError, OverflowError):
            continue

    now = time.time()
    monotonic = time.monotonic()
    with _health_snapshot_lock:
        for key in list(_health_snapshots.keys()):
            entry = _health_snapshots[key]
            if now < entry['last_used'] or now - entry['last_used'] > _HEALTH_SNAPSHOT_TTL:
                del _health_snapshots[key]

        previous = _health_snapshots.get(instance_key)
        baseline_reset = False
        elapsed = 0
        if previous is not None:
            elapsed = monotonic - previous['monotonic']
            baseline_reset = elapsed <= 0
            if not baseline_reset:
                for name, value in current.items():
                    if name in previous['counters'] and value < previous['counters'][name]:
                        baseline_reset = True
                        break

        can_diff = previous is not None and not baseline_reset
        deltas = {}
        rates = {}
        if can_diff:
            for name, value in current.items():
                if name in previous['counters']:
                    delta = value - previous['counters'][name]
                    deltas[name] = delta
                    rates[name] = delta / elapsed

        _health_snapshots[instance_key] = {
            'counters': dict(current),
            'monotonic': monotonic,
            'last_used': now,
        }
        while len(_health_snapshots) > _HEALTH_SNAPSHOT_CAPACITY:
            oldest = min(_health_snapshots, key=lambda key: _health_snapshots[key]['last_used'])
            del _health_snapshots[oldest]

        return {
            'cumulative': current,
            'delta': deltas if can_diff else None,
            'rates': rates if can_diff else None,
            'elapsed': elapsed if can_diff else 0,
            'first_sample': previous is None,
            'baseline_reset': previous is not None and not can_diff,
        }


def _lock_wait_count(server_status):
    locks = server_status.get('locks')
    if not isinstance(locks, dict):
        raise ValueError('locks 不可用')
    total = 0
    found = False
    def add_wait_values(values):
        nonlocal total, found
        for value in values:
            if isinstance(value, dict):
                add_wait_values(value.values())
            else:
                total += _counter_value(value)
                found = True

    for scope_metrics in locks.values():
        if not isinstance(scope_metrics, dict):
            continue
        wait_count = scope_metrics.get('acquireWaitCount')
        if wait_count is None:
            continue
        if not isinstance(wait_count, dict):
            raise ValueError('locks.*.acquireWaitCount 格式无效')
        # 常见格式为 {r: 0, w: 0}; 兼容个别版本/作用域的嵌套模式。
        add_wait_values(wait_count.values())
    if not found:
        raise ValueError('locks.*.acquireWaitCount 不可用')
    return total


def _controlled_health_scan(client):
    result = {
        'databases_total': 0,
        'databases_scanned': 0,
        'collections_found': 0,
        'collections_scanned': 0,
        'collections_skipped': 0,
        'truncated': False,
        'failures': 0,
        'first_error': None,
        'profiles': [],
        'unused_index_count': 0,
        'unused_index_examples': [],
        'big_collections': [],
        'total_storage_mb': 0.0,
        'complete': False,
    }

    def record_failure(stage, exc):
        result['failures'] += 1
        if result['first_error'] is None:
            message = str(exc).replace('\n', ' ')[:240]
            result['first_error'] = '%s: %s' % (stage, message)

    try:
        database_names = client.list_database_names()
    except Exception as exc:
        record_failure('list_database_names', exc)
        return result

    business_names = [name for name in database_names if name not in ('admin', 'config', 'local')]
    result['databases_total'] = len(business_names)
    selected_names = business_names[:_HEALTH_MAX_DATABASES]
    if len(business_names) > len(selected_names):
        result['truncated'] = True

    stop = False
    for database_name in selected_names:
        if stop:
            break
        result['databases_scanned'] += 1
        try:
            database = client[database_name]
        except Exception as exc:
            record_failure('%s: 获取数据库句柄' % database_name, exc)
            continue

        try:
            profile = database.command('profile', -1)
            level = _counter_value(profile.get('was'))
            result['profiles'].append((database_name, level))
        except Exception as exc:
            record_failure('%s: profile' % database_name, exc)

        try:
            database_stats = database.command('dbStats')
            result['total_storage_mb'] += _counter_value(database_stats.get('storageSize')) / 1024 / 1024
        except Exception as exc:
            record_failure('%s: dbStats' % database_name, exc)

        try:
            collection_names = database.list_collection_names()
        except Exception as exc:
            record_failure('%s: list_collection_names' % database_name, exc)
            continue

        collection_names = [name for name in collection_names if not name.startswith('system.')]
        result['collections_found'] += len(collection_names)
        selected_collections = collection_names[:_HEALTH_MAX_COLLECTIONS_PER_DB]
        if len(collection_names) > len(selected_collections):
            result['collections_skipped'] += len(collection_names) - len(selected_collections)
            result['truncated'] = True

        for collection_index, collection_name in enumerate(selected_collections):
            if result['collections_scanned'] >= _HEALTH_MAX_COLLECTIONS:
                result['collections_skipped'] += len(selected_collections) - collection_index
                result['truncated'] = True
                stop = True
                break
            result['collections_scanned'] += 1

            try:
                collection_stats = database.command('collStats', collection_name)
                storage_size = _counter_value(collection_stats.get('storageSize')) / 1024 / 1024
                document_count = _counter_value(collection_stats.get('count'))
                if storage_size >= 50:
                    result['big_collections'].append((database_name, collection_name, storage_size, document_count))
            except Exception as exc:
                record_failure('%s.%s: collStats' % (database_name, collection_name), exc)

            try:
                cursor = database[collection_name].aggregate([{'$indexStats': {}}])
                for index_doc in cursor:
                    if not isinstance(index_doc, dict):
                        raise ValueError('$indexStats 游标文档格式无效')
                    index_name = index_doc.get('name')
                    accesses = index_doc.get('accesses')
                    if not isinstance(index_name, str) or not isinstance(accesses, dict):
                        raise ValueError('$indexStats 缺少 name/accesses')
                    operations = _counter_value(accesses.get('ops'))
                    if operations == 0 and index_name != '_id_':
                        result['unused_index_count'] += 1
                        if len(result['unused_index_examples']) < 3:
                            result['unused_index_examples'].append((database_name, collection_name, index_name))
            except Exception as exc:
                record_failure('%s.%s: $indexStats' % (database_name, collection_name), exc)

    result['complete'] = not result['truncated'] and result['failures'] == 0
    return result


def get_health(args):
    sid = args.get('sid', 0)
    ctr = nosqlMongodbCtr()
    instance = ctr.getInstanceBySid(sid)
    client, err = ctr._connect(sid)
    if err: return err

    try:
        ss = client.admin.command('serverStatus')
    except Exception as exc:
        return mw.returnData(False, 'serverStatus 获取失败: %s' % exc)

    counters = {}

    def add_counter(source, source_key, target_key):
        try:
            counters[target_key] = _counter_value(source.get(source_key))
        except (ValueError, TypeError, OverflowError, AttributeError):
            pass

    add_counter(ss, 'uptime', 'uptime')
    for key in ('totalCreated', 'rejected'):
        add_counter(ss.get('connections', {}), key, 'connections.' + key)
    for key in ('insert', 'query', 'update', 'delete', 'command', 'getmore'):
        add_counter(ss.get('opcounters', {}), key, 'opcounters.' + key)
    for key in ('bytesIn', 'bytesOut', 'numSlowDNSOperations', 'numSlowSSLOperations'):
        add_counter(ss.get('network', {}), key, 'network.' + key)
    for key in ('journaledCommits', 'commitsInWriteLock'):
        add_counter(ss.get('dur', {}), key, 'dur.' + key)

    wt = ss.get('wiredTiger', {})
    wt_cache = wt.get('cache', {}) if isinstance(wt, dict) else {}
    wt_transaction = wt.get('transaction', {}) if isinstance(wt, dict) else {}
    add_counter(wt_cache, 'pages requested from the cache', 'wt.pagesRequested')
    add_counter(wt_cache, 'pages read into cache', 'wt.pagesRead')
    add_counter(wt_transaction, 'transaction checkpoint number', 'wt.checkpointNumber')
    add_counter(wt_transaction, 'transaction checkpoint total time (msecs)', 'wt.checkpointTotalMs')

    lock_wait_total = None
    current_lock_waits = None
    lock_error = None
    try:
        lock_wait_total = _lock_wait_count(ss)
        counters['locks.acquireWaitCount'] = lock_wait_total
    except Exception as exc:
        lock_error = str(exc)

    # 新版实例可能不再提供累计 acquireWaitCount，改查当前等待锁的操作数。
    if lock_wait_total is None:
        try:
            current_rows = list(client.admin.aggregate([
                {'$currentOp': {'allUsers': True, 'idleConnections': False}},
                {'$match': {'waitingForLock': True}},
                {'$count': 'waiting'},
            ]))
            current_lock_waits = _counter_value(current_rows[0].get('waiting')) if current_rows else 0
        except Exception as exc:
            lock_error = '%s; $currentOp: %s' % (lock_error, exc)

    snapshot_key = '%s|%s' % (sid, instance.get_connection_id())
    snapshot = _update_health_snapshot(snapshot_key, counters)
    scan = _controlled_health_scan(client)

    lines = []
    issues = []
    cur_section = ''

    def section(title):
        nonlocal cur_section
        cur_section = title
        lines.append(''); lines.append('━━━ %s ━━━' % title)
    def ok(msg):       lines.append('  ✅ ' + msg)
    def critical(msg): issues.append(('critical', cur_section, '🚨 ' + msg)); lines.append('  🚨 ' + msg)
    def warn(msg):     issues.append(('warning', cur_section, '⚠️  ' + msg)); lines.append('  ⚠️  ' + msg)
    def tip(msg):      issues.append(('tip', cur_section, '💡 ' + msg)); lines.append('  💡 ' + msg)
    def info(msg):     lines.append('  ℹ️   ' + msg)
    def unknown(msg):  issues.append(('unknown', cur_section, '❓ ' + msg)); lines.append('  ❓ ' + msg)
    def skipped(msg):  issues.append(('unknown', cur_section, '⏭️  ' + msg)); lines.append('  ⏭️  ' + msg)

    has_delta = snapshot['delta'] is not None
    sample_label = '首次采样' if snapshot['first_sample'] else '基线重建'

    # ---------- 0. 基础信息 ----------
    section('基础信息')
    if ss.get('version'):
        info('MongoDB %s' % ss['version'])
    else:
        unknown('MongoDB version 指标不可用')
    upt = counters.get('uptime')
    if upt is None:
        unknown('uptime 指标不可用')
    else:
        info('已运行: %s' % ('%d天%02d:%02d' % (upt//86400, (upt%86400)//3600, (upt%3600)//60)))
    storage_engine = ss.get('storageEngine', {})
    engine_name = storage_engine.get('name') if isinstance(storage_engine, dict) else None
    if engine_name:
        info('存储引擎: %s' % engine_name)
    else:
        unknown('存储引擎指标不可用')
    if snapshot['first_sample']:
        info('计数采样: 首次采样，展示累计值；后续采样展示间隔增量/速率')
    elif snapshot['baseline_reset']:
        info('计数器回退或实例重启，已重建基线；本次按首次采样展示累计值')
    else:
        info('计数采样间隔: %.3f 秒' % snapshot['elapsed'])

    host_mem_mb = 0
    try:
        hi = client.admin.command('hostInfo')
        system = hi.get('system', {})
        host_mem_mb = _counter_value(system.get('memSizeMB'))
        host_cores = _counter_value(system.get('numCores'))
        info('主机: %d核 / %dMB' % (host_cores, host_mem_mb))
    except Exception as exc:
        unknown('hostInfo 指标不可用: %s' % exc)

    # ---------- 1. 连接 ----------
    section('连接')
    cc = ss.get('connections', {})
    try:
        cur_conn = _counter_value(cc.get('current'))
        avail = _counter_value(cc.get('available'))
        total = cur_conn + avail
        total_created = counters.get('connections.totalCreated')
        info('连接: current=%d, available=%d, totalCreated=%s' % (
            cur_conn, avail, total_created if total_created is not None else 'unknown'))
        if total <= 0:
            unknown('连接总数为 0，无法计算连接水位')
        else:
            conn_pct = cur_conn / total * 100
            if conn_pct >= 80:
                warn('连接数水位 %.1f%% 偏高' % conn_pct)
            else:
                ok('连接数水位 %.1f%%' % conn_pct)
        if total_created is None:
            unknown('connections.totalCreated 指标不可用')
    except Exception as exc:
        unknown('connections.current/available 指标不可用: %s' % exc)

    if has_delta:
        created_delta = snapshot['delta'].get('connections.totalCreated')
        created_rate = snapshot['rates'].get('connections.totalCreated')
        if created_delta is not None:
            info('新建连接: 间隔新增=%d, 速率=%.2f 次/秒' % (created_delta, created_rate))

    rejected = counters.get('connections.rejected')
    if rejected is None:
        unknown('connections.rejected 指标不可用')
    elif not has_delta:
        info('连接拒绝累计=%d（%s，仅建立基线）' % (rejected, sample_label))
    else:
        rejected_delta = snapshot['delta'].get('connections.rejected')
        rejected_rate = snapshot['rates'].get('connections.rejected')
        if rejected_delta is None:
            unknown('连接拒绝缺少上一采样基线')
        else:
            info('连接拒绝: 累计=%d, 间隔新增=%d, 速率=%.2f 次/秒' % (
                rejected, rejected_delta, rejected_rate))
            if rejected_delta > 0:
                critical('采样间隔新增拒绝 %d 次新连接, 请检查 maxConns' % rejected_delta)

    # ---------- 2. 内存 ----------
    section('内存 / WiredTiger')
    mem = ss.get('mem', {})
    try:
        resident_mb = _counter_value(mem.get('resident'))
        virt_mb = _counter_value(mem.get('virtual'))
        info('mem.resident=%dMB, virtual=%dMB' % (resident_mb, virt_mb))
    except Exception as exc:
        unknown('mem 指标不可用: %s' % exc)

    if engine_name and str(engine_name).lower() != 'wiredtiger':
        info('当前存储引擎不是 WiredTiger，跳过 WT 专属指标')
    elif not isinstance(wt_cache, dict) or not wt_cache:
        unknown('WiredTiger cache 指标不可用')
    else:
        try:
            max_bytes = _counter_value(wt_cache.get('maximum bytes configured'))
            cur_bytes = _counter_value(wt_cache.get('bytes currently in the cache'))
            dirty = _counter_value(wt_cache.get('tracked dirty bytes in the cache'))
            info('WT cache max=%.0fMB, current=%.0fMB, dirty=%.0fMB (%.1f%%)' % (
                max_bytes/1024/1024, cur_bytes/1024/1024, dirty/1024/1024,
                dirty/cur_bytes*100 if cur_bytes else 0))
            if max_bytes > 0 and host_mem_mb > 0:
                cache_pct = max_bytes / (host_mem_mb*1024*1024) * 100
                if cache_pct < 40:
                    warn('WT cache sizeOnly 只占物理内存 %.1f%%, 建议检查是否调到 50%%' % cache_pct)
        except Exception as exc:
            unknown('WiredTiger cache size 指标不可用: %s' % exc)

        pages_requested = counters.get('wt.pagesRequested')
        pages_read = counters.get('wt.pagesRead')
        if pages_requested is None or pages_read is None or pages_requested <= 0 or pages_read > pages_requested:
            unknown('WiredTiger 页面请求/读取指标不足或无效，无法可靠计算 cache 命中率')
        else:
            cache_hit = (pages_requested - pages_read) / pages_requested * 100
            info('WT cache 累计命中率: %.2f%% (pages requested/read)' % cache_hit)
            if has_delta:
                requested_delta = snapshot['delta'].get('wt.pagesRequested')
                read_delta = snapshot['delta'].get('wt.pagesRead')
                if requested_delta is None or read_delta is None:
                    unknown('WiredTiger 命中率缺少上一采样基线')
                elif requested_delta > 0 and 0 <= read_delta <= requested_delta:
                    interval_hit = (requested_delta - read_delta) / requested_delta * 100
                    info('WT cache 间隔命中率: %.2f%%' % interval_hit)
                elif requested_delta < 0 or read_delta < 0 or read_delta > requested_delta:
                    unknown('WiredTiger 间隔页面指标无效，无法计算命中率')
                else:
                    info('WT cache 本采样间隔无页面请求')

    # ---------- 3. opcounters / QPS ----------
    section('opcounters / 操作')
    op_names = ('insert', 'query', 'update', 'delete', 'command', 'getmore')
    op_keys = ['opcounters.' + name for name in op_names]
    if not all(key in counters for key in op_keys):
        unknown('opcounters 指标不完整，无法计算操作增量/QPS')
    else:
        info('累计操作: %s' % ' '.join('%s=%d' % (name, counters['opcounters.' + name]) for name in op_names))
        if not has_delta:
            info('操作计数为%s，本采样不计算 QPS' % sample_label)
        elif not all(key in snapshot['delta'] for key in op_keys):
            unknown('opcounters 缺少上一采样基线')
        else:
            op_deltas = [snapshot['delta'][key] for key in op_keys]
            total_delta = sum(op_deltas)
            info('间隔操作增量: %s' % ' '.join('%s=%d' % item for item in zip(op_names, op_deltas)))
            info('间隔总操作=%d, QPS=%.2f' % (total_delta, total_delta / snapshot['elapsed']))

    net = ss.get('network', {})
    if not isinstance(net, dict) or 'network.bytesIn' not in counters or 'network.bytesOut' not in counters:
        unknown('network.bytesIn/bytesOut 指标不可用')
    else:
        info('网络累计: bytesIn=%d, bytesOut=%d' % (counters['network.bytesIn'], counters['network.bytesOut']))
        if has_delta and 'network.bytesIn' in snapshot['delta'] and 'network.bytesOut' in snapshot['delta']:
            info('网络间隔增量: bytesIn=%d (%.1f B/s), bytesOut=%d (%.1f B/s)' % (
                snapshot['delta']['network.bytesIn'], snapshot['rates']['network.bytesIn'],
                snapshot['delta']['network.bytesOut'], snapshot['rates']['network.bytesOut']))
    if has_delta:
        slow_network_delta = sum(snapshot['delta'].get(key, 0) for key in (
            'network.numSlowDNSOperations', 'network.numSlowSSLOperations'))
        if slow_network_delta > 0:
            warn('采样间隔有 %d 次慢速 DNS / SSL 操作, 检查网络环境' % slow_network_delta)

    # ---------- 4. 锁 / 死锁 ----------
    section('锁 / 死锁')
    if lock_wait_total is not None:
        info('累计锁等待次数(Global/Database/Collection 等): %d' % lock_wait_total)
        if not has_delta:
            info('锁等待为%s，本采样不以历史累计值告警' % sample_label)
        elif 'locks.acquireWaitCount' not in snapshot['delta']:
            unknown('锁等待缺少上一采样基线')
        else:
            wait_delta = snapshot['delta']['locks.acquireWaitCount']
            wait_rate = snapshot['rates']['locks.acquireWaitCount']
            info('锁等待间隔新增=%d, 速率=%.2f 次/秒' % (wait_delta, wait_rate))
            if wait_delta > 100:
                warn('采样间隔锁等待较多, 应用层可能有热点文档/长事务')
                tip('排查: db.currentOp({"waitingForLock": true})')
            else:
                ok('采样间隔锁等待增量正常')
    elif current_lock_waits is not None:
        info('当前等待锁的操作数($currentOp): %d' % current_lock_waits)
        if current_lock_waits > 0:
            warn('当前有 %d 个操作等待锁, 请检查热点文档和长事务' % current_lock_waits)
            tip('排查: db.currentOp({"waitingForLock": true})')
        else:
            ok('当前没有等待锁的操作')
    else:
        unknown('锁等待指标不可用: %s' % lock_error)

    # ---------- 5. 持久化 / journal ----------
    section('持久化 / Checkpoint')
    # dur 是旧存储引擎指标；WiredTiger 使用自身 transaction checkpoint 计数。
    dur_available = 'dur.journaledCommits' in counters and 'dur.commitsInWriteLock' in counters
    checkpoint_count = counters.get('wt.checkpointNumber')
    checkpoint_ms = counters.get('wt.checkpointTotalMs')
    if dur_available:
        info('journal commits=%d, commitsInWriteLock=%d' % (
            counters['dur.journaledCommits'], counters['dur.commitsInWriteLock']))
        if has_delta and snapshot['delta'].get('dur.commitsInWriteLock', 0) > 0:
            tip('采样间隔有 commits 在 writeLock 中完成, journal 可能成为瓶颈')
            tip('mongod.conf: storage.journal.commitIntervalMs 可适当调大 (默认 300ms)')
    elif checkpoint_count is not None and checkpoint_ms is not None:
        info('WT checkpoint 累计: number=%d, totalTime=%dms' % (checkpoint_count, checkpoint_ms))
        if not has_delta:
            info('WT checkpoint 为%s，后续采样分析间隔次数和耗时' % sample_label)
        elif 'wt.checkpointNumber' not in snapshot['delta'] or 'wt.checkpointTotalMs' not in snapshot['delta']:
            unknown('WT checkpoint 缺少上一采样基线')
        else:
            count_delta = snapshot['delta']['wt.checkpointNumber']
            ms_delta = snapshot['delta']['wt.checkpointTotalMs']
            info('WT checkpoint 间隔: number=%d, totalTime=%dms' % (count_delta, ms_delta))
            if count_delta > 0:
                avg_ms = ms_delta / count_delta
                if avg_ms >= 1000:
                    warn('WT checkpoint 平均耗时 %.1fms, 请检查磁盘 IO、cache 压力和长事务' % avg_ms)
                else:
                    ok('WT checkpoint 平均耗时 %.1fms' % avg_ms)
            else:
                info('本采样间隔没有新增 WT checkpoint')
    elif engine_name and str(engine_name).lower() == 'wiredtiger':
        skipped('dur journal 为旧存储引擎指标, 当前版本未提供可用的 WT checkpoint 计数')
    else:
        unknown('dur journal 指标在当前版本不可用或无效')
    if isinstance(storage_engine, dict) and storage_engine.get('readOnly'):
        critical('storageEngine 是 readOnly! 磁盘可能只读 / fsync 锁')

    # ---------- 6. 单次受控扫描 ----------
    section('受控扫描范围')
    info('业务数据库: 实际扫描 %d/%d；集合: 实际扫描 %d，已展开发现 %d，已知上限跳过 %d' % (
        scan['databases_scanned'], scan['databases_total'], scan['collections_scanned'],
        scan['collections_found'], scan['collections_skipped']))
    info('扫描上限: 数据库=%d, 单库集合=%d, 全局集合=%d；截断=%s' % (
        _HEALTH_MAX_DATABASES, _HEALTH_MAX_COLLECTIONS_PER_DB,
        _HEALTH_MAX_COLLECTIONS, '是' if scan['truncated'] else '否'))
    if scan['truncated']:
        skipped('扫描范围被上限截断，未扫描部分不作“无异常”结论')
    if scan['failures']:
        unknown('受控扫描失败数=%d；首个错误: %s' % (scan['failures'], scan['first_error']))
    else:
        info('受控扫描失败数=0；首个错误: 无')

    section('Profiling / system.profile')
    enabled_profiles = [(name, level) for name, level in scan['profiles'] if level > 0]
    for database_name, level in enabled_profiles:
        info('%s profiling level=%d' % (database_name, level))
    if scan['profiles']:
        info('Profiling 检查: 成功 %d 库，开启 %d 库；system.* 集合不进入业务扫描' % (
            len(scan['profiles']), len(enabled_profiles)))
    else:
        skipped('没有成功获取业务数据库 Profiling 指标')

    # ---------- 7. 索引 / schema ----------
    section('索引 / schema')
    if scan['unused_index_count']:
        warn('发现至少 %d 个自统计重置以来 accesses.ops=0 的非 _id_ 索引；需覆盖完整业务周期并核实用途，不要仅凭本报告删除' % scan['unused_index_count'])
        for database_name, collection_name, index_name in scan['unused_index_examples']:
            tip('%s.%s 索引 %s 当前 accesses.ops=0' % (database_name, collection_name, index_name))
    elif scan['complete']:
        ok('完整扫描未发现 accesses.ops=0 的非 _id_ 索引')
    else:
        skipped('索引扫描未完整成功，无法确认是否存在未使用索引')

    # ---------- 8. 大集合 / 膨胀 ----------
    section('大集合 / 膨胀')
    big_colls = sorted(scan['big_collections'], key=lambda item: -item[2])
    if big_colls:
        warn('发现至少 %d 个 ≥50MB 的集合（仅作容量/性能排查提示，取前 3）' % len(big_colls))
        for database_name, collection_name, size_mb, count in big_colls[:3]:
            info('  %s.%s [%.1fMB, %d 文档]' % (database_name, collection_name, size_mb, count))
    elif scan['complete']:
        ok('完整扫描未发现 ≥50MB 的业务集合')
    else:
        skipped('集合扫描未完整成功，无法确认是否存在 ≥50MB 的大集合')
    info('已扫描数据库 storageSize 合计: %.1fMB（截断或失败时为部分合计）' % scan['total_storage_mb'])

    # ---------- 总结 ----------
    lines.append(''); lines.append('━━━ 总结 ━━━')
    nc = sum(1 for item in issues if item[0] == 'critical')
    nw = sum(1 for item in issues if item[0] == 'warning')
    nt = sum(1 for item in issues if item[0] == 'tip')
    nu = sum(1 for item in issues if item[0] == 'unknown')
    lines.append('  📊 严重 🚨 %d / 警告 ⚠️  %d / 建议 💡 %d / 未知 ❓ %d (共 %d)' % (
        nc, nw, nt, nu, len(issues)))
    if not issues:
        lines.append('  🎉 MongoDB 健康状况良好!')
    else:
        if nu > 0:
            lines.append('  ❓ 存在查询失败、权限不足、版本不支持或扫描不完整，不能据此判定整体健康')
        if nc > 0:
            lines.append(''); lines.append('  ── 最严重 Top %d ──' % min(nc, 5))
            for item in [item for item in issues if item[0] == 'critical'][:5]:
                lines.append('  %s  [%s]' % (item[2], item[1]))
        lines.append(''); lines.append('  ── 完整清单 (按严重度排序) ──')
        issue_order = {'critical': 0, 'warning': 1, 'tip': 2, 'unknown': 3}
        for kind, sec, txt in sorted(issues, key=lambda item: (issue_order[item[0]], item[1])):
            lines.append('  %s  [%s]' % (txt, sec))
    lines.append('')
    return mw.returnData(True, 'ok', '\n'.join(lines))


# 测试
def test(args):
    sid = args['sid']
    t = nosqlMongodbCtr()
    print(t.get_options())
    print("test")
    return 'ok'
