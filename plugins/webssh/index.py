# coding: utf-8

import time
import random
import os
import json
import re
import sys

sys.path.append(os.getcwd() + "/class/core")
import mw


class App():

    __cmd_file = 'cmd.json'
    __cmd_path = ''

    def __init__(self):
        self.__cmd_path = self.getServerDir() + '/' + self.__cmd_file

        if not os.path.exists(self.__cmd_path):
            mw.writeFile(self.__cmd_path, '[]')

    def getPluginName(self):
        return 'webssh'

    def getPluginDir(self):
        return mw.getPluginDir() + '/' + self.getPluginName()

    def getServerDir(self):
        return mw.getServerDir() + '/' + self.getPluginName()

    def getArgs(self):
        args = sys.argv[2:]
        tmp = {}
        args_len = len(args)

        if args_len == 1:
            t = args[0].strip('{').strip('}')
            t = t.split(':')
            tmp[t[0]] = t[1]
        elif args_len > 1:
            for i in range(len(args)):
                t = args[i].split(':')
                tmp[t[0]] = t[1]

        return tmp

    def checkArgs(self, data, ck=[]):
        for i in range(len(ck)):
            if not ck[i] in data:
                return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
        return (True, mw.returnJson(True, 'ok'))

    def status(self):
        return 'start'

    def saveCmd(self, t):
        data_tmp = json.loads(mw.readFile(self.__cmd_path))
        is_has = False
        for x in range(0, len(data_tmp) - 1):
            if data_tmp[x]['title'] == t['title']:
                is_has = True
                data_tmp[x]['cmd'] = t['cmd']
        if not is_has:
            data_tmp.append(t)
        mw.writeFile(self.__cmd_path, json.dumps(data_tmp))

    def add_cmd(self):
        args = self.getArgs()
        check = self.checkArgs(args, ['title', 'cmd'])
        if not check[0]:
            return check[1]

        title = args['title'].strip()
        cmd = args['cmd']

        t = {
            'title': title,
            'cmd': cmd
        }
        self.saveCmd(t)

        return mw.returnJson(True, '添加成功!')

    def del_cmd(self):
        args = self.getArgs()
        check = self.checkArgs(args, ['title'])
        if not check[0]:
            return check[1]

        title = args['title'].strip()
        data_tmp = json.loads(mw.readFile(self.__cmd_path))
        for x in range(0, len(data_tmp)):
            if data_tmp[x]['title'] == title:
                del(data_tmp[x])
                mw.writeFile(self.__cmd_path, json.dumps(data_tmp))
                return mw.returnJson(True, '删除成功')
        return mw.returnJson(False, '删除无效')

    def get_cmd_list(self):
        alist = json.loads(mw.readFile(self.__cmd_path))
        return mw.returnJson(True, 'ok', alist)

    def add_server(self):
        args = self.getArgs()
        check = self.checkArgs(
            args, ['host', 'port', 'username', 'password', 'pkey', 'pkey_passwd', 'ps'])
        if not check[0]:
            return check[1]

if __name__ == "__main__":
    func = sys.argv[1]
    classApp = App()
    try:
        data = eval("classApp." + func + "()")
        print(data)
    except Exception as e:
        print(mw.getTracebackInfo())
