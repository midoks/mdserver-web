# coding:utf-8

import sys
import io
import os
import time
import re
import threading
import redis

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
class nosqlRedis():

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


    def redis_conn(self, db_idx=0):

        if self.__DB_HOST in ['127.0.0.1', 'localhost']:
            redis_path = "{}/redis".format(mw.getServerDir())
            if not os.path.exists(redis_path):
                self.__DB_STATUS = 'not_installed'
                return False

        if not self.__DB_LOCAL:
            if not self.__config:
                self.__DB_STATUS = 'not_installed'
                return False
            self.__DB_PASS = self.__config['requirepass']
            self.__DB_PORT = int(self.__config['port'])

        # print(self.__DB_HOST,self.__DB_PORT, self.__DB_PASS)
        try:
            redis_pool = redis.ConnectionPool(host=self.__DB_HOST, port=self.__DB_PORT, password=self.__DB_PASS, db=db_idx, socket_timeout=3)
            self.__DB_CONN = redis.Redis(connection_pool=redis_pool)
            self.__DB_CONN.ping()
            self.__DB_STATUS = None
            return self.__DB_CONN
        except redis.exceptions.ConnectionError:
            self.__DB_STATUS = 'not_running'
            return False
        except Exception:
            self.__DB_ERR = mw.getTracebackInfo()
        self.__DB_STATUS = 'not_running'
        return False

    # 连接状态：not_installed 未安装 / not_running 未启动 / None 正常
    def get_status(self):
        return self.__DB_STATUS

    # 获取配置项
    def get_options(self, get=None):

        result = {}
        redis_conf = mw.readFile("{}/redis/redis.conf".format(mw.getServerDir()))
        if not redis_conf: return False

        keys = ["bind", "port", "timeout", "maxclients", "databases", "requirepass", "maxmemory"]
        for k in keys:
            v = ""
            rep = r"\n%s\s+(.+)" % k
            group = re.search(rep, redis_conf)
            if not group:
                if k == "maxmemory":
                    v = "0"
                if k == "maxclients":
                    v = "10000"
                if k == "requirepass":
                    v = ""
            else:
                if k == "maxmemory":
                    v = int(group.group(1).strip("mb"))
                else:
                    v = group.group(1)
            result[k] = v
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
class nosqlRedisCtr():

    def __init__(self):
        pass

    def getInstanceBySid(self, sid = 0):
        instance = nosqlRedis()
        return instance

    def _connect(self, sid, idx=0):
        obj = self.getInstanceBySid(sid)
        conn = obj.redis_conn(idx)
        if conn is False:
            if obj.get_status() == 'not_installed':
                return None, mw.returnData(False, '未安装')
            return None, mw.returnData(False, '未启动')
        return conn, None

    def getList(self, args):

        sid = args['sid']
        redis_instance, err = self._connect(sid, 0)
        if err:
            return err


        redis_info = redis_instance.info()
        is_cluster = redis_info.get("cluster_enabled", 0)
        if is_cluster != 0:
            return mw.returnData(False, "当前不支持连接redis集群！")

        db_num = 16
        if sid != 0:
            db_num = 1000

        result = []
        for x in range(0, db_num):
            data = {}
            data['id'] = x
            data['name'] = 'DB{}'.format(x)
            try:
                redis_instance = self.getInstanceBySid(sid).redis_conn(x)
                data['keynum'] = redis_instance.dbsize()
                result.append(data)
            except:
                break

        return mw.returnData(True,'ok', result)

    def getDbKeyList(self, args):
        p = 1
        size = 10

        if not 'sid' in args:
            return mw.returnData(False, "缺少参数！sid")

        if 'p' in args:
            p = args['p']
        if p < 1:
            p = 1
        if p > 10:
            p = 10

        if 'size' in args:
            size = args['size']

        sid = args['sid']
        idx = args['idx']
        search = '*'
        if 'search' in args and args['search'] != '':
            search = args['search']

        redis_instance, err = self._connect(sid, idx)
        if err:
            return err

        total = redis_instance.dbsize()

        if search != '*':
            keylist = redis_instance.keys(search)
            total = len(keylist)
        else:
            keys = redis_instance.scan(cursor=0, match="{}".format(search), count=p*size)
            keylist = keys[1]

        slist = keylist[(p - 1) * size:p*size]

        items = []
        for key in slist:
            item = {}
            try:
                item['name'] = key.decode()
            except Exception as e:
                item['name'] = str(key)

            item['endtime'] = redis_instance.ttl(key)
            item['type'] = redis_instance.type(key).decode()
            
            if item['type'] == 'string':
                try:
                    item['val'] = redis_instance.get(key).decode()
                except Exception as e:
                    item['val'] = str(redis_instance.get(key))
            elif item['type'] == 'hash':
                if redis_instance.hlen(key) > 500:
                    item['val'] = "数据量过大无法显示！共 {} 条".format(redis_instance.hlen(key))
                else:
                    item['val'] = str(redis_instance.hgetall(key))
            elif item['type'] == 'list':
                if redis_instance.llen(key) > 500:
                    item['val'] = "数据量过大无法显示！共 {} 条".format(redis_instance.llen(key))
                else:
                    item['val'] = str(redis_instance.lrange(key, 0, -1))
            elif item['type'] == 'set':
                if redis_instance.scard(key) > 500:
                    item['val'] = "数据量过大无法显示！共 {} 条".format(redis_instance.scard(key))
                else:
                    item['val'] = str(redis_instance.smembers(key))
            elif item['type'] == 'zset':
                if redis_instance.zcard(key) > 500:
                    item['val'] = "数据量过大无法显示！共 {} 条".format(redis_instance.zcard(key))
                else:
                    item['val'] = str(redis_instance.zrange(key, 0, -1, withscores=True))
            else:
                item['val'] = ''

            try:
                item['len'] = redis_instance.strlen(key)
            except:
                item['len'] = len(item['val'])
            items.append(item)


        page_args = {}
        page_args['count'] = total
        page_args['tojs'] = 'redisGetKeyList'
        page_args['p'] = p
        page_args['row'] = size

        rdata = {}
        rdata['page'] = mw.getPage(page_args)
        rdata['data'] = items
        return mw.returnData(True,'ok',rdata)

    def setKv(self,args):
        if not 'name' in args:
            return mw.returnData(False, "缺少参数！name")
        if not 'val' in args:
            return mw.returnData(False, "缺少参数！val")
        if not 'idx' in args:
            return mw.returnData(False, "缺少参数！idx")

        sid = args['sid']
        idx = args['idx']

        name = args["name"]
        val = args["val"]
        endtime = args["endtime"]

        redis_instance, err = self._connect(sid, idx)
        if err:
            return err

        redis_info = redis_instance.info()
        if redis_info['role'] == 'slave':
            return mw.returnData(False,'从库不能写操作!')

        if endtime != '0':
            redis_instance.set(name, val, int(endtime))
        else:
            redis_instance.set(name, val)

        return mw.returnData(True,'操作成功')

    def delVal(self, args):
        sid = args['sid']
        idx = args['idx']
        name = args["name"]
        redis_instance, err = self._connect(sid, idx)
        if err:
            return err

        redis_info = redis_instance.info()
        if redis_info['role'] == 'slave':
            return mw.returnData(False,'从库不能删除操作!')

        redis_instance.delete(name)
        return mw.returnData(True,'操作成功')

    def batchDelVal(self, args):
        sid = args['sid']
        idx = args['idx']
        keys = args["keys"]
        redis_instance, err = self._connect(sid, idx)
        if err:
            return err

        redis_info = redis_instance.info()
        if redis_info['role'] == 'slave':
            return mw.returnData(False,'从库不能删除操作!')

        for k in keys:
            redis_instance.delete(k)
        return mw.returnData(True,'操作成功')

    def clearFlushDB(self, args):

        sid = args['sid']
        idxs = args['idxs']

        for idx in idxs:
            redis_instance, err = self._connect(sid, idx)
            if err:
                return err

            redis_info = redis_instance.info()
            if redis_info['role'] == 'slave':
                return mw.returnData(False,'从库不能清空操作!')

            redis_instance.flushdb()

        return mw.returnData(True,'操作成功')


