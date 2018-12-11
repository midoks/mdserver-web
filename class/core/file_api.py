# coding: utf-8

import psutil
import time
import os
import sys
import public
import re
import json
import pwd


class file_api:

    def __init__(self):
        pass

    def getBody(self, path):
        if not os.path.exists(path):
            return public.returnJson(False, '文件不存在', (path,))

        if os.path.getsize(path) > 2097152:
            return public.returnJson(False, u'不能在线编辑大于2MB的文件!')

        fp = open(path, 'rb')
        data = {}
        data['status'] = True
        try:
            if fp:
                from chardet.universaldetector import UniversalDetector
                detector = UniversalDetector()
                srcBody = b""
                for line in fp.readlines():
                    detector.feed(line)
                    srcBody += line
                detector.close()
                char = detector.result
                data['encoding'] = char['encoding']
                if char['encoding'] == 'GB2312' or not char['encoding'] or char[
                        'encoding'] == 'TIS-620' or char['encoding'] == 'ISO-8859-9':
                    data['encoding'] = 'GBK'
                if char['encoding'] == 'ascii' or char[
                        'encoding'] == 'ISO-8859-1':
                    data['encoding'] = 'utf-8'
                if char['encoding'] == 'Big5':
                    data['encoding'] = 'BIG5'
                if not char['encoding'] in ['GBK', 'utf-8',
                                            'BIG5']:
                    data['encoding'] = 'utf-8'
                try:
                    if sys.version_info[0] == 2:
                        data['data'] = srcBody.decode(
                            data['encoding']).encode('utf-8', errors='ignore')
                    else:
                        data['data'] = srcBody.decode(data['encoding'])
                except:
                    data['encoding'] = char['encoding']
                    if sys.version_info[0] == 2:
                        data['data'] = srcBody.decode(
                            data['encoding']).encode('utf-8', errors='ignore')
                    else:
                        data['data'] = srcBody.decode(data['encoding'])
            else:
                if sys.version_info[0] == 2:
                    data['data'] = srcBody.decode('utf-8').encode('utf-8')
                else:
                    data['data'] = srcBody.decode('utf-8')
                data['encoding'] = u'utf-8'

            return public.returnJson(True, 'OK', data)
        except Exception as ex:
            return public.returnJson(False, u'文件编码不被兼容，无法正确读取文件!' + str(ex))

    def saveBody(self, path, data, encoding='utf-8'):
        if not os.path.exists(path):
            return public.returnJson(False, '文件不存在')
        try:
            if encoding == 'ascii':
                encoding = 'utf-8'
            if sys.version_info[0] == 2:
                data = data.encode(encoding, errors='ignore')
                fp = open(path, 'w+')
            else:
                data = data.encode(
                    encoding, errors='ignore').decode(encoding)
                fp = open(path, 'w+', encoding=encoding)
            fp.write(data)
            fp.close()

            public.writeLog('TYPE_FILE', '文件保存成功', (path,))
            return public.returnJson(True, '文件保存成功')
        except Exception as ex:
            return public.returnJson(False, 'FILE_SAVE_ERR:' + str(ex))

    def setFileAccept(self, filename):
        auth = 'www:www'
        if public.getOs() == 'darwin':
            user = public.execShell(
                "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
            auth = user + ':staff'
        os.system('chown -R ' + auth + ' ' + filename)
        os.system('chmod -R 755 ' + filename)

    def zip(self, sfile, dfile, stype, path):
        if sfile.find(',') == -1:
            if not os.path.exists(path + '/' + sfile):
                return public.returnMsg(False, '指定文件不存在!')

        try:
            tmps = public.getRunDir() + '/tmp/panelExec.log'
            if stype == 'zip':
                os.system("cd '" + path + "' && zip '" + dfile +
                          "' -r '" + sfile + "' > " + tmps + " 2>&1")
            else:
                sfiles = ''
                for sfile in sfile.split(','):
                    if not sfile:
                        continue
                    sfiles += " '" + sfile + "'"
                os.system("cd '" + path + "' && tar -zcvf '" +
                          dfile + "' " + sfiles + " > " + tmps + " 2>&1")
            self.setFileAccept(dfile)
            public.writeLog("TYPE_FILE", '文件压缩成功!', (sfile, dfile))
            return public.returnJson(True, '文件压缩成功!')
        except:
            return public.returnJson(False, '文件压缩失败!')

    # 计算文件数量
    def getFilesCount(self, path, search):
        i = 0
        for name in os.listdir(path):
            if search:
                if name.lower().find(search) == -1:
                    continue
            # if name[0:1] == '.':
            #     continue
            i += 1
        return i

    def getDir(self, path, page=1, page_size=10, search=None):
        data = {}
        dirnames = []
        filenames = []

        info = {}
        info['count'] = self.getFilesCount(path, search)
        info['row'] = page_size
        info['p'] = page
        info['tojs'] = 'getFiles'
        pageObj = public.getPageObject(info, '1,2,3,4,5,6,7,8')
        data['PAGE'] = pageObj[0]

        i = 0
        n = 0
        for filename in os.listdir(path):
            if search:
                if filename.lower().find(search) == -1:
                    continue
            i += 1
            if n >= pageObj[1].ROW:
                break
            if i < pageObj[1].SHIFT:
                continue

            try:
                filePath = (path + '/' + filename).encode('utf8')
                link = ''
                if os.path.islink(filePath):
                    filePath = os.readlink(filePath)
                    link = ' -> ' + filePath
                    if not os.path.exists(filePath):
                        filePath = path + '/' + filePath
                    if not os.path.exists(filePath):
                        continue

                stat = os.stat(filePath)
                accept = str(oct(stat.st_mode)[-3:])
                mtime = str(int(stat.st_mtime))
                user = ''
                try:
                    user = pwd.getpwuid(stat.st_uid).pw_name
                except:
                    user = str(stat.st_uid)
                size = str(stat.st_size)
                if os.path.isdir(filePath):
                    dirnames.append(filename + ';' + size + ';' +
                                    mtime + ';' + accept + ';' + user + ';' + link)
                else:
                    filenames.append(filename + ';' + size + ';' +
                                     mtime + ';' + accept + ';' + user + ';' + link)
                n += 1
            except:
                continue

        data['DIR'] = sorted(dirnames)
        data['FILES'] = sorted(filenames)
        if path[0:2] == '//':
            data['PATH'] = path[1:]
        else:
            data['PATH'] = path
        return public.getJson(data)
