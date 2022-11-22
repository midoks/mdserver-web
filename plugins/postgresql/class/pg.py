# coding: utf-8

import re
import os
import sys

import psycopg2


sys.path.append(os.getcwd() + "/class/core")
import mw


class ORM:
    __DB_PASS = None
    __DB_USER = 'postgres'
    __DB_PORT = 5432
    __DB_HOST = 'localhost'
    __DB_CONN = None
    __DB_CUR = None
    __DB_ERR = None
    __DB_CNF = '/etc/postgresql.cnf'
    __DB_SOCKET = '/tmp/.s.PGSQL.5432'
    __DB_CHARSET = "utf8"

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
                    self.__DB_CONN = psycopg2.connect(database='postgres',
                                                      user=self.__DB_USER,
                                                      password=self.__DB_PASS,
                                                      host=self.__DB_SOCKET,
                                                      port=int(self.__DB_PORT))
                except Exception as e:
                    self.__DB_HOST = '127.0.0.1'
                    self.__DB_CONN = psycopg2.connect(database='postgres',
                                                      user=self.__DB_USER,
                                                      password=self.__DB_PASS,
                                                      host=self.__DB_SOCKET,
                                                      port=int(self.__DB_PORT))
            else:
                try:
                    self.__DB_CONN = psycopg2.connect(database='postgres',
                                                      user=self.__DB_USER,
                                                      password=self.__DB_PASS,
                                                      host=self.__DB_HOST,
                                                      port=int(self.__DB_PORT))
                except Exception as e:
                    self.__DB_HOST = '127.0.0.1'
                    self.__DB_CONN = psycopg2.connect(database='postgres',
                                                      user=self.__DB_USER,
                                                      password=self.__DB_PASS,
                                                      host=self.__DB_HOST,
                                                      port=int(self.__DB_PORT))

            self.__DB_CONN.autocommit = True
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

    def setPort(self, port):
        self.__DB_PORT = port

    def setHostAddr(self, host):
        self.__DB_HOST = host

    def setPwd(self, pwd):
        self.__DB_PASS = pwd

    def getPwd(self):
        return self.__DB_PASS

    def table(self, table):
        # 设置表名
        self.__DB_TABLE = table
        return self

    def where(self, where, param=()):
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

    def select(self):
        # 查询数据集
        if not self.__Conn():
            return self.__DB_ERR
        try:
            sql = "SELECT " + self.__OPT_FIELD + " FROM " + self.__DB_TABLE + \
                self.__OPT_WHERE + self.__OPT_GROUP + self.__OPT_ORDER + self.__OPT_LIMIT
            # print(sql)
            result = self.__DB_CUR.execute(sql, self.__OPT_PARAM)
            data = self.__DB_CUR.fetchall()
            ret = []
            if self.__OPT_FIELD != "*":
                field = self.__OPT_FIELD.split(',')
                for row in data:
                    i = 0
                    field_k = {}
                    for key in field:
                        field_k[key] = row[i]
                        i += 1
                    ret.append(field_k)
            else:
                ret = map(list, data)
            self.__Close()
            return ret
        except Exception as ex:
            return "error: " + str(ex)

    def execute(self, sql):
        # 执行SQL语句返回受影响行
        if not self.__Conn():
            return self.__DB_ERR
        try:
            result = self.__DB_CUR.execute(sql)
            self.__DB_CONN.commit()
            self.__Close()
            return result
        except Exception as ex:
            return ex

    def query(self, sql):
        # 执行SQL语句返回数据集
        if not self.__Conn():
            return self.__DB_ERR
        try:
            self.__DB_CUR.execute(sql)
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
