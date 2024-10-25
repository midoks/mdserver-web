# coding: utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------
# sqlite3操作
# ---------------------------------------------------------------------------------


import sqlite3
import os
import sys


class Sql():
    #------------------------------
    # 数据库操作类 For sqlite3
    #------------------------------
    __DB_FILE = None            # 数据库文件
    __DB_CONN = None            # 数据库连接对象
    __DB_TABLE = ""             # 被操作的表名称
    __OPT_WHERE = ""            # where条件
    __OPT_LIMIT = ""            # limit条件
    __OPT_GROUP = ""            # group条件
    __OPT_ORDER = ""            # order条件
    __OPT_FIELD = "*"           # field条件
    __OPT_PARAM = ()            # where值

    def __init__(self):
        self.__DB_FILE = 'data/default.db'

    def __getConn(self):
        # 取数据库对象
        try:
            if self.__DB_CONN == None:
                self.__DB_CONN = sqlite3.connect(self.__DB_FILE)
                self.__DB_CONN.text_factory = str
        except Exception as ex:
            # print(mw.getTracebackInfo())
            return "error: " + str(ex)

    def changeTextFactoryToBytes(self):
        self.__DB_CONN.text_factory = bytes
        return True

    def autoTextFactory(self):
        if sys.version_info[0] == 3:
            self.__DB_CONN.text_factory = lambda x: str(
                x, encoding="utf-8", errors='ignore')
        else:
            self.__DB_CONN.text_factory = lambda x: unicode(
                x, "utf-8", "ignore")

    def dbfile(self, name):
        self.__DB_FILE = 'data/' + name + '.db'
        return self

    def dbPos(self, path, name, suffix_name = 'db'):
        self.__DB_FILE = path + '/' + name + '.' + suffix_name
        return self

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
        self.__getConn()
        try:
            sql = "SELECT " + self.__OPT_FIELD + " FROM " + self.__DB_TABLE + \
                self.__OPT_WHERE + self.__OPT_GROUP + self.__OPT_ORDER + self.__OPT_LIMIT
            # print(sql)
            # print(self.__OPT_PARAM)
            result = self.__DB_CONN.execute(sql, self.__OPT_PARAM)
            data = result.fetchall()
            # 构造字曲系列
            if self.__OPT_FIELD != "*":
                field = self.__OPT_FIELD.split(',')
                tmp = []
                for row in data:
                    i = 0
                    tmp1 = {}
                    for key in field:
                        tmp1[key] = row[i]
                        i += 1
                    tmp.append(tmp1)
                    del(tmp1)
                data = tmp
                del(tmp)
            else:
                # 将元组转换成列表
                tmp = map(list, data)
                data = tmp
                del(tmp)
            self.__close()
            return data
        except Exception as ex:
            return "error: " + str(ex)

    def inquiry(self, input_field=''):
        # 查询数据集
        # 不清空查询参数
        self.__getConn()
        try:
            sql = "SELECT " + self.__OPT_FIELD + " FROM " + self.__DB_TABLE + \
                self.__OPT_WHERE + self.__OPT_GROUP + self.__OPT_ORDER + self.__OPT_LIMIT

            if os.path.exists('data/debug.pl'):
                print(sql, self.__OPT_PARAM)
            result = self.__DB_CONN.execute(sql, self.__OPT_PARAM)
            data = result.fetchall()
            # 构造字曲系列
            if self.__OPT_FIELD != "*":

                if input_field != "":
                    field = input_field.split(',')
                else:
                    field = self.__OPT_FIELD.split(',')

                tmp = []
                for row in data:
                    i = 0
                    tmp1 = {}
                    for key in field:
                        tmp1[key] = row[i]
                        i += 1
                    tmp.append(tmp1)
                    del(tmp1)
                data = tmp
                del(tmp)
            else:
                # 将元组转换成列表
                tmp = map(list, data)
                data = tmp
                del(tmp)
            return data
        except Exception as ex:
            return "error: " + str(ex)

    def getField(self, keyName):
        # 取回指定字段
        result = self.field(keyName).select()
        # print(result)
        if len(result) == 1:
            return result[0][keyName]
        return result

    def setField(self, keyName, keyValue):
        # 更新指定字段
        return self.save(keyName, (keyValue,))

    def find(self):
        # 取一行数据
        result = self.limit("1").select()
        if len(result) == 1:
            return result[0]
        return result

    def count(self):
        # 取行数
        key = "COUNT(*)"
        data = self.field(key).select()
        try:
            return int(data[0][key])
        except:
            return 0

    def add(self, keys, param):
        # 插入数据
        self.__getConn()
        try:
            values = ""
            for key in keys.split(','):
                values += "?,"
            values = self.checkInput(values[0:len(values) - 1])
            sql = "INSERT INTO " + self.__DB_TABLE + \
                "(" + keys + ") " + "VALUES(" + values + ")"
            result = self.__DB_CONN.execute(sql, param)
            last_id = result.lastrowid
            self.__close()
            self.__DB_CONN.commit()
            return last_id
        except Exception as ex:
            return "error: " + str(ex)

    # 插入数据
    def insert(self, pdata):
        if not pdata:
            return False
        keys, param = self.__format_pdata(pdata)
        return self.add(keys, param)

    # 更新数据
    def update(self, pdata):
        if not pdata:
            return False
        keys, param = self.__format_pdata(pdata)
        return self.save(keys, param)

    # 构造数据
    def __format_pdata(self, pdata):
        keys = pdata.keys()
        keys_str = ','.join(keys)
        param = []
        for k in keys:
            param.append(pdata[k])
        return keys_str, tuple(param)

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

    def addAll(self, keys, param):
        # 插入数据
        self.__getConn()
        try:
            values = ""
            for key in keys.split(','):
                values += "?,"
            values = values[0:len(values) - 1]
            sql = "INSERT INTO " + self.__DB_TABLE + \
                "(" + keys + ") " + "VALUES(" + values + ")"
            result = self.__DB_CONN.execute(sql, param)
            return True
        except Exception as ex:
            return "error: " + str(ex)

    def commit(self):
        self.__close()
        self.__DB_CONN.commit()

    def save(self, keys, param):
        # 更新数据
        self.__getConn()
        try:
            opt = ""
            for key in keys.split(','):
                opt += key + "=?,"
            opt = opt[0:len(opt) - 1]
            sql = "UPDATE " + self.__DB_TABLE + " SET " + opt + self.__OPT_WHERE

            # import mw
            # mw.writeFile('/tmp/test.pl', sql)

            # 处理拼接WHERE与UPDATE参数
            tmp = list(param)
            for arg in self.__OPT_PARAM:
                tmp.append(arg)
            self.__OPT_PARAM = tuple(tmp)
            result = self.__DB_CONN.execute(sql, self.__OPT_PARAM)
            self.__close()
            self.__DB_CONN.commit()
            return result.rowcount
        except Exception as ex:
            return "error: " + str(ex)

    def delete(self, id=None):
        # 删除数据
        self.__getConn()
        try:
            if id:
                self.__OPT_WHERE = " WHERE id=?"
                self.__OPT_PARAM = (id,)
            sql = "DELETE FROM " + self.__DB_TABLE + self.__OPT_WHERE
            result = self.__DB_CONN.execute(sql, self.__OPT_PARAM)
            self.__close()
            self.__DB_CONN.commit()
            return result.rowcount
        except Exception as ex:
            return "error: " + str(ex)

    def originExecute(self, sql, param=()):
        self.__getConn()
        try:
            result = self.__DB_CONN.execute(sql, param)
            self.__DB_CONN.commit()
            return result
        except Exception as ex:
            return "error: " + str(ex)

    def execute(self, sql, param=()):
        # 执行SQL语句返回受影响行
        self.__getConn()
        # print sql, param
        try:
            result = self.__DB_CONN.execute(sql, param)
            self.__DB_CONN.commit()
            return result.rowcount
        except Exception as ex:
            return "error: " + str(ex)

    def query(self, sql, param=()):
        # 执行SQL语句返回数据集
        self.__getConn()
        try:
            result = self.__DB_CONN.execute(sql, param)
            # 将元组转换成列表
            # data = map(list, result)
            return result
        except Exception as ex:
            return "error: " + str(ex)

    def create(self, name):
        # 创建数据表
        self.__getConn()
        import mw
        script = mw.readFile('data/' + name + '.sql')
        result = self.__DB_CONN.executescript(script)
        self.__DB_CONN.commit()
        return result.rowcount

    def fofile(self, filename):
        # 执行脚本
        self.__getConn()
        import mw
        script = mw.readFile(filename)
        result = self.__DB_CONN.executescript(script)
        self.__DB_CONN.commit()
        return result.rowcount

    def __close(self):
        # 清理条件属性
        self.__OPT_WHERE = ""
        self.__OPT_FIELD = "*"
        self.__OPT_ORDER = ""
        self.__OPT_LIMIT = ""
        self.__OPT_PARAM = ()

    def close(self):
        # 释放资源
        try:
            self.__DB_CONN.close()
            self.__DB_CONN = None
        except:
            pass
