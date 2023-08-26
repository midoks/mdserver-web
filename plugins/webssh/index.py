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
    __host_dir = ''

    def __init__(self):
        self.__cmd_path = self.getServerDir() + '/' + self.__cmd_file

        if not os.path.exists(self.__cmd_path):
            mw.writeFile(self.__cmd_path, '[]')

        self.__host_dir = self.getServerDir() + '/host'
        if not os.path.exists(self.__host_dir):
            mw.execShell('mkdir -p ' + self.__host_dir)

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
            if t.strip() == '':
                tmp = []
            else:
                t = t.split(':')
                tmp[t[0]] = t[1]
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

    def getSshInfo(self, file):
        rdata = mw.readFile(file)
        destr = mw.deDoubleCrypt('mdserver-web', rdata)
        return json.loads(destr)

    def get_server_by_host(self):
        args = self.getArgs()
        check = self.checkArgs(args, ['host'])
        if not check[0]:
            return check[1]

        info_file = self.__host_dir + '/' + args['host'] + '/info.json'
        if os.path.exists(info_file):
            try:
                info_tmp = self.getSshInfo(info_file)
                host_info = {}
                host_info['host'] = args['host']
                host_info['port'] = info_tmp['port']
                host_info['ps'] = info_tmp['ps']
                host_info['type'] = info_tmp['type']
                if 'password' in info_tmp:
                    host_info['password'] = info_tmp['password']
                if 'pkey' in info_tmp:
                    host_info['pkey'] = info_tmp['pkey']
                if 'pkey_passwd' in info_tmp:
                    host_info['pkey_passwd'] = info_tmp['pkey_passwd']
            except Exception as e:
                return mw.returnJson(False, '错误:' + str(e))

            return mw.returnJson(True, 'ok!', host_info)
        return mw.returnJson(False, '不存在此配置')

    def get_server_list(self):
        host_list = []
        if os.path.exists(self.__host_dir):
            for name in os.listdir(self.__host_dir):
                info_file = self.__host_dir + '/' + name + '/info.json'
                if not os.path.exists(info_file):
                    continue

                host_info = {}
                try:
                    info_tmp = self.getSshInfo(info_file)

                    host_info['host'] = name
                    host_info['port'] = info_tmp['port']
                    host_info['ps'] = info_tmp['ps']
                    # host_info['sort'] = int(info_tmp['sort'])
                except Exception as e:
                    # print(e)
                    return mw.returnJson(False, str(e))

                    # if os.path.exists(info_file):
                    #     os.remove(info_file)
                    # continue

                host_list.append(host_info)

        host_list = sorted(host_list, key=lambda x: x['host'], reverse=False)
        return mw.returnJson(True, 'ok!', host_list)

    def del_server(self):
        args = self.getArgs()
        check = self.checkArgs(args, ['host'])
        if not check[0]:
            return check[1]
        host = args['host']
        info_file = self.__host_dir + '/' + host
        mw.execShell('rm -rf {}'.format(info_file))
        return mw.returnJson(True, '删除成功!')

    def add_server(self):
        args = self.getArgs()
        check = self.checkArgs(
            args, ['host', 'port', 'type', 'username', 'ps'])
        if not check[0]:
            return check[1]

        host = args['host']
        info = {
            'port': args['port'],
            'username': args['username'],
            'ps': args['ps'],
            'type': args['type'],
        }

        if args['type'] == '0':
            info['password'] = args['password']
        else:
            info['pkey'] = args['pkey']
            info['pkey_passwd'] = args['pkey_passwd']

        dst_host_dir = self.__host_dir + '/' + host
        if not os.path.exists(dst_host_dir):
            os.makedirs(dst_host_dir)

        enstr = mw.enDoubleCrypt('mdserver-web', json.dumps(info))
        mw.writeFile(dst_host_dir + '/info.json', enstr)
        return mw.returnJson(True, '添加成功!')

if __name__ == "__main__":
    func = sys.argv[1]
    classApp = App()
    try:
        data = eval("classApp." + func + "()")
        print(data)
    except Exception as e:
        print(mw.getTracebackInfo())
