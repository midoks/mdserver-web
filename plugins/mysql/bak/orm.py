# coding: utf-8

import re
import os
import sys

import pymysql.cursors


class ORM:
    __DB_PASS = None
    __DB_USER = 'root'
    __DB_PORT = 3306
    __DB_NAME = ''
    __DB_HOST = 'localhost'
    __DB_CONN = None
    __DB_CUR = None
    __DB_ERR = None
    __DB_CNF = '/etc/my.cnf'
    __DB_SOCKET = '/www/server/mysql/mysql.sock'
    __DB_CHARSET = "utf8"

    # orm
    __DB_TABLE = ""             # 被操作的表名称
    __OPT_WHERE = ""            # where条件
    __OPT_LIMIT = ""            # limit条件
    __OPT_GROUP = ""            # group条件
    __OPT_ORDER = ""            # order条件
    __OPT_FIELD = "*"           # field条件
    __OPT_PARAM = ()            # where值

    def __Conn(self):
        '''连接数据库'''
        try:

            if os.path.exists(self.__DB_SOCKET):
                try:
                    self.__DB_CONN = pymysql.connect(host=self.__DB_HOST, user=self.__DB_USER, passwd=self.__DB_PASS,
                                                     database=self.__DB_NAME,
                                                     port=int(self.__DB_PORT), charset=self.__DB_CHARSET, connect_timeout=1,
                                                     unix_socket=self.__DB_SOCKET, cursorclass=pymysql.cursors.DictCursor)
                except Exception as e:
                    self.__DB_HOST = '127.0.0.1'
                    self.__DB_CONN = pymysql.connect(host=self.__DB_HOST, user=self.__DB_USER, passwd=self.__DB_PASS,
                                                     database=self.__DB_NAME,
                                                     port=int(self.__DB_PORT), charset=self.__DB_CHARSET, connect_timeout=1,
                                                     unix_socket=self.__DB_SOCKET, cursorclass=pymysql.cursors.DictCursor)
            else:
                try:
                    self.__DB_CONN = pymysql.connect(host=self.__DB_HOST, user=self.__DB_USER, passwd=self.__DB_PASS,
                                                     database=self.__DB_NAME,
                                                     port=int(self.__DB_PORT), charset=self.__DB_CHARSET, connect_timeout=1,
                                                     cursorclass=pymysql.cursors.DictCursor)
                except Exception as e:
                    self.__DB_HOST = '127.0.0.1'
                    self.__DB_CONN = pymysql.connect(host=self.__DB_HOST, user=self.__DB_USER, passwd=self.__DB_PASS,
                                                     database=self.__DB_NAME,
                                                     port=int(self.__DB_PORT), charset=self.__DB_CHARSET, connect_timeout=1,
                                                     cursorclass=pymysql.cursors.DictCursor)

            self.__DB_CUR = self.__DB_CONN.cursor()
            return True
        except Exception as e:
            self.__DB_ERR = e
            return False

    def setDbConf(self, conf):
        self.__DB_CNF = conf

    def setSocket(self, sock):
        self.__DB_SOCKET = sock

    def setCharset(self, charset):
        self.__DB_CHARSET = charset

    def setHost(self, host):
        self.__DB_HOST = host

    def setPort(self, port):
        self.__DB_PORT = port

    def setUser(self, user):
        self.__DB_USER = user

    def setPwd(self, pwd):
        self.__DB_PASS = pwd

    def getPwd(self):
        return self.__DB_PASS

    def setDbName(self, name):
        self.__DB_NAME = name

    def execute(self, sql, param=()):
        # 执行SQL语句返回受影响行
        if not self.__Conn():
            return self.__DB_ERR
        try:
            result = self.__DB_CUR.execute(sql,param)
            self.__DB_CONN.commit()
            self.__Close()
            return result
        except Exception as ex:
            return ex

    def query(self, sql, param=()):
        # 执行SQL语句返回数据集
        if not self.__Conn():
            return self.__DB_ERR
        try:
            self.__DB_CUR.execute(sql,param)
            result = self.__DB_CUR.fetchall()
            # print(result)
            # 将元组转换成列表
            # data = map(list, result)
            self.__Close()
            return result
        except Exception as ex:
            return ex

    def __Close(self):
        # 关闭连接
        self.__DB_CUR.close()
        self.__DB_CONN.close()


    def checkInput(self, data):
        if not data:
            return data
        if type(data) != str:
            return data
        checkList = [
            {'d': '<', 'r': '＜'},
            {'d': '>', 'r': '＞'},
            {'d': '\'', 'r': '‘'},
            {'d': '"', 'r': '“'},
            {'d': '&', 'r': '＆'},
            {'d': '#', 'r': '＃'},
            {'d': '<', 'r': '＜'}
        ]
        for v in checkList:
            data = data.replace(v['d'], v['r'])
        return data


    def table(self, table):
        # 设置表名
        self.__DB_TABLE = table
        return self

    def where(self, where, param):
        # WHERE条件
        if where:
            self.__OPT_WHERE = " WHERE " + where
            self.__OPT_PARAM = param
        return self

    def andWhere(self, where, param):
        # WHERE条件
        if where:
            self.__OPT_WHERE = self.__OPT_WHERE + " and " + where
            # print(param)
            # print(self.__OPT_PARAM)
            self.__OPT_PARAM = self.__OPT_PARAM + param
        return self

    def order(self, order):
        # ORDER条件
        if len(order):
            self.__OPT_ORDER = " ORDER BY " + order
        else:
            self.__OPT_ORDER = ""
        return self

    def group(self, group):
        if len(group):
            self.__OPT_GROUP = " GROUP BY " + group
        else:
            self.__OPT_GROUP = ""
        return self

    def limit(self, limit):
        # LIMIT条件
        if len(limit):
            self.__OPT_LIMIT = " LIMIT " + limit
        else:
            self.__OPT_LIMIT = ""
        return self

    def field(self, field):
        # FIELD条件
        if len(field):
            self.__OPT_FIELD = field
        return self

    def find(self):
        # 取一行数据
        result = self.limit("1").select()
        # print(result)
        if len(result) == 1:
            return result[0]
        return result

    def select(self):
        # 查询数据集
        
        sql = "SELECT " + self.__OPT_FIELD + " FROM " + self.__DB_TABLE + \
            self.__OPT_WHERE + self.__OPT_GROUP + self.__OPT_ORDER + self.__OPT_LIMIT
        # print(sql)
        # print(self.__OPT_PARAM)
        result = self.query(sql, self.__OPT_PARAM)
        return result

    def getField(self, keyName):
        # 取回指定字段
        result = self.field(keyName).select()
        # print(result[0][keyName])
        if len(result) == 1:
            return result[0][keyName]
        return result

    def setField(self, keyName, keyValue):
        # 更新指定字段
        return self.save(keyName, (keyValue,))

    # 构造数据
    def __format_pdata(self, pdata):
        keys = pdata.keys()
        keys_str = ','.join(keys)
        param = []
        for k in keys:
            param.append(pdata[k])
        return keys_str, tuple(param)

    def delete(self, id=None):
        # 删除数据
     
        if id:
            self.__OPT_WHERE = " WHERE id=%s"
            self.__OPT_PARAM = (id,)
        sql = "DELETE FROM " + self.__DB_TABLE + self.__OPT_WHERE
        # print(sql)
        result = self.execute(sql, self.__OPT_PARAM)
        return result


    def save(self, keys, param):
        # 更新数据

        opt = ""
        for key in keys.split(','):
            opt += key + "=%s,"
        opt = opt[0:len(opt) - 1]
        sql = "UPDATE " + self.__DB_TABLE + " SET " + opt + self.__OPT_WHERE

        # 处理拼接WHERE与UPDATE参数
        tmp = list(param)
        for arg in self.__OPT_PARAM:
            tmp.append(arg)
        self.__OPT_PARAM = tuple(tmp)

        # print(sql,self.__OPT_PARAM)
        result = self.execute(sql, self.__OPT_PARAM)
        return result

    # 更新数据
    def update(self, pdata):
        if not pdata:
            return False
        keys, param = self.__format_pdata(pdata)
        return self.save(keys, param)

    def add(self, keys, param):
        # 插入数据
        values = ""
        for key in keys.split(','):
            values += "%s,"
        values = self.checkInput(values[0:len(values) - 1])
        sql = "INSERT INTO " + self.__DB_TABLE + \
            "(" + keys + ") " + "VALUES(" + values + ")"

        # print(sql)
        result = self.execute(sql, param)
        return result







