# coding:utf-8

# https://pypi.org/project/pymemcache/
# https://pymemcache.readthedocs.io/en/latest/getting_started.html#using-a-client-pool

import sys
import io
import os
import time
import re
import json
import pymemcache

sys.path.append(os.getcwd() + "/class/core")
import mw

def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner

@singleton
class nosqlMemcached():

    __DB_PASS = None
    __DB_USER = None
    __DB_PORT = 11211
    __DB_HOST = '127.0.0.1'
    __DB_CONN = None
    __DB_ERR = None

    __DB_LOCAL = None

    def __init__(self):
        self.__config = self.get_options(None)


    def conn(self):

        if self.__DB_HOST in ['127.0.0.1', 'localhost']:
            mem_path = "{}/memcached".format(mw.getServerDir())
            if not os.path.exists(mem_path): return False

        if not self.__DB_LOCAL:
            self.__DB_PORT = int(self.__config['port'])
        try:
            self.__DB_CONN = pymemcache.client.base.PooledClient((self.__DB_HOST,self.__DB_PORT), max_pool_size=4)
            return self.__DB_CONN
        except pymemcache.exceptions.MemcacheError:
            return False
        except Exception:
            self.__DB_ERR = mw.getTracebackInfo()
        return False

    # 获取配置项
    def get_options(self, get=None):

        result = {}
        mem_content = mw.readFile("{}/memcached/memcached.env".format(mw.getServerDir()))
        if not mem_content: return False

        keys = ["bind", "PORT"]
        rep = 'PORT\s*=\s*(.*)'
        port_re = re.search(rep, mem_content)
        if port_re:
            result['port'] = int(port_re.groups()[0].strip())
        else:
            result['port'] = 11211
        return result

    def set_host(self, host, port, prefix=''):
        self.__DB_HOST = host
        self.__DB_PORT = int(port)
        self.__DB_PREFIX = prefix
        self.__DB_LOCAL = 1
        return self
        

@singleton
class nosqlMemcachedCtr():

    def __init__(self):
        pass

    def getInstanceBySid(self, sid = 0):
        instance = nosqlMemcached()
        return instance

    def getItems(self, args):
        sid = args['sid']
        mem_instance = self.getInstanceBySid(sid).conn()
        if mem_instance is False:
            return mw.returnData(False,'无法链接')

        result = {}
        m_items = mem_instance.stats('items')

        item_no = []
        for i in m_items:
            item_match = b'items:(\d*?):number'
            item_match_re = re.search(item_match, i)
            if item_match_re:
                v = item_match_re.groups()[0].strip()
                v_str = v.decode()
                if not v_str in item_no:
                    item_no.append(v_str)

        if len(item_no) == 0:
            item_no = [0]

        result['items'] = item_no
        return mw.returnData(True,'ok', result)

    def getKeyList(self, args):
        sid = args['sid']
        mem_instance = self.getInstanceBySid(sid).conn()
        if mem_instance is False:
            return mw.returnData(False,'无法链接')


        p = 1
        size = 10
        if 'p' in args:
            p = args['p']

        if 'size' in args:
            size = args['size']

        item_id = args['item_id']
        if item_id == '0':
            return mw.returnData(False,'ok')

        m_items = mem_instance.stats('items')

        item_key = 'items:%s:number' % item_id
        item_key_b = item_key.encode("utf-8")
        m_items_v = m_items[item_key_b]

        
        start = (p-1)*size
        end = start+size
        if end > m_items_v:
            end = m_items_v


        all_key = mem_instance.stats('cachedump', str(item_id) , str(0))
        # print(all_key)
        all_key_list = []
        cur_time_t = time.time()
        for k in all_key:
            t = {}
            t['k'] = k.decode("utf-8")
            v = all_key[k].decode("utf-8")
            v = v.strip('[').strip(']').split(';')
            t['s'] = v[0]
            cur_time = v[1].strip().split(' ')[0]

            if int(cur_time) != 0 :
                t['t'] =  int(cur_time) - int(cur_time_t)
            else:
                t['t'] = 0
            all_key_list.append(t)

        # print(len(all_key_list))
        # print(start,end)
        return_all_key = all_key_list[start:end]

        for x in range(len(return_all_key)):
            v = mem_instance.get(return_all_key[x]['k'])
            return_all_key[x]['v'] = v.decode('utf-8')

        result = {}
        result['list'] = return_all_key 
        result['p'] = p

        page_args = {}
        page_args['count'] = len(all_key_list)
        page_args['tojs'] = 'memcachedGetKeyList'
        page_args['p'] = p
        page_args['row'] = size
        result['page'] = mw.getPage(page_args)

        return mw.returnData(True,'ok', result)

    def delVal(self, args):

        sid = args['sid']
        mem_instance = self.getInstanceBySid(sid).conn()
        if mem_instance is False:
            return mw.returnData(False,'无法链接')

        key = args['key']
        mem_instance.delete(key)
        return mw.returnData(True,'删除成功!')

    def setKv(self, args):

        sid = args['sid']
        mem_instance = self.getInstanceBySid(sid).conn()
        if mem_instance is False:
            return mw.returnData(False,'无法链接')

        key = args['key']
        val = args['val']
        endtime = args['endtime']
        mem_instance.set(key, val, int(endtime))
        return mw.returnData(True,'设置成功!')

    def clear(self, args):
        sid = args['sid']
        mem_instance = self.getInstanceBySid(sid).conn()
        if mem_instance is False:
            return mw.returnData(False,'无法链接')

        mem_instance.flush_all()
        return mw.returnData(True,'清空成功!')

# ---------------------------------- run ----------------------------------
# 获取 memcached 列表
def get_items(args):
    t = nosqlMemcachedCtr()
    return t.getItems(args)

def get_key_list(args):
    t = nosqlMemcachedCtr()
    return t.getKeyList(args)

def del_val(args):
    t = nosqlMemcachedCtr()
    return t.delVal(args)

def set_kv(args):
    t = nosqlMemcachedCtr()
    return t.setKv(args)

def clear(args):
    t = nosqlMemcachedCtr()
    return t.clear(args)

# 测试
def test(args):
    sid = args['sid']
    t = nosqlMemcachedCtr()
    print(t.get_options())
    print("test")
    return 'ok'

# ---------------------------------- run ----------------------------------