# ---------------------------------- run ----------------------------------
# 获取 redis databases 列表
def get_list(args):
    t = nosqlRedisCtr()
    return t.getList(args)

# 获取 redis key 列表
def get_dbkey_list(args):
    t = nosqlRedisCtr()
    return t.getDbKeyList(args)


def set_kv(args):
    t = nosqlRedisCtr()
    return t.setKv(args)


def del_val(args):
    t = nosqlRedisCtr()
    return t.delVal(args)

def batch_del_val(args):
    t = nosqlRedisCtr()
    return t.batchDelVal(args)

def clear_flushdb(args):
    t = nosqlRedisCtr()
    return t.clearFlushDB(args)


# ---------------- Redis 健康检查 ----------------
_REDIS_HEALTH_SNAPSHOTS = {}
_REDIS_HEALTH_SNAPSHOT_LOCK = threading.Lock()
_REDIS_HEALTH_SNAPSHOT_TTL = 6 * 3600
_REDIS_HEALTH_SNAPSHOT_CAPACITY = 256


def _redis_health_instance_key(sid, client):
    pool = getattr(client, 'connection_pool', None)
    kwargs = getattr(pool, 'connection_kwargs', {}) or {}
    return '%s|%s:%s|db=%s|socket=%s' % (
        sid, kwargs.get('host', 'unknown'), kwargs.get('port', 'unknown'),
        kwargs.get('db', 0), kwargs.get('unix_socket_path', ''))


