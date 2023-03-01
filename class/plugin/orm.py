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
