# coding: utf-8

import psutil
import time
import os
import sys
import public
import re
import json
import pwd

from flask import request
from flask import send_file, send_from_directory
from flask import make_response


class files_api:

    def __init__(self):
        pass

    ##### ----- start ----- ###
    def getBodyApi(self):
        path = request.form.get('path', '').encode('utf-8')
        return self.getBody(path)

    def getLastBodyApi(self):
        path = request.form.get('path', '').encode('utf-8')
        line = request.form.get('line', '100')

        if not os.path.exists(path):
            return public.returnJson(False, '文件不存在', (path,))

        try:
            data = public.getNumLines(path, int(line))
            print data
            return public.returnJson(True, 'OK', data)
        except Exception as ex:
            return public.returnJson(False, u'无法正确读取文件!' + str(ex))

    def saveBodyApi(self):
        path = request.form.get('path', '').encode('utf-8')
        data = request.form.get('data', '').encode('utf-8')
        encoding = request.form.get('encoding', '').encode('utf-8')
        return self.saveBody(path, data, encoding)

    def downloadApi(self):
        filename = request.args.get('filename', '').encode('utf-8')
        if not os.path.exists(filename):
            return ''
        response = make_response(send_from_directory(
            os.path.dirname(filename), os.path.basename(filename), as_attachment=True))
        return response

    def zipApi(self):
        sfile = request.form.get('sfile', '').encode('utf-8')
        dfile = request.form.get('dfile', '').encode('utf-8')
        stype = request.form.get('type', '').encode('utf-8')
        path = request.form.get('path', '').encode('utf-8')
        return self.zip(sfile, dfile, stype, path)

    def deleteApi(self):
        path = request.form.get('path', '').encode('utf-8')
        return self.delete(path)

    def fileAccessApi(self):
        filename = request.form.get('filename', '').encode('utf-8')
        data = self.getAccess(filename)
        return public.getJson(data)

    def getDirSizeApi(self):
        path = request.form.get('path', '').encode('utf-8')
        if public.getOs() == 'darwin':
            tmp = public.execShell('du -sh ' + path)
        else:
            tmp = public.execShell('du -sbh ' + path)
        return public.returnJson(True, tmp[0].split()[0])

    def getDirApi(self):
        path = request.form.get('path', '').encode('utf-8')
        if not os.path.exists(path):
            path = public.getRootDir() + "/wwwroot"
        search = request.args.get('search', '').strip().lower()
        page = request.args.get('p', '1').strip().lower()
        row = request.args.get('showRow', '10')
        return self.getDir(path, int(page), int(row), search)
    ##### ----- end ----- ###

    def setFileAccept(self, filename):
        auth = 'www:www'
        if public.getOs() == 'darwin':
            user = public.execShell(
                "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
            auth = user + ':staff'
        os.system('chown -R ' + auth + ' ' + filename)
        os.system('chmod -R 755 ' + filename)

    # 移动到回收站
    def mvRecycleBin(self, path):
        rPath = public.getRootDir() + '/recycle_bin/'
        if not os.path.exists(rPath):
            os.system('mkdir -p ' + rPath)

        rFile = rPath + path.replace('/', '_mw_') + '_t_' + str(time.time())
        try:
            import shutil
            shutil.move(path, rFile)
            public.writeLog('TYPE_FILE', public.getInfo(
                '移动文件[{1}]到回收站成功!', (path)))
            return True
        except:
            public.writeLog('TYPE_FILE', public.getInfo(
                '移动文件[{1}]到回收站失败!', (path)))
            return False

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

    def delete(self, path):

        if not os.path.exists(path):
            return public.returnJson(False, '指定文件不存在!')

        # 检查是否为.user.ini
        if path.find('.user.ini') >= 0:
            os.system("chattr -i '" + path + "'")

        try:
            if os.path.exists('data/recycle_bin.pl'):
                if self.mvRecycleBin(path):
                    return public.returnJson(True, '已将文件移动到回收站!')
            os.remove(path)
            public.writeLog('TYPE_FILE', public.getInfo(
                '删除文件[{1}]成功!', (path)))
            return public.returnJson(True, '删除文件成功!')
        except:
            return public.returnJson(False, '删除文件失败!')

    def getAccess(self, filename):
        data = {}
        try:
            stat = os.stat(filename)
            data['chmod'] = str(oct(stat.st_mode)[-3:])
            data['chown'] = pwd.getpwuid(stat.st_uid).pw_name
        except:
            data['chmod'] = 755
            data['chown'] = 'www'
        return data

        # 计算文件数量
    def getCount(self, path, search):
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
        info['count'] = self.getCount(path, search)
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