def _redis_health_counter_snapshot(key, counters, uptime=None):
    """保存轻量计数基线, 返回首轮/重置状态及间隔增量和速率."""
    now = time.time()
    current = {str(k): float(v) for k, v in counters.items() if isinstance(v, (int, float))}
    with _REDIS_HEALTH_SNAPSHOT_LOCK:
        expired = [k for k, v in _REDIS_HEALTH_SNAPSHOTS.items()
                   if now - v['time'] > _REDIS_HEALTH_SNAPSHOT_TTL]
        for old_key in expired:
            _REDIS_HEALTH_SNAPSHOTS.pop(old_key, None)
        if key not in _REDIS_HEALTH_SNAPSHOTS and len(_REDIS_HEALTH_SNAPSHOTS) >= _REDIS_HEALTH_SNAPSHOT_CAPACITY:
            oldest = min(_REDIS_HEALTH_SNAPSHOTS, key=lambda k: _REDIS_HEALTH_SNAPSHOTS[k]['time'])
            _REDIS_HEALTH_SNAPSHOTS.pop(oldest, None)
        previous = _REDIS_HEALTH_SNAPSHOTS.get(key)
        _REDIS_HEALTH_SNAPSHOTS[key] = {'time': now, 'counters': current, 'uptime': uptime}

    if previous is None:
        return {'first': True, 'reset': False, 'reason': '', 'elapsed': 0, 'delta': {}, 'rate': {}}
    elapsed = now - previous['time']
    old = previous['counters']
    restarted = uptime is not None and previous.get('uptime') is not None and uptime < previous['uptime']
    rolled_back = any(k in old and current[k] < old[k] for k in current)
    reset = elapsed <= 0 or restarted or rolled_back
    if reset:
        reason = 'restart' if restarted else ('rollback' if rolled_back else 'time')
        return {'first': False, 'reset': True, 'reason': reason, 'elapsed': max(elapsed, 0), 'delta': {}, 'rate': {}}
    delta = {k: v - old.get(k, v) for k, v in current.items()}
    rate = {k: v / elapsed for k, v in delta.items()}
    return {'first': False, 'reset': False, 'reason': '', 'elapsed': elapsed, 'delta': delta, 'rate': rate}


