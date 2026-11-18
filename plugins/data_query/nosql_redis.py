# coding:utf-8

import sys
import io
import os
import time
import re
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
def get_health(args):
    sid = args.get('sid', 0)
    ctr = nosqlRedisCtr()
    c, err = ctr._connect(sid)
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
        rinfo = c.info()

        # ---------- 0. 基础信息 ----------
        section('基础信息')
        lines = lines  # keep ref; already set
        info('Redis %s' % rinfo.get('redis_version'))
        upt = int(rinfo.get('uptime_in_seconds', 0))
        info('已运行: %s' % ('%d天%02d:%02d' % (upt//86400, (upt%86400)//3600, (upt%3600)//60)))
        info('mode: %s, tcp_port: %s' % (rinfo.get('redis_mode', 'standalone'), rinfo.get('tcp_port')))

        # ---------- 1. 连接 ----------
        section('连接')
        cc = int(rinfo.get('connected_clients', 0))
        blocked = int(rinfo.get('blocked_clients', 0))
        rejected = int(rinfo.get('rejected_connections', 0))
        maxc = rinfo.get('maxclients')
        info('connected_clients=%d, blocked_clients=%d, maxclients=%s, rejected=%d' % (
            cc, blocked, maxc, rejected))
        if rejected > 0:
            critical('已拒绝 %d 次新连接! 客户端太多或 maxclients 太小' % rejected)
            critical('redis.conf: maxclients=10000')
        if blocked > 0:
            warn('有 %d 个客户端在阻塞 (BRPOP/BLPOP/BZPOPMIN, 属正常; 太多要排查)' % blocked)
        if maxc and cc / int(maxc) * 100 >= 80:
            warn('连接数 %.0f%% 接近 maxclients' % (cc / int(maxc) * 100))
        if rejected == 0 and cc / (int(maxc) if maxc else 1) * 100 < 80:
            ok('连接数水位正常')

        # ---------- 2. 内存 ----------
        section('内存')
        def _human_mb(s):
            """Redis used_memory_human → float MB, 兼容 955.95K / 1.03M / 3.5G / 纯数字"""
            if s is None: return 0
            s = str(s).strip()
            if s.endswith('K'): return float(s[:-1]) / 1024
            if s.endswith('M'): return float(s[:-1])
            if s.endswith('G'): return float(s[:-1]) * 1024
            if s.endswith('T'): return float(s[:-1]) * 1024 * 1024
            try: return float(s) / 1024 / 1024  # 纯字节数
            except Exception: return 0

        umb = _human_mb(rinfo.get('used_memory_human'))
        peak_mb = _human_mb(rinfo.get('used_memory_peak_human'))
        maxm = rinfo.get('maxmemory_human', '0B')
        maxm_mb = _human_mb(maxm)
        policy = rinfo.get('maxmemory_policy')
        info('used_memory=%s, peak=%s, maxmemory=%s, policy=%s' % (
            rinfo.get('used_memory_human'), rinfo.get('used_memory_peak_human'), maxm, policy))

        if maxm_mb > 0:
            um_pct = umb / maxm_mb * 100
            if um_pct >= 90:
                critical('内存已用 %.0f%% 接近 maxmemory (%.1fMB / %.1fMB), 即将驱逐!' % (um_pct, umb, maxm_mb))
                critical('当前策略: %s (volatile-lru 只驱逐带 TTL 的 key; noeviction 会拒写)' % policy)
            elif um_pct >= 70:
                warn('内存已用 %.0f%% (%.1fMB / %.1fMB), 关注驱逐情况' % (um_pct, umb, maxm_mb))
        else:
            warn('maxmemory 未设置! Redis 会无限制用物理内存, 可能 OOM 被系统 kill')
            warn('redis.conf: maxmemory 4gb, maxmemory-policy allkeys-lru')

        if policy == 'noeviction':
            warn('maxmemory_policy=noeviction, 到达 maxmemory 后写请求会被拒绝!')
            warn('生产建议: allkeys-lru 或 allkeys-lfu (Redis 4+)')
        elif policy == 'volatile-lru':
            tip('volatile-lru 只驱逐带过期的 key, 如果大部分 key 没 TTL, 还是会 OOM')

        # ---------- 3. 持久化 ----------
        section('持久化 (RDB / AOF)')
        info('loading=%s, rdb_last_bgsave_status=%s, aof_enabled=%s' % (
            rinfo.get('loading'), rinfo.get('rdb_last_bgsave_status'), rinfo.get('aof_enabled')))
        if rinfo.get('rdb_last_bgsave_status') == 'err':
            critical('RDB last bgsave 失败! 检查磁盘空间 / 权限')
        if rinfo.get('aof_enabled') == '1':
            aof_rewrite = rinfo.get('aof_rewrite_in_progress', '0')
            info('AOF enabled, rewrite_in_progress=%s, aof_last_bgrewrite_status=%s' % (
                aof_rewrite, rinfo.get('aof_last_bgrewrite_status')))
            if rinfo.get('aof_last_bgrewrite_status') == 'err':
                critical('AOF rewrite 失败! 磁盘空间可能不足')
            if int(aof_rewrite or 0) > 0:
                tip('AOF 正在 rewrite, 内存/IO 压力会增大, 避免大 RENAME/FLUSHALL')
        else:
            warn('AOF 未开启, 只有 RDB 快照, 断电可能丢最近几分钟数据')
            warn('redis.conf: appendonly yes')

        # ---------- 4. Fork / BGSAVE 延迟 ----------
        section('Fork / BGSAVE')
        lfu = rinfo.get('latest_fork_usec')
        if lfu is None:
            info('当前版本未上报 latest_fork_usec, 略过')
        elif int(lfu) > 100000:
            warn('latest_fork_usec=%s > 100ms, fork 阻塞主线程时间长' % lfu)
            warn('Redis fork 是 copy-on-write, 写入量大时 fork 慢属正常; 错开高峰')
        else:
            ok('fork 延迟正常 (%sus)' % lfu)

        # ---------- 5. QPS / ops ----------
        section('QPS / 操作')
        total_cmds = int(rinfo.get('total_commands_processed', 0))
        upt = max(upt, 1)
        qps = total_cmds / upt
        info('累计命令=%d, 估算平均 QPS=%.1f' % (total_cmds, qps))
        inst_ops = rinfo.get('instantaneous_ops_per_sec')
        if inst_ops: info('瞬时 ops_per_sec=%s' % inst_ops)

        # ---------- 6. keyspace ----------
        section('keyspace')
        ks = {}
        for k, v in rinfo.items():
            if k.startswith('db'):
                # redis-py 对 decode_responses=True 会把 keyspace 解析成 dict
                # 原始形式是 'keys=1,expires=0,avg_ttl=0' 字符串, 两种都兼容
                if isinstance(v, dict):
                    ks[k] = v
                    continue
                m = {}
                for kv in str(v).split(','):
                    if '=' in kv:
                        a, b = kv.split('=', 1)
                        m[a.strip()] = b.strip()
                ks[k] = m
        if not ks:
            ok('当前实例所有 db 都是空的 (无 key)')
        for db, d in ks.items():
            keys = int(d.get('keys', 0))
            expires = int(d.get('expires', 0))
            avg_ttl = int(d.get('avg_ttl', 0)) / 1000
            info('%s keys=%d, expires=%d, avg_ttl=%ds' % (db, keys, expires, avg_ttl))
            if keys > 1000000:
                warn('%s key 数超 100 万, 确认内存是否够用, 大 key 可能导致 RDB fork 变慢' % db)

        # ---------- 7. slowlog ----------
        section('slowlog')
        try:
            sl = c.slowlog_get(-1)
            if sl:
                warn('最近 10 条慢日志 (取前 3):')
                for x in sl[:3]:
                    cmd = ' '.join(x.get('command', []))[:80]
                    warn('  id=%s dur=%sµs cmd=%s' % (
                        x.get('id'), x.get('duration'), cmd))
            else:
                ok('暂无慢日志')
            sl_len = c.config_get('slowlog-max-len').get('slowlog-max-len', '?')
            sl_thr = c.config_get('slowlog-log-slower-than').get('slowlog-log-slower-than', '?')
            info('slowlog-max-len=%s, slowlog-log-slower-than=%s µs' % (sl_len, sl_thr))
            try:
                if int(sl_thr) > 10000:
                    tip('slowlog-log-slower-than=%s > 10ms, 建议调到 5000 µs 抓更多慢命令' % sl_thr)
            except Exception: pass
        except Exception as e:
            info('slowlog 查询异常: %s' % str(e))

        # ---------- 总结 ----------
        lines.append(''); lines.append('━━━ 总结 ━━━')
        nc = sum(1 for x in issues if x[0] == 2)
        nw = sum(1 for x in issues if x[0] == 1)
        nt = sum(1 for x in issues if x[0] == 0)
        if not issues:
            lines.append('  🎉 Redis 健康状况良好!')
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

