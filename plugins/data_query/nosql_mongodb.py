# coding:utf-8

import sys
import io
import os
import time
import re
import pymongo
import json

from bson.objectid import ObjectId
from bson.json_util import dumps

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
class nosqlMongodb():

    __DB_PASS = None
    __DB_USER = None
    __DB_PORT = 6379
    __DB_HOST = '127.0.0.1'
    __DB_CONN = None
    __DB_ERR = None

    __DB_LOCAL = None

    def __init__(self):
        self.__config = self.get_options(None)


    def mgdb_conn(self):

        if self.__DB_HOST in ['127.0.0.1', 'localhost']:
            mgdb_path = "{}/mongodb".format(mw.getServerDir())
            if not os.path.exists(mgdb_path): return False

        if not self.__DB_LOCAL:
            self.__DB_PORT = int(self.__config['port'])

        # print(self.__DB_HOST,self.__DB_PORT, self.__DB_PASS)
        try:
            self.__DB_CONN = pymongo.MongoClient(host=self.__DB_HOST, port=self.__DB_PORT, maxPoolSize=10)
            self.__DB_CONN.admin.command('ping')
            return self.__DB_CONN
        except pymongo.errors.ConnectionFailure:
            return False
        except Exception:
            self.__DB_ERR = mw.get_error_info()
        return False

    # 获取配置项
    def get_options(self, get=None):
        result = {}
        mgdb_content = mw.readFile("{}/mongodb/mongodb.conf".format(mw.getServerDir()))
        if not mgdb_content: return False

        keys = ["bind_ip", "port"]

        result['host'] = '127.0.0.1'
        rep = 'port\s*=\s*(.*)'
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

    def getDbList(self, args):
        sid = args['sid']
        mgdb_instance = self.getInstanceBySid(sid).mgdb_conn()
        if mgdb_instance is False:
            return mw.returnData(False,'无法链接')

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

        mgdb_instance = self.getInstanceBySid(sid).mgdb_conn()
        if mgdb_instance is False:
            return mw.returnData(False,'无法链接')

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

        mgdb_instance = self.getInstanceBySid(sid).mgdb_conn()
        if mgdb_instance is False:
            return mw.returnData(False,'无法链接')

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
        result = collection_instance.find(where).skip(start_index).limit(size).sort({'_id':-1})
        count = collection_instance.count_documents(where)
        d = []
        for document in result:
            d.append(document)

        doc_str_json = dumps(d)
        result = json.loads(doc_str_json)


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

        mgdb_instance = self.getInstanceBySid(sid).mgdb_conn()
        if mgdb_instance is False:
            return mw.returnData(False,'无法链接')

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

# 测试
def test(args):
    sid = args['sid']
    t = nosqlMongodbCtr()
    print(t.get_options())
    print("test")
    return 'ok'