def get_health(args):
    sid = args.get('sid', 0)
    ctr = nosqlRedisCtr()
    c, err = ctr._connect(sid)
    if err: return err

    lines = []
    issues = []  # [(level, section, text)] level: 2=严重 1=警告 0=建议 -1=未知
    cur_section = ''

    def section(title):
        nonlocal cur_section
        cur_section = title
        lines.append(''); lines.append('━━━ %s ━━━' % title)
    def ok(msg):       lines.append('  ✅ ' + msg)
    def critical(msg): issues.append((2, cur_section, '🚨 ' + msg)); lines.append('  🚨 ' + msg)
    def warn(msg):     issues.append((1, cur_section, '⚠️  ' + msg)); lines.append('  ⚠️  ' + msg)
    def tip(msg):      issues.append((0, cur_section, '💡 ' + msg)); lines.append('  💡 ' + msg)
    def unknown(msg):  issues.append((-1, cur_section, '❓ ' + msg)); lines.append('  ❓ ' + msg)
    def skipped(msg):  lines.append('  ⏭️  ' + msg)
    def info(msg):     lines.append('  ℹ️   ' + msg)

    def as_int(value):
        try:
            if value is None: return None
            return int(value)
        except (TypeError, ValueError, OverflowError):
            return None

    def as_float(value):
        try:
            if value is None: return None
            return float(value)
        except (TypeError, ValueError, OverflowError):
            return None

    def as_text(value):
        if value is None: return None
        if isinstance(value, bytes):
            return value.decode('utf-8', 'replace')
        return str(value)

    def status_value(name):
        value = as_text(rinfo.get(name))
        return value.lower() if value is not None else None

    def slowlog_text(value):
        if isinstance(value, bytes):
            return value.decode('utf-8', 'replace')
        if isinstance(value, (list, tuple)):
            return ' '.join(slowlog_text(item) for item in value)
        if value is None:
            return ''
        return str(value)

    try:
        rinfo = c.info()
        if not isinstance(rinfo, dict):
            return mw.returnData(False, 'Redis 健康检查异常: INFO 返回格式无效')

        # ---------- 0. 基础信息 / 计数基线 ----------
        section('基础信息')
        info('Redis %s' % (as_text(rinfo.get('redis_version')) or 'unknown'))
        upt = as_int(rinfo.get('uptime_in_seconds'))
        if upt is None or upt < 0:
            unknown('uptime_in_seconds 缺失或无效, 无法识别实例重启')
            upt_for_qps = None
        else:
            upt_for_qps = max(upt, 1)
            info('已运行: %s' % ('%d天%02d:%02d' % (upt//86400, (upt%86400)//3600, (upt%3600)//60)))
        info('mode: %s, tcp_port: %s' % (
            as_text(rinfo.get('redis_mode')) or 'standalone', as_text(rinfo.get('tcp_port')) or 'unknown'))

        counter_names = ('rejected_connections', 'evicted_keys', 'keyspace_hits',
                         'keyspace_misses', 'total_commands_processed')
        counters = {}
        for name in counter_names:
            value = as_int(rinfo.get(name))
            if value is not None and value >= 0:
                counters[name] = value
        instance_key = _redis_health_instance_key(sid, c)
        snapshot = _redis_health_counter_snapshot(instance_key, counters, upt)
        if snapshot['first']:
            info('计数快照: 首次采样, 仅显示累计值, 不根据历史累计触发当前增量告警')
        elif snapshot['reset']:
            info('计数快照: 检测到实例重启/计数回退/时间异常, 已重建基线, 本轮不计算增量')
        else:
            info('计数快照: 采样间隔 %.2fs, 显示间隔增量及速率' % snapshot['elapsed'])

        def counter_text(name, label):
            value = counters.get(name)
            if value is None:
                return None
            text = '%s: 累计=%d' % (label, value)
            if name in snapshot['delta']:
                text += ', 增量=%+d' % snapshot['delta'][name]
                if name in snapshot['rate']:
                    text += ', 速率=%.2f/s' % snapshot['rate'][name]
            elif not snapshot['first'] and not snapshot['reset']:
                text += ', 增量=unknown (缺少上一轮的同项基线)'
            return text

        # ---------- 1. 连接 ----------
        section('连接')
        cc = as_int(rinfo.get('connected_clients'))
        blocked = as_int(rinfo.get('blocked_clients'))
        maxc = as_int(rinfo.get('maxclients'))
        info('connected_clients=%s, blocked_clients=%s, maxclients=%s' % (
            cc if cc is not None else 'unknown', blocked if blocked is not None else 'unknown',
            maxc if maxc is not None else 'unknown'))
        rejected_text = counter_text('rejected_connections', 'rejected_connections')
        if rejected_text is None:
            unknown('rejected_connections 缺失或无效, 无法判断新连接拒绝情况')
        else:
            info(rejected_text)
        rejected_delta = snapshot['delta'].get('rejected_connections')
        if rejected_delta is not None and rejected_delta > 0:
            critical('本间隔新增拒绝 %d 次新连接! 客户端太多或 maxclients 太小' % rejected_delta)
            critical('请结合连接水位调整 maxclients, 并排查客户端连接泄漏')
        if blocked is None or blocked < 0:
            unknown('blocked_clients 缺失或无效')
        elif blocked > 0:
            warn('有 %d 个客户端在阻塞 (BRPOP/BLPOP/BZPOPMIN, 属正常; 太多要排查)' % blocked)
        if cc is None or cc < 0:
            unknown('connected_clients 缺失或无效')
        elif maxc is None or maxc <= 0:
            unknown('maxclients 缺失或无效, 无法计算连接水位')
        else:
            cc_pct = cc / maxc * 100
            if cc_pct >= 80:
                warn('连接数 %.0f%% 接近 maxclients' % cc_pct)
            else:
                ok('连接数水位正常 (%.1f%%)' % cc_pct)

        # ---------- 2. 内存 ----------
        section('内存')
        def _human_mb(value):
            """Redis 人类可读内存或纯字节数 → MB; 无法解析时返回 None."""
            if value is None: return None
            text = as_text(value)
            if text is None: return None
            text = text.strip().upper()
            try:
                if text.endswith('K'): return float(text[:-1]) / 1024
                if text.endswith('M'): return float(text[:-1])
                if text.endswith('G'): return float(text[:-1]) * 1024
                if text.endswith('T'): return float(text[:-1]) * 1024 * 1024
                if text.endswith('B'): return float(text[:-1]) / 1024 / 1024
                return float(text) / 1024 / 1024
            except (TypeError, ValueError, OverflowError):
                return None

        used_raw = rinfo.get('used_memory_human', rinfo.get('used_memory'))
        peak_raw = rinfo.get('used_memory_peak_human', rinfo.get('used_memory_peak'))
        maxm_raw = rinfo.get('maxmemory_human', rinfo.get('maxmemory'))
        umb = _human_mb(used_raw)
        maxm_mb = _human_mb(maxm_raw)
        policy = status_value('maxmemory_policy')
        info('used_memory=%s, peak=%s, maxmemory=%s, policy=%s' % (
            as_text(used_raw) or 'unknown', as_text(peak_raw) or 'unknown',
            as_text(maxm_raw) or 'unknown', policy or 'unknown'))
        if umb is None or umb < 0:
            unknown('used_memory 缺失或无效, 无法计算内存水位')
        if maxm_mb is None or maxm_mb < 0:
            unknown('maxmemory 缺失或无效, 无法计算内存水位')
        elif umb is not None and umb >= 0:
            if maxm_mb > 0:
                um_pct = umb / maxm_mb * 100
                if um_pct >= 90:
                    if policy == 'noeviction':
                        critical('内存已用 %.0f%% 接近 maxmemory (%.1fMB / %.1fMB), 即将拒绝写入!' % (um_pct, umb, maxm_mb))
                    elif policy and policy != 'noeviction':
                        critical('内存已用 %.0f%% 接近 maxmemory (%.1fMB / %.1fMB), 可能触发驱逐!' % (um_pct, umb, maxm_mb))
                    else:
                        critical('内存已用 %.0f%% 接近 maxmemory (%.1fMB / %.1fMB), 策略未知!' % (um_pct, umb, maxm_mb))
                elif um_pct >= 70:
                    warn('内存已用 %.0f%% (%.1fMB / %.1fMB), 关注内存和驱逐情况' % (um_pct, umb, maxm_mb))
                else:
                    ok('maxmemory 水位正常 (%.1f%%)' % um_pct)
            else:
                warn('maxmemory 未设置! Redis 会无限制用物理内存, 可能 OOM 被系统 kill')
                tip('先设置合理 maxmemory; 纯缓存可评估 LRU/LFU, 不可丢数据应配合 noeviction、扩容及持久化高可用')

        eviction_policies = ('allkeys-lru', 'allkeys-lfu', 'volatile-lru', 'volatile-lfu',
                             'allkeys-random', 'volatile-random', 'volatile-ttl')
        if policy is None:
            unknown('maxmemory_policy 缺失或无效, 无法判断到达上限后的行为')
        elif policy == 'noeviction':
            warn('maxmemory_policy=noeviction, 到达 maxmemory 后写请求会被拒绝!')
            tip('纯缓存可评估 allkeys-lru/lfu; 会话、队列等不可丢数据不应启用驱逐, 应扩容/降低内存占用并完善持久化与高可用')
        elif policy in eviction_policies:
            tip('当前驱逐策略仅适合可重建的纯缓存; 若数据不可丢失, 不应依赖驱逐, 应评估 noeviction、扩容/降内存及持久化高可用')
            if policy in ('volatile-lru', 'volatile-lfu', 'volatile-random', 'volatile-ttl'):
                tip('%s 只处理带 TTL 的 key, 大部分 key 无 TTL 时仍可能拒绝写入或 OOM' % policy)
        else:
            unknown('未知 maxmemory_policy=%s, 无法给出驱逐建议' % policy)

        evicted_text = counter_text('evicted_keys', 'evicted_keys')
        if evicted_text is None:
            unknown('evicted_keys 缺失或无效, 无法判断当前驱逐情况')
        else:
            info(evicted_text)
        evicted_delta = snapshot['delta'].get('evicted_keys')
        if evicted_delta is not None and evicted_delta > 0:
            warn('本间隔新增驱逐 %d 个 key (累计 %d), 请结合业务是否允许丢数据评估内存容量和策略' % (
                evicted_delta, counters['evicted_keys']))

        frag = as_float(rinfo.get('mem_fragmentation_ratio'))
        if frag is None or frag <= 0:
            unknown('mem_fragmentation_ratio 缺失、不支持或无效')
        else:
            info('mem_fragmentation_ratio=%.2f' % frag)
            if frag >= 1.5:
                warn('内存碎片率 %.2f 偏高, 关注 RSS 与已用内存差异, 谨慎评估 activedefrag/重启窗口' % frag)
            elif frag < 1.0:
                warn('内存碎片率 %.2f 小于 1, Redis 可能正在使用交换分区, 请检查系统内存' % frag)
            else:
                ok('内存碎片率正常 (%.2f)' % frag)

        # ---------- 3. 持久化 ----------
        section('持久化 (RDB / AOF)')
        loading = as_int(rinfo.get('loading'))
        if loading is None or loading not in (0, 1):
            unknown('loading 缺失或无效, 无法判断数据集加载状态')
        elif loading == 1:
            warn('Redis 正在加载数据集 (loading=1), 当前可用性和命令响应可能受影响')
        else:
            ok('当前未处于数据集加载状态')

        rdb_status = status_value('rdb_last_bgsave_status')
        if rdb_status == 'err':
            critical('RDB last bgsave 失败! 检查磁盘空间 / 权限')
        elif rdb_status == 'ok':
            ok('最近一次 RDB BGSAVE 成功')
        else:
            unknown('rdb_last_bgsave_status 缺失、不支持或无效')
        rdb_progress = as_int(rinfo.get('rdb_bgsave_in_progress'))
        if rdb_progress is None or rdb_progress not in (0, 1):
            unknown('rdb_bgsave_in_progress 缺失或无效')
        elif rdb_progress == 1:
            tip('RDB BGSAVE 正在进行, 关注 fork、内存及磁盘 IO 压力')
        else:
            ok('当前无 RDB BGSAVE 正在执行')

        aof_enabled = as_int(rinfo.get('aof_enabled'))
        if aof_enabled is None or aof_enabled not in (0, 1):
            unknown('aof_enabled 缺失或无效, 无法判断 AOF 状态')
        elif aof_enabled == 1:
            info('AOF 已开启')
            aof_write = status_value('aof_last_write_status')
            if aof_write == 'err':
                critical('AOF 最近一次写入失败! 检查磁盘空间、权限和 fsync 错误')
            elif aof_write == 'ok':
                ok('AOF 最近一次写入成功')
            else:
                unknown('aof_last_write_status 缺失、不支持或无效')
            aof_rewrite_status = status_value('aof_last_bgrewrite_status')
            if aof_rewrite_status == 'err':
                critical('AOF rewrite 失败! 磁盘空间可能不足')
            elif aof_rewrite_status == 'ok':
                ok('最近一次 AOF rewrite 成功')
            else:
                unknown('aof_last_bgrewrite_status 缺失、不支持或无效')
            aof_rewrite = as_int(rinfo.get('aof_rewrite_in_progress'))
            if aof_rewrite is None or aof_rewrite not in (0, 1):
                unknown('aof_rewrite_in_progress 缺失或无效')
            elif aof_rewrite == 1:
                tip('AOF 正在 rewrite, 内存/IO 压力会增大, 避免大 RENAME/FLUSHALL')
            else:
                ok('当前无 AOF rewrite 正在执行')
        else:
            warn('AOF 未开启, 只有 RDB 快照, 断电可能丢最近几分钟数据')
            warn('有持久化要求时评估 redis.conf: appendonly yes')
            skipped('AOF 未开启, AOF 写入/重写状态检查不适用')

        # ---------- 4. 主从复制 ----------
        section('主从复制')
        role = status_value('role')
        if role not in ('master', 'slave'):
            unknown('role 缺失、不支持或无效, 无法检查主从角色/链路/同步状态')
        else:
            info('role=%s' % role)
            if role == 'slave':
                link = status_value('master_link_status')
                if link == 'up':
                    ok('主从链路 master_link_status=up')
                elif link == 'down':
                    critical('主从链路 master_link_status=down, 请检查主库、网络及认证配置')
                else:
                    unknown('master_link_status 缺失、不支持或无效')
                sync = as_int(rinfo.get('master_sync_in_progress'))
                if sync is None or sync not in (0, 1):
                    unknown('master_sync_in_progress 缺失、不支持或无效')
                elif sync == 1:
                    warn('从库正在进行主从同步 (master_sync_in_progress=1), 暂不能视为同步完成')
                elif link == 'up':
                    ok('主从全量同步未在进行, 链路已建立')
                else:
                    skipped('主从链路未确认 up, 不将 master_sync_in_progress=0 判定为同步正常')
                lag = as_int(rinfo.get('master_last_io_seconds_ago'))
                if lag is None or lag < 0:
                    unknown('master_last_io_seconds_ago 缺失或无效, 无法评估主从 IO 活性')
                else:
                    info('master_last_io_seconds_ago=%ds' % lag)
                    if lag > 30:
                        warn('从库已超过 %ds 未与主库 IO, 请检查链路和复制积压' % lag)
            else:
                replicas = as_int(rinfo.get('connected_slaves'))
                if replicas is None or replicas < 0:
                    unknown('connected_slaves 缺失或无效, 无法检查从库链路状态')
                elif replicas == 0:
                    skipped('当前无已连接从库, 主从链路/同步状态检查不适用')
                else:
                    info('connected_slaves=%d' % replicas)
                    for idx in range(min(replicas, 10)):
                        slave_name = 'slave%d' % idx
                        slave_raw = rinfo.get(slave_name)
                        if slave_raw is None:
                            unknown('%s 状态缺失, 无法确认对应从库链路' % slave_name)
                            continue
                        if isinstance(slave_raw, dict):
                            slave_info = slave_raw
                        else:
                            slave_info = {}
                            for item in (as_text(slave_raw) or '').split(','):
                                if '=' in item:
                                    key, value = item.split('=', 1)
                                    slave_info[key.strip()] = value.strip()
                        slave_state = as_text(slave_info.get('state'))
                        if slave_state is None:
                            unknown('%s.state 缺失或无效' % slave_name)
                        elif slave_state.lower() == 'online':
                            ok('%s state=online' % slave_name)
                        else:
                            warn('%s state=%s, 从库尚未在线' % (slave_name, slave_state))
                    if replicas > 10:
                        info('从库较多, 详细链路状态仅展示前 10 个')

        # ---------- 5. Fork / BGSAVE 延迟 ----------
        section('Fork / BGSAVE')
        lfu = as_int(rinfo.get('latest_fork_usec'))
        if lfu is None or lfu < 0:
            unknown('latest_fork_usec 缺失、当前版本不支持或无效')
        elif lfu > 100000:
            warn('latest_fork_usec=%s > 100ms, fork 阻塞主线程时间长' % lfu)
            warn('Redis fork 是 copy-on-write, 写入量大时 fork 慢属正常; 错开高峰')
        else:
            ok('fork 延迟正常 (%sus)' % lfu)

        # ---------- 6. QPS / ops ----------
        section('QPS / 操作')
        total_cmds = counters.get('total_commands_processed')
        if total_cmds is None:
            unknown('total_commands_processed 缺失或无效, 无法计算 QPS')
        else:
            if upt_for_qps is not None:
                info('累计命令=%d, 估算生命周期平均 QPS=%.1f' % (total_cmds, total_cmds / upt_for_qps))
            else:
                info('累计命令=%d, 生命周期平均 QPS=unknown' % total_cmds)
            if 'total_commands_processed' in snapshot['delta']:
                info('本间隔命令增量=%+d, 实际间隔 QPS=%.2f' % (
                    snapshot['delta']['total_commands_processed'], snapshot['rate']['total_commands_processed']))
        inst_ops = as_int(rinfo.get('instantaneous_ops_per_sec'))
        if inst_ops is None or inst_ops < 0:
            unknown('instantaneous_ops_per_sec 缺失或无效')
        else:
            info('瞬时 ops_per_sec=%d' % inst_ops)

        # ---------- 7. keyspace / 命中率 ----------
        section('keyspace')
        hits = counters.get('keyspace_hits')
        misses = counters.get('keyspace_misses')
        hits_text = counter_text('keyspace_hits', 'keyspace_hits')
        misses_text = counter_text('keyspace_misses', 'keyspace_misses')
        if hits_text is None:
            unknown('keyspace_hits 缺失或无效')
        else:
            info(hits_text)
        if misses_text is None:
            unknown('keyspace_misses 缺失或无效')
        else:
            info(misses_text)
        if hits is not None and misses is not None:
            total_lookup = hits + misses
            if total_lookup > 0:
                cumulative_hit = hits / total_lookup * 100
                info('累计 keyspace 命中率=%.2f%% (%d/%d), 仅作历史参考' % (
                    cumulative_hit, hits, total_lookup))
            else:
                skipped('累计 keyspace 查找数为 0, 累计命中率不适用')
            delta_hits = snapshot['delta'].get('keyspace_hits')
            delta_misses = snapshot['delta'].get('keyspace_misses')
            if delta_hits is not None and delta_misses is not None:
                delta_lookup = delta_hits + delta_misses
                if delta_lookup > 0:
                    interval_hit = delta_hits / delta_lookup * 100
                    info('本间隔 keyspace 命中率=%.2f%% (%d/%d)' % (
                        interval_hit, delta_hits, delta_lookup))
                    if delta_lookup >= 100 and interval_hit < 50:
                        warn('本间隔 keyspace 命中率 %.2f%% 偏低, 检查缓存 key 设计、TTL 和业务访问模式' % interval_hit)
                else:
                    skipped('本间隔无 keyspace 查找, 增量命中率不适用')

        ks = {}
        for key, value in rinfo.items():
            key = as_text(key) or ''
            if not key.startswith('db'): continue
            if isinstance(value, dict):
                ks[key] = value
                continue
            item_map = {}
            for item in (as_text(value) or '').split(','):
                if '=' in item:
                    name, item_value = item.split('=', 1)
                    item_map[name.strip()] = item_value.strip()
            ks[key] = item_map
        if not ks:
            ok('当前实例所有 db 都是空的 (无 key)')
        for db, data in ks.items():
            keys = as_int(data.get('keys', 0))
            expires = as_int(data.get('expires', 0))
            avg_ttl = as_int(data.get('avg_ttl', 0))
            if keys is None or expires is None or avg_ttl is None:
                unknown('%s keyspace 数据无效, 无法完整解析' % db)
                continue
            info('%s keys=%d, expires=%d, avg_ttl=%ds' % (db, keys, expires, avg_ttl / 1000))
            if keys > 1000000:
                warn('%s key 数超 100 万, 确认内存是否够用, 大 key 可能导致 RDB fork 变慢' % db)

        # ---------- 8. slowlog ----------
        section('slowlog')
        try:
            slowlogs = c.slowlog_get(10)
        except Exception as ex:
            unknown('slowlog 查询异常: %s' % str(ex))
        else:
            if slowlogs:
                warn('最近 10 条慢日志 (取前 3):')
                for entry in slowlogs[:3]:
                    if not isinstance(entry, dict):
                        unknown('慢日志条目格式无法识别: %s' % slowlog_text(entry)[:80])
                        continue
                    cmd = slowlog_text(entry.get('command', []))[:80]
                    warn('  id=%s dur=%sµs cmd=%s' % (
                        slowlog_text(entry.get('id')), slowlog_text(entry.get('duration')), cmd))
            else:
                ok('暂无慢日志')

        def read_slowlog_config(name):
            try:
                config = c.config_get(name)
                if not isinstance(config, dict) or name not in config:
                    unknown('%s 查询结果缺失, 当前配置为 unknown' % name)
                    return None
                return config.get(name)
            except Exception as ex:
                unknown('%s 查询异常, 当前配置为 unknown: %s' % (name, str(ex)))
                return None

        sl_len = read_slowlog_config('slowlog-max-len')
        sl_thr = read_slowlog_config('slowlog-log-slower-than')
        if sl_len is not None:
            info('slowlog-max-len=%s' % slowlog_text(sl_len))
        if sl_thr is not None:
            info('slowlog-log-slower-than=%s µs' % slowlog_text(sl_thr))
            threshold = as_int(sl_thr)
            if threshold is None:
                unknown('slowlog-log-slower-than 返回值无效')
            elif threshold > 10000:
                tip('slowlog-log-slower-than=%s > 10ms, 建议调到 5000 µs 抓更多慢命令' % sl_thr)

        # ---------- 总结 ----------
        lines.append(''); lines.append('━━━ 总结 ━━━')
        nc = sum(1 for x in issues if x[0] == 2)
        nw = sum(1 for x in issues if x[0] == 1)
        nt = sum(1 for x in issues if x[0] == 0)
        nu = sum(1 for x in issues if x[0] == -1)
        if not issues:
            lines.append('  🎉 Redis 健康状况良好!')
        else:
            lines.append('  📊 严重 🚨 %d / 警告 ⚠️  %d / 建议 💡 %d / 未知 ❓ %d (共 %d)' % (
                nc, nw, nt, nu, len(issues)))
            if nu > 0:
                lines.append('  ❓ 存在未知/不支持/查询失败项, 不能据此宣称 Redis 健康状况良好')
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
    except Exception as ex:
        return mw.returnData(False, 'Redis 健康检查异常: %s' % str(ex))


# 测试
def test(args):
    sid = args['sid']
    t = nosqlRedis()
    print(t.get_options())
    print("test")
    return 'ok'

# ---------------------------------- run ----------------------------------

