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
BLOCK_SIZE = 1024 * 1024 * 2
# BLOCK_SIZE = 50
PROGRESS_FILE_NAME = "PROGRESS_FILE_NAME"

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

    def __init__(self, load_config=True, timeout=600):
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
        self.__host = host = data["ftp_host"].strip()
        if host.find(':') == -1:
            self.__port = self.default_port
        else:
            self.__host = host.split(':')[0]
            self.__port = host.split(':')[1]

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
            raise OsError("无法连接FTP客户端，请检查配置参数是否正确!")

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

    def buildDirName(self, data_type, file_name):
        import re
        prefix_dict = {
            "site": "web",
            "database": "db",
            "path": "path",
        }
        file_regx = prefix_dict.get(data_type) + "_(.+)_20\d+_\d+\."
        sub_search = re.search(file_regx, file_name)
        sub_path_name = ""
        if sub_search:
            sub_path_name = sub_search.groups()[0]
            sub_path_name += '/'

        # 构建OS存储路径
        object_name = self.backup_path + \
            data_type + '/' + \
            sub_path_name + \
            file_name
        return object_name

    def uploadFile(self, filename, data_type=None, *args, **kwargs):

        client = self.authorize()

        local_file_name = filename
        filename = os.path.abspath(filename)
        dirname = os.path.dirname(filename)
        temp_name = os.path.split(filename)[1]

        object_name = self.buildDirName(data_type, temp_name)

        upload_tmp_dir = os.path.join(dirname, ".upload_tmp")
        if not os.path.exists(upload_tmp_dir):
            os.mkdir(upload_tmp_dir)

        print("|-正在上传文件到 {}".format(object_name))

        total_bytes = os.path.getsize(filename)
        object_md5_name = mw.md5(object_name)
        pg_file = os.path.join(upload_tmp_dir, object_md5_name + ".pl")

        block_size = BLOCK_SIZE
        if kwargs.get("block_size"):
            try:
                block_size = float(kwargs.get("block_size"))
            except:
                pass

        remote_file_size = None
        if not os.path.exists(pg_file):
            # import uuid
            # uid = str(uuid.uuid1())
            progress_info = {
                "filename": local_file_name,
                "total_bytes": total_bytes,
                "uploaded_bytes": 0,
            }
            mw.writeFile(pg_file, json.dumps(progress_info))
        else:
            progress_info = json.loads(mw.readFile(pg_file))
            if total_bytes == progress_info.get("total_bytes"):
                # 取远程文件大小
                _max_loop = 10
                while _max_loop > 0:
                    try:
                        time.sleep(1)
                        remote_file_size = client.size(object_name)
                        if remote_file_size > total_bytes:
                            remote_file_size = None
                        break
                    except Exception as e:
                        if DEBUG:
                            print(type(e))
                            print(e)
                        _max_loop -= 1
            else:
                remote_file_size = None

        uploaded_bytes = 0 if remote_file_size is None else remote_file_size

        dir_name = os.path.split(object_name)[0]
        if dir_name:
            self.createDirP(dir_name)

        upload_start = time.time()

        try:
            if total_bytes > 1024 * 1024 * 1024:
                with open(local_file_name, 'rb') as file_handler:
                    if remote_file_size is not None:
                        file_handler.seek(remote_file_size)

                    client.voidcmd("TYPE I")
                    datasock = ''
                    esize = ''

                    datasock, esize = client.ntransfercmd(
                        "STOR " + object_name, remote_file_size)

                    while True:
                        buf = file_handler.read(block_size)
                        if not len(buf):
                            break
                        datasock.sendall(buf)
                        uploaded_bytes += len(buf)
                        if DEBUG:
                            print('\ruploading %.2f%%' %
                                  (float(uploaded_bytes) / total_bytes * 100))

                        print("uploaded_bytes", uploaded_bytes)
                        if uploaded_bytes == total_bytes:
                            break
                    datasock.close()

                    if DEBUG:
                        print('close data handle')
                    try:
                        client.voidcmd('NOOP')
                    except Exception as e:
                        if DEBUG:
                            print("Send NOOP command error:")
                            print(e)
                    else:
                        if DEBUG:
                            print('keep alive cmd success')
                    client.voidresp()
                    if DEBUG:
                        print('No loop cmd')
            else:
                # 小于1G文件直接上传
                file_handler = open(local_file_name, "rb")
                client.storbinary('STOR %s' % object_name,
                                  file_handler, blocksize=block_size)
                file_handler.close()
        except Exception as e:
            print(str(e))

        completed_file_size = None
        _max_loop = 10
        while _max_loop > 0:
            try:
                time.sleep(1)
                completed_file_size = client.size(object_name)
                break
            except Exception as e:
                _max_loop -= 1
                if DEBUG:
                    print("size error:" + str(e))

        # 上传完成
        if completed_file_size == total_bytes:
            if DEBUG:
                upload_completed = time.time()
                upload_diff = upload_completed - upload_start
                print("文件上传成功, 耗时: {}s。".format(upload_diff))
            if os.path.exists(pg_file):
                os.remove(pg_file)
            return True
        else:
            if os.path.exists(pg_file):
                os.remove(pg_file)
            print("文件上传后大小不一致！")

        print("completed_file_size:" + str(completed_file_size))
        print("total_bytes:", total_bytes)
        print("object_md5_name:", object_md5_name)
        print("pg_file:", pg_file)
        print("filename:", filename)
        print("dirname:", dirname)
        print("object_name:", object_name)
        return False

    def createDirP(self, dir_name):
        """创建远程目录

        :param dir_name: 目录名称
        :return:
        """
        try:
            dirnames = dir_name.split('/')
            ftp = self.authorize()
            # ftp.cwd(get.path);
            for dirname in dirnames:
                if not dirname or not dirname.strip():
                    continue
                try:
                    flist = ftp.nlst()
                    if not dirname in flist:
                        ftp.mkd(dirname)
                except:
                    # print("mlsd mode.")
                    try:
                        flist = list(ftp.mlsd())[1:]
                        for f in flist:
                            if dirname == f[0]:
                                break
                        else:
                            ftp.mkd(dirname)
                    except:
                        return False
                ftp.cwd(dirname)
            return True
        except:
            return False

    def createDir(self, path, name):
        ftp = self.authorize()
        path = self.getPath(path)
        ftp.cwd(path)
        try:
            ftp.mkd(name)
            ftp.close()
            return True
        except Exception as e:
            print(str(e))
            ftp.close()
            return False

    def deleteDir(self, path, dir_name):
        try:
            ftp = self.authorize()
            ftp.rmd(dir_name)
            return True
        except ftplib.error_perm as e:
            print("deleteDir:" + str(e) + ":" + dir_name)
        except Exception as e:
            print(e)
        return False

    def deleteFile(self, filename):
        try:
            ftp = self.authorize()
            ftp.delete(filename)
            return True
        except Exception as e:
            print(str(e))
            return False

    def getList(self, path="/"):
        ftp = self.authorize()
        path = self.getPath(path)
        ftp.cwd(path)
        mlsd = False
        try:
            files = list(ftp.mlsd())
            mlsd = True
        except:
            try:
                files = ftp.nlst(path)
                mlsd = False
            except:
                raise RuntimeError("FTP服务器数据返回异常!")
        ftp.close()
        # print(files)
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
