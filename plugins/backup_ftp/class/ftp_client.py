# coding:utf-8

'''
doc: https://docs.python.org/zh-cn/3/library/ftplib.html
'''

import sys
import io
import os
import time
import re
import json

import paramiko
import ftplib

sys.path.append(os.getcwd() + "/class/core")
import mw

DEBUG = True

"""
=============自定义异常===================
"""


class OsError(Exception):
    """OS端异常"""


class ObjectNotFound(OsError):
    """对象不存在时抛出的异常"""

    def __init__(self, *args, **kwargs):
        message = "文件对象不存在。"
        super(ObjectNotFound, self).__init__(message, *args, **kwargs)


class APIError(Exception):
    """API参数错误异常"""

    def __init__(self, *args, **kwargs):
        _api_error_msg = 'API资料校验失败，请核实!'
        super(APIError, self).__init__(_api_error_msg, *args, **kwargs)


class FtpPSClient:
    _title = "FTP"
    _name = "ftp"
    __host = None
    __port = None
    __user = None
    __password = None
    default_port = 21
    default_backup_path = "/backup/"
    config_file = "cfg.json"

    def __init__(self, load_config=True, timeout=10):
        self.timeout = timeout
        if load_config:
            data = self.get_config()
            self.injection_config(data)

    def get_config(self):
        default_config = {
            "ftp_host": '',
            "ftp_user": '',
            "ftp_pass": '',
            "backup_path": self.default_backup_path
        }

        cfg = mw.getServerDir() + "/backup_ftp/" + self.config_file
        if os.path.exists(cfg):
            data = mw.readFile(cfg)
            return json.loads(data)
        else:
            return default_config

    def injection_config(self, data):
        host = data["ftp_host"].strip()
        if host.find(':') == -1:
            self.__port = self.default_port

        self.__host = data['ftp_host'].strip()
        self.__user = data['ftp_user'].strip()
        self.__password = data['ftp_pass'].strip()
        bp = data['backup_path'].strip()
        if bp:
            self.backup_path = self.getPath(bp)
        else:
            self.backup_path = self.getPath(self.default_backup_path)

    def authorize(self):
        try:
            if self.timeout is not None:
                ftp = ftplib.FTP(timeout=self.timeout)
            else:
                ftp = ftplib.FTP()

            debuglevel = 0
            # if DEBUG:
            # debuglevel = 3
            ftp.set_debuglevel(debuglevel)
            # ftp.set_pasv(True)
            ftp.connect(self.__host, int(self.__port))
            ftp.login(self.__user, self.__password)
            return ftp
        except Exception as e:
            raise OsError("无法连接FTP客户端，请检查配置参数是否正确。")

    # 取目录路径
    def getPath(self, path):
        if path[-1:] != '/':
            path += '/'
        if path[:1] != '/':
            path = '/' + path
        return path.replace('//', '/')

    def generateDownloadUrl(self, object_name):

        return 'ftp://' + \
               self.__user + ':' + \
               self.__password + '@' + \
               self.__host + ':' + \
               "/" + object_name

    def createDir(self, path, name):
        ftp = self.authorize()
        path = self.getPath(path)
        ftp.cwd(path)
        try:
            ftp.mkd(name)
            ftp.close()
            return True
        except Exception as e:
            ftp.close()
            return False

    def deleteDir(self, path, dir_name):
        try:
            ftp = self.authorize()
            ftp.rmd(dir_name)
            return True
        except ftplib.error_perm as e:
            print(str(e) + ":" + dir_name)
        except Exception as e:
            print(e)
        return False

    def deleteFile(self, filename):
        try:
            ftp = self.authorize()
            ftp.delete(filename)
            return True
        except Exception as e:
            return False

    def getList(self, path="/"):
        ftp = self.authorize()
        path = self.getPath(path)
        ftp.cwd(path)
        mlsd = False
        try:
            files = list(ftp.mlsd())
            files = files[1:]
            mlsd = True
        except:
            try:
                files = ftp.nlst(path)
                mlsd = False
            except:
                raise RuntimeError("ftp服务器数据返回异常。")

        ftp.close()
        f_list = []
        dirs = []
        data = []
        default_time = '1971/01/01 01:01:01'
        for dt in files:
            # print(dt)
            if mlsd:
                dt_name = dt[0]
                dt_info = dt[1]
            else:
                if dt.find("/") >= 0:
                    dt = dt.split("/")[-1]
            tmp = {}
            tmp['name'] = dt_name
            if dt_name == '.' or dt_name == '..':
                continue

            tmp['time'] = dt_info['modify']
            try:
                tmp['size'] = dt_info['size']
                tmp['type'] = "File"
                tmp['download'] = self.generateDownloadUrl(path + dt_name)
                f_list.append(tmp)
            except:
                tmp['size'] = dt_info['sizd']
                tmp['type'] = None
                tmp['download'] = ''
                dirs.append(tmp)
        data = dirs + f_list

        mlist = {}
        mlist['path'] = path
        mlist['list'] = data
        return mlist
