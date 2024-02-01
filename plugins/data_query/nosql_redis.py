# coding:utf-8

import sys
import io
import os
import time
import re
import redis

sys.path.append(os.getcwd() + "/class/core")
import mw

# def getPluginName():
#     return 'data_query'

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

    __DB_LOCAL = None

    def __init__(self):
        self.__config = self.get_options(None)


    def redis_conn(self, db_idx=0):

        if self.__DB_HOST in ['127.0.0.1', 'localhost']:
            redis_path = "{}/redis".format(mw.getServerDir())
            if not os.path.exists(redis_path): return False

        if not self.__DB_LOCAL:
            self.__DB_PASS = self.__config['requirepass']
            self.__DB_PORT = int(self.__config['port'])

        # print(self.__DB_HOST,self.__DB_PORT, self.__DB_PASS)
        try:
            redis_pool = redis.ConnectionPool(host=self.__DB_HOST, port=self.__DB_PORT, password=self.__DB_PASS, db=db_idx, socket_timeout=3)
            self.__DB_CONN = redis.Redis(connection_pool=redis_pool)
            self.__DB_CONN.ping()
            return self.__DB_CONN
        except redis.exceptions.ConnectionError:
            return False
        except Exception:
            self.__DB_ERR = mw.getTracebackInfo()
        return False

    # 获取配置项
    def get_options(self, get=None):

        result = {}
        redis_conf = mw.readFile("{}/redis/redis.conf".format(mw.getServerDir()))
        if not redis_conf: return False

        keys = ["bind", "port", "timeout", "maxclients", "databases", "requirepass", "maxmemory"]
        for k in keys:
            v = ""
            rep = "\n%s\s+(.+)" % k
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

    def getList(self, args):

        sid = args['sid']
        redis_instance = self.getInstanceBySid(sid).redis_conn(0)
        if redis_instance is False:
            return mw.returnData(False,'无法链接')


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

        redis_instance = self.getInstanceBySid(sid).redis_conn(idx)

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

        redis_instance = self.getInstanceBySid(sid).redis_conn(idx)

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
        redis_instance = self.getInstanceBySid(sid).redis_conn(idx)

        redis_info = redis_instance.info()
        if redis_info['role'] == 'slave':
            return mw.returnData(False,'从库不能删除操作!')

        redis_instance.delete(name)
        return mw.returnData(True,'操作成功')

    def batchDelVal(self, args):
        sid = args['sid']
        idx = args['idx']
        keys = args["keys"]
        redis_instance = self.getInstanceBySid(sid).redis_conn(idx)

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
            redis_instance = self.getInstanceBySid(sid).redis_conn(idx)

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

# 测试
def test(args):
    sid = args['sid']
    t = nosqlRedis()
    print(t.get_options())
    print("test")
    return 'ok'

# ---------------------------------- run ----------------------------------

