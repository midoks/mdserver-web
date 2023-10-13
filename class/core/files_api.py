# coding: utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------
# 文件类操作
# ---------------------------------------------------------------------------------


import psutil
import time
import os
import sys
import mw
import re
import json
import pwd
import shutil

from flask import request
from flask import send_file, send_from_directory
from flask import make_response
from flask import session


class files_api:

    rPath = None

    def __init__(self):
        self.rPath = mw.getRootDir() + '/recycle_bin/'

    ##### ----- start ----- ###
    def getBodyApi(self):
        path = request.form.get('path', '')
        return self.getBody(path)

    def getLastBodyApi(self):
        path = request.form.get('path', '')
        line = request.form.get('line', '100')

        if not os.path.exists(path):
            return mw.returnJson(False, '文件不存在', (path,))

        try:
            data = mw.getLastLine(path, int(line))
            return mw.returnJson(True, 'OK', data)
        except Exception as ex:
            return mw.returnJson(False, '无法正确读取文件!' + str(ex))

    def saveBodyApi(self):
        path = request.form.get('path', '')
        data = request.form.get('data', '')
        encoding = request.form.get('encoding', '')
        return self.saveBody(path, data, encoding)

    def downloadApi(self):
        filename = request.args.get('filename', '')
        if not os.path.exists(filename):
            return ''

        is_attachment = True
        if filename.endswith(".svg"):
            is_attachment = False

        response = make_response(send_from_directory(
            os.path.dirname(filename), os.path.basename(filename), as_attachment=is_attachment))
        return response

    def zipApi(self):
        sfile = request.form.get('sfile', '')
        dfile = request.form.get('dfile', '')
        stype = request.form.get('type', '')
        path = request.form.get('path', '')
        return self.zip(sfile, dfile, stype, path)

    def unzipApi(self):
        sfile = request.form.get('sfile', '')
        dfile = request.form.get('dfile', '')
        stype = request.form.get('type', '')
        path = request.form.get('path', '')
        return self.unzip(sfile, dfile, stype, path)

    def uncompressApi(self):
        sfile = request.form.get('sfile', '')
        dfile = request.form.get('dfile', '')
        path = request.form.get('path', '')
        return self.uncompress(sfile, dfile, path)

    # 移动文件或目录
    def mvFileApi(self):
        sfile = request.form.get('sfile', '')
        dfile = request.form.get('dfile', '')
        if not self.checkFileName(dfile):
            return mw.returnJson(False, '文件名中不能包含特殊字符!')
        if not os.path.exists(sfile):
            return mw.returnJson(False, '指定文件不存在!')

        if not self.checkDir(sfile):
            return mw.returnJson(False, 'FILE_DANGER')

        import shutil
        try:
            shutil.move(sfile, dfile)
            msg = mw.getInfo('移动或重名命文件[{1}]到[{2}]成功!', (sfile, dfile,))
            mw.writeLog('文件管理', msg)
            return mw.returnJson(True, '移动或重名命文件成功!')
        except:
            return mw.returnJson(False, '移动或重名命文件失败!')

    def deleteApi(self):
        path = request.form.get('path', '')
        return self.delete(path)

    def fileAccessApi(self):
        filename = request.form.get('filename', '')
        data = self.getAccess(filename)
        return mw.getJson(data)

    def setFileAccessApi(self):

        if mw.isAppleSystem():
            return mw.returnJson(True, '开发机不设置!')

        filename = request.form.get('filename', '')
        user = request.form.get('user', '')
        access = request.form.get('access', '755')
        sall = '-R'
        try:
            if not self.checkDir(filename):
                return mw.returnJson(False, '请不要花样作死')

            if not os.path.exists(filename):
                return mw.returnJson(False, '指定文件不存在!')

            os.system('chmod ' + sall + ' ' + access + " '" + filename + "'")
            os.system('chown ' + sall + ' ' + user +
                      ':' + user + " '" + filename + "'")
            msg = mw.getInfo(
                '设置[{1}]权限为[{2}]所有者为[{3}]', (filename, access, user,))
            mw.writeLog('文件管理', msg)
            return mw.returnJson(True, '设置成功!')
        except:
            return mw.returnJson(False, '设置失败!')

    def getDirSizeApi(self):
        path = request.form.get('path', '')
        tmp = self.getDirSize(path)
        return mw.returnJson(True, tmp[0].split()[0])

    def getDirApi(self):
        path = request.form.get('path', '')
        if not os.path.exists(path):
            path = mw.getRootDir() + "/wwwroot"
        search = request.args.get('search', '').strip().lower()
        search_all = request.args.get('all', '').strip().lower()
        page = request.args.get('p', '1').strip().lower()
        row = request.args.get('showRow', '10')
        disk = request.form.get('disk', '')
        if disk == 'True':
            row = 1000

        # return self.getAllDir(path, int(page), int(row), "wp-inlcude")
        if search_all == 'yes' and search != '':
            return self.getAllDir(path, int(page), int(row), search)
        return self.getDir(path, int(page), int(row), search)

    def createFileApi(self):
        file = request.form.get('path', '')
        try:
            if not self.checkFileName(file):
                return mw.returnJson(False, '文件名中不能包含特殊字符!')
            if os.path.exists(file):
                return mw.returnJson(False, '指定文件已存在!')
            _path = os.path.dirname(file)
            if not os.path.exists(_path):
                os.makedirs(_path)
            open(file, 'w+').close()
            self.setFileAccept(file)
            msg = mw.getInfo('创建文件[{1}]成功!', (file,))
            mw.writeLog('文件管理', msg)
            return mw.returnJson(True, '文件创建成功!')
        except Exception as e:
            return mw.returnJson(True, '文件创建失败!')

    def createDirApi(self):
        path = request.form.get('path', '')
        try:
            if not self.checkFileName(path):
                return mw.returnJson(False, '目录名中不能包含特殊字符!')
            if os.path.exists(path):
                return mw.returnJson(False, '指定目录已存在!')
            os.makedirs(path)
            self.setFileAccept(path)
            msg = mw.getInfo('创建目录[{1}]成功!', (path,))
            mw.writeLog('文件管理', msg)
            return mw.returnJson(True, '目录创建成功!')
        except Exception as e:
            return mw.returnJson(False, '目录创建失败!')

    def downloadFileApi(self):
        import db
        import time
        url = request.form.get('url', '')
        path = request.form.get('path', '')
        filename = request.form.get('filename', '')
        execstr = url + '|mw|' + path + '/' + filename
        execstr = execstr.strip()
        mw.M('tasks').add('name,type,status,addtime,execstr',
                          ('下载文件[' + filename + ']', 'download', '-1', time.strftime('%Y-%m-%d %H:%M:%S'), execstr))

        # self.setFileAccept(path + '/' + filename)
        mw.triggerTask()
        return mw.returnJson(True, '已将下载任务添加到队列!')

    # 删除进程下的所有进程
    def removeTaskRecursion(self, pid):
        cmd = "ps -ef|grep " + pid + \
            " | grep -v grep |sed -n '2,1p' | awk '{print $2}'"
        sub_pid = mw.execShell(cmd)

        if sub_pid[0].strip() == '':
            return 'ok'

        self.removeTaskRecursion(sub_pid[0].strip())
        mw.execShell('kill -9 ' + sub_pid[0].strip())
        return sub_pid[0].strip()

    def removeTaskApi(self):
        import system_api
        mid = request.form.get('id', '')
        try:
            name = mw.M('tasks').where('id=?', (mid,)).getField('name')
            status = mw.M('tasks').where('id=?', (mid,)).getField('status')
            mw.M('tasks').delete(mid)
            if status == '-1':
                task_pid = mw.execShell(
                    "ps aux | grep 'task.py' | grep -v grep |awk '{print $2}'")

                task_list = task_pid[0].strip().split("\n")
                for i in range(len(task_list)):
                    self.removeTaskRecursion(task_list[i])

                mw.triggerTask()
                system_api.system_api().restartTask()
        except:
            system_api.system_api().restartTask()

        # 删除日志
        task_log = mw.getRunDir() + "/tmp/panelTask.pl"
        if os.path.exists(task_log):
            os.remove(task_log)
        return mw.returnJson(True, '任务已删除!')

    def uploadFileApi(self):
        # 上传文件
        from werkzeug.utils import secure_filename
        from flask import request

        path = request.args.get('path', '')

        if not os.path.exists(path):
            os.makedirs(path)
        f = request.files['zunfile']
        filename = os.path.join(path, f.filename)

        s_path = path
        if os.path.exists(filename):
            s_path = filename
        p_stat = os.stat(s_path)

        # print(filename)
        f.save(filename)
        os.chown(filename, p_stat.st_uid, p_stat.st_gid)
        os.chmod(filename, p_stat.st_mode)

        msg = mw.getInfo('上传文件[{1}] 到 [{2}]成功!', (filename, path))
        mw.writeLog('文件管理', msg)
        return mw.returnMsg(True, '上传成功!')

    # 设置文件和目录权限
    def setMode(self, path):
        s_path = os.path.dirname(path)
        p_stat = os.stat(s_path)
        os.chown(path, p_stat.st_uid, p_stat.st_gid)
        os.chmod(path, p_stat.st_mode)

    def uploadSegmentApi(self):
        # 分段上传
        path = request.form.get('path', '')
        name = request.form.get('name', '')
        size = request.form.get('size')
        start = request.form.get('start')
        dir_mode = request.form.get('dir_mode', '')
        file_mode = request.form.get('file_mode', '')

        if not mw.fileNameCheck(name):
            return mw.returnJson(False, '文件名中不能包含特殊字符!')

        if path == '/':
            return mw.returnJson(False, '不能直接上传文件到系统根目录!')

        if name.find('./') != -1 or path.find('./') != -1:
            return mw.returnJson(False, '错误的参数')

        if not os.path.exists(path):
            os.makedirs(path, 493)
            if not dir_mode != '' or not file_mode != '':
                mw.setMode(path)

        save_path = os.path.join(
            path, name + '.' + str(int(size)) + '.upload.tmp')
        d_size = 0
        if os.path.exists(save_path):
            d_size = os.path.getsize(save_path)

        if d_size != int(start):
            return str(d_size)

        f = open(save_path, 'ab')
        b64_data = request.form.get('b64_data', '0')
        if b64_data == '1':
            import base64
            b64_data = base64.b64decode(args.b64_data)
            f.write(b64_data)
        else:
            upload_files = request.files.getlist("blob")
            for tmp_f in upload_files:
                f.write(tmp_f.read())

        f.close()
        f_size = os.path.getsize(save_path)
        if f_size != int(size):
            return str(f_size)

        new_name = os.path.join(path, name)
        if os.path.exists(new_name):
            if new_name.find('.user.ini') != -1:
                mw.execShell("chattr -i " + new_name)
            try:
                os.remove(new_name)
            except:
                mw.execShell("rm -f %s" % new_name)

        os.renames(save_path, new_name)

        if dir_mode != '' and dir_mode != '':
            mode_tmp1 = dir_mode.split(',')
            mw.setMode(path, mode_tmp1[0])
            mw.setOwn(path, mode_tmp1[1])
            mode_tmp2 = file_mode.split(',')
            mw.setMode(new_name, mode_tmp2[0])
            mw.setOwn(new_name, mode_tmp2[1])
        else:
            self.setMode(new_name)

        msg = mw.getInfo('上传文件[{1}] 到 [{2}]成功!', (new_name, path))
        mw.writeLog('文件管理', msg)
        return mw.returnMsg(True, '上传成功!')

    def getRecycleBinApi(self):
        rPath = self.rPath
        if not os.path.exists(rPath):
            os.system('mkdir -p ' + rPath)
        data = {}
        data['dirs'] = []
        data['files'] = []
        data['status'] = os.path.exists('data/recycle_bin.pl')
        data['status_db'] = os.path.exists('data/recycle_bin_db.pl')
        for file in os.listdir(rPath):
            try:
                tmp = {}
                fname = rPath + file
                tmp1 = file.split('_mw_')
                tmp2 = tmp1[len(tmp1) - 1].split('_t_')
                tmp['rname'] = file
                tmp['dname'] = file.replace('_mw_', '/').split('_t_')[0]
                tmp['name'] = tmp2[0]
                tmp['time'] = int(float(tmp2[1]))
                if os.path.islink(fname):
                    filePath = os.readlink(fname)
                    link = ' -> ' + filePath
                    if os.path.exists(filePath):
                        tmp['size'] = os.path.getsize(filePath)
                    else:
                        tmp['size'] = 0
                else:
                    tmp['size'] = os.path.getsize(fname)
                if os.path.isdir(fname):
                    data['dirs'].append(tmp)
                else:
                    data['files'].append(tmp)
            except Exception as e:
                continue
        return mw.returnJson(True, 'OK', data)

    # 回收站开关
    def recycleBinApi(self):
        c = 'data/recycle_bin.pl'
        db = request.form.get('db', '')
        if db != '':
            c = 'data/recycle_bin_db.pl'
        if os.path.exists(c):
            os.remove(c)
            mw.writeLog('文件管理', '已关闭回收站功能!')
            return mw.returnJson(True, '已关闭回收站功能!')
        else:
            mw.writeFile(c, 'True')
            mw.writeLog('文件管理', '已开启回收站功能!')
            return mw.returnJson(True, '已开启回收站功能!')

    def reRecycleBinApi(self):
        rPath = self.rPath
        path = request.form.get('path', '')
        dFile = path.replace('_mw_', '/').split('_t_')[0]
        try:
            import shutil
            shutil.move(rPath + path, dFile)
            msg = mw.getInfo('移动文件[{1}]到回收站成功!', (dFile,))
            mw.writeLog('文件管理', msg)
            return mw.returnJson(True, '恢复成功!')
        except Exception as e:
            msg = mw.getInfo('从回收站恢复[{1}]失败!', (dFile,))
            mw.writeLog('文件管理', msg)
            return mw.returnJson(False, '恢复失败!')

    def delRecycleBinApi(self):
        rPath = self.rPath
        path = request.form.get('path', '')
        empty = request.form.get('empty', '')
        dFile = path.split('_t_')[0]

        if not self.checkDir(path):
            return mw.returnJson(False, '敏感目录,请不要花样作死!')

        mw.execShell('which chattr && chattr -R -i ' + rPath + path)
        if os.path.isdir(rPath + path):
            import shutil
            shutil.rmtree(rPath + path)
        else:
            os.remove(rPath + path)

        tfile = path.replace('_mw_', '/').split('_t_')[0]
        msg = mw.getInfo('已彻底从回收站删除{1}!', (tfile,))
        mw.writeLog('文件管理', msg)
        return mw.returnJson(True, msg)

    # 获取进度
    def getSpeedApi(self):
        data = mw.getSpeed()
        return mw.returnJson(True, '已清空回收站!', data)

    def closeRecycleBinApi(self):
        rPath = self.rPath
        mw.execShell('which chattr && chattr -R -i ' + rPath)
        rlist = os.listdir(rPath)
        i = 0
        l = len(rlist)
        for name in rlist:
            i += 1
            path = rPath + name
            mw.writeSpeed(name, i, l)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        mw.writeSpeed(None, 0, 0)
        mw.writeLog('文件管理', '已清空回收站!')
        return mw.returnJson(True, '已清空回收站!')

    def deleteDirApi(self):
        path = request.form.get('path', '')
        if not os.path.exists(path):
            return mw.returnJson(False, '指定文件不存在!')

        # 检查是否为.user.ini
        if path.find('.user.ini'):
            os.system("which chattr && chattr -i '" + path + "'")
        try:
            if os.path.exists('data/recycle_bin.pl'):
                if self.mvRecycleBin(path):
                    return mw.returnJson(True, '已将文件移动到回收站!')
            mw.execShell('rm -rf ' + path)
            mw.writeLog('文件管理', '删除文件成功！', (path,))
            return mw.returnJson(True, '删除文件成功!')
        except:
            return mw.returnJson(False, '删除文件失败!')

    def closeLogsApi(self):
        logPath = mw.getLogsDir()
        os.system('rm -f ' + logPath + '/*')
        os.system('kill -USR1 `cat ' + mw.getServerDir() +
                  'openresty/nginx/logs/nginx.pid`')
        mw.writeLog('文件管理', '网站日志已被清空!')
        tmp = self.getDirSize(logPath)
        return mw.returnJson(True, tmp[0].split()[0])

    def setBatchDataApi(self):
        path = request.form.get('path', '')
        stype = request.form.get('type', '')
        access = request.form.get('access', '')
        user = request.form.get('user', '')
        data = request.form.get('data')
        if stype == '1' or stype == '2':
            session['selected'] = {
                'path': path,
                'type': stype,
                'access': access,
                'user': user,
                'data': data
            }
            return mw.returnJson(True, '标记成功,请在目标目录点击粘贴所有按钮!')
        elif stype == '3':
            for key in json.loads(data):
                try:
                    filename = path + '/' + key
                    if not self.checkDir(filename):
                        return mw.returnJson(False, 'FILE_DANGER')
                    os.system('chmod -R ' + access + " '" + filename + "'")
                    os.system('chown -R ' + user + ':' +
                              user + " '" + filename + "'")
                except:
                    continue
            mw.writeLog('文件管理', '批量设置权限成功!')
            return mw.returnJson(True, '批量设置权限成功!')
        else:
            import shutil
            isRecyle = os.path.exists('data/recycle_bin.pl')
            data = json.loads(data)
            l = len(data)
            i = 0
            for key in data:
                try:
                    filename = path + '/' + key
                    topath = filename
                    if not os.path.exists(filename):
                        continue

                    i += 1
                    mw.writeSpeed(key, i, l)
                    if os.path.isdir(filename):
                        if not self.checkDir(filename):
                            return mw.returnJson(False, '请不要花样作死!')
                        if isRecyle:
                            self.mvRecycleBin(topath)
                        else:
                            shutil.rmtree(filename)
                    else:
                        if key == '.user.ini':
                            os.system('which chattr && chattr -i ' + filename)
                        if isRecyle:
                            self.mvRecycleBin(topath)
                        else:
                            os.remove(filename)
                except:
                    continue
                mw.writeSpeed(None, 0, 0)
            mw.writeLog('文件管理', '批量删除成功!')
            return mw.returnJson(True, '批量删除成功！')

    def checkExistsFilesApi(self):
        dfile = request.form.get('dfile', '')
        filename = request.form.get('filename', '')
        data = []
        filesx = []
        if filename == '':
            filesx = json.loads(session['selected']['data'])
        else:
            filesx.append(filename)

        for fn in filesx:
            if fn == '.':
                continue
            filename = dfile + '/' + fn
            if os.path.exists(filename):
                tmp = {}
                stat = os.stat(filename)
                tmp['filename'] = fn
                tmp['size'] = os.path.getsize(filename)
                tmp['mtime'] = str(int(stat.st_mtime))
                data.append(tmp)
        return mw.returnJson(True, 'ok', data)

    def batchPasteApi(self):
        path = request.form.get('path', '')
        stype = request.form.get('type', '')
        # filename = request.form.get('filename', '')
        import shutil
        if not self.checkDir(path):
            return mw.returnJson(False, '请不要花样作死!')
        i = 0
        myfiles = json.loads(session['selected']['data'])
        l = len(myfiles)
        if stype == '1':
            for key in myfiles:
                i += 1
                mw.writeSpeed(key, i, l)
                try:

                    sfile = session['selected'][
                        'path'] + '/' + key
                    dfile = path + '/' + key

                    if os.path.isdir(sfile):
                        shutil.copytree(sfile, dfile)
                    else:
                        shutil.copyfile(sfile, dfile)
                    stat = os.stat(sfile)
                    os.chown(dfile, stat.st_uid, stat.st_gid)
                except:
                    continue
            msg = mw.getInfo('从[{1}]批量复制到[{2}]成功',
                             (session['selected']['path'], path,))
            mw.writeLog('文件管理', msg)
        else:
            for key in myfiles:
                try:
                    i += 1
                    mw.writeSpeed(key, i, l)

                    sfile = session['selected'][
                        'path'] + '/' + key
                    dfile = path + '/' + key

                    shutil.move(sfile, dfile)
                except:
                    continue
            msg = mw.getInfo('从[{1}]批量移动到[{2}]成功',
                             (session['selected']['path'], path,))
            mw.writeLog('文件管理', msg)
        mw.writeSpeed(None, 0, 0)
        errorCount = len(myfiles) - i
        del(session['selected'])
        msg = mw.getInfo('批量操作成功[{1}],失败[{2}]', (str(i), str(errorCount)))
        return mw.returnJson(True, msg)

    def copyFileApi(self):
        sfile = request.form.get('sfile', '')
        dfile = request.form.get('dfile', '')

        if sfile == dfile:
            return mw.returnJson(False, '源与目的一致!')

        if not os.path.exists(sfile):
            return mw.returnJson(False, '指定文件不存在!')

        if os.path.isdir(sfile):
            return self.copyDir(sfile, dfile)

        try:
            import shutil
            shutil.copyfile(sfile, dfile)
            msg = mw.getInfo('复制文件[{1}]到[{2}]成功!', (sfile, dfile,))
            mw.writeLog('文件管理', msg)
            stat = os.stat(sfile)
            os.chown(dfile, stat.st_uid, stat.st_gid)
            return mw.returnJson(True, '文件复制成功!')
        except:
            return mw.returnJson(False, '文件复制失败!')

    ##### ----- end ----- ###

    def copyDir(self, sfile, dfile):

        if not os.path.exists(sfile):
            return mw.returnJson(False, '指定目录不存在!')

        if os.path.exists(dfile):
            return mw.returnJson(False, '指定目录已存在!')
        import shutil
        try:
            shutil.copytree(sfile, dfile)
            stat = os.stat(sfile)
            os.chown(dfile, stat.st_uid, stat.st_gid)
            msg = mw.getInfo('复制目录[{1}]到[{2}]成功!', (sfile, dfile))
            mw.writeLog('文件管理', msg)
            return mw.returnJson(True, '目录复制成功!')
        except:
            return mw.returnJson(False, '目录复制失败!')

    # 检查敏感目录
    def checkDir(self, path):
        # path = str(path, encoding='utf-8')
        path = path.replace('//', '/')
        if path[-1:] == '/':
            path = path[:-1]

        nDirs = ('',
                 '/',
                 '/*',
                 '/www',
                 '/root',
                 '/boot',
                 '/bin',
                 '/etc',
                 '/home',
                 '/dev',
                 '/sbin',
                 '/var',
                 '/usr',
                 '/tmp',
                 '/sys',
                 '/proc',
                 '/media',
                 '/mnt',
                 '/opt',
                 '/lib',
                 '/srv',
                 '/selinux',
                 '/www/server',
                 mw.getRootDir())

        return not path in nDirs

    def getDirSize(self, path):
        tmp = mw.execShell('du -sh ' + path)
        return tmp

    def checkFileName(self, filename):
        # 检测文件名
        nots = ['\\', '&', '*', '|', ';']
        if filename.find('/') != -1:
            filename = filename.split('/')[-1]
        for n in nots:
            if n in filename:
                return False
        return True

    def setFileAccept(self, filename):
        auth = 'www:www'
        if mw.getOs() == 'darwin':
            user = mw.execShell(
                "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
            auth = user + ':staff'

        os.system('chown -R ' + auth + ' ' + filename)
        os.system('chmod -R 755 ' + filename)

    # 移动到回收站
    def mvRecycleBin(self, path):
        rPath = self.rPath
        if not os.path.exists(rPath):
            os.system('mkdir -p ' + rPath)

        rFile = rPath + path.replace('/', '_mw_') + '_t_' + str(time.time())
        try:
            import shutil
            shutil.move(path, rFile)
            mw.writeLog('文件管理', mw.getInfo(
                '移动文件[{1}]到回收站成功!', (path)))
            return True
        except:
            mw.writeLog('文件管理', mw.getInfo(
                '移动文件[{1}]到回收站失败!', (path)))
            return False

    def getBody(self, path):
        if not os.path.exists(path):
            return mw.returnJson(False, '文件不存在', (path,))

        if os.path.getsize(path) > 2097152:
            return mw.returnJson(False, '不能在线编辑大于2MB的文件!')

        if os.path.isdir(path):
            return mw.returnJson(False, '这不是一个文件!')

        fp = open(path, 'rb')
        data = {}
        data['status'] = True
        if fp:
            srcBody = fp.read()
            fp.close()

            encoding_list = ['utf-8', 'GBK', 'BIG5']
            for el in encoding_list:
                try:
                    data['encoding'] = el
                    data['data'] = srcBody.decode(data['encoding'])
                    break
                except Exception as ex:
                    if el == 'BIG5':
                        return mw.returnJson(False, '文件编码不被兼容，无法正确读取文件!' + str(ex))
        else:
            return mw.returnJson(False, '文件未正常打开!')

        return mw.returnJson(True, 'OK', data)

    def saveBody(self, path, data, encoding='utf-8'):
        if not os.path.exists(path):
            return mw.returnJson(False, '文件不存在')
        try:
            if encoding == 'ascii':
                encoding = 'utf-8'

            data = data.encode(
                encoding, errors='ignore').decode(encoding)
            fp = open(path, 'w+', encoding=encoding)
            fp.write(data)
            fp.close()

            if path.find("web_conf") > 0:
                mw.restartWeb()

            mw.writeLog('文件管理', '文件[{1}]保存成功', (path,))
            return mw.returnJson(True, '文件保存成功')
        except Exception as ex:
            return mw.returnJson(False, '文件保存错误:' + str(ex))

    def zip(self, sfile, dfile, stype, path):
        if sfile.find(',') == -1:
            if not os.path.exists(path + '/' + sfile):
                return mw.returnMsg(False, '指定文件不存在!')

        try:
            tmps = mw.getRunDir() + '/tmp/panelExec.log'
            if stype == 'zip':
                mw.execShell("cd '" + path + "' && zip '" + dfile +
                             "' -r '" + sfile + "' > " + tmps + " 2>&1")
            else:
                sfiles = ''
                for sfile in sfile.split(','):
                    if not sfile:
                        continue
                    sfiles += " '" + sfile + "'"
                mw.execShell("cd '" + path + "' && tar -zcvf '" +
                             dfile + "' " + sfiles + " > " + tmps + " 2>&1")
            self.setFileAccept(dfile)
            mw.writeLog("文件管理", '文件[{1}]压缩[{2}]成功!', (sfile, dfile))
            return mw.returnJson(True, '文件压缩成功!')
        except:
            return mw.returnJson(False, '文件压缩失败!')

    def uncompress(self, sfile, dfile, path):
        if not os.path.exists(sfile):
            return mw.returnJson(False, '指定文件不存在!')

        filename = os.path.basename(sfile)
        extension = os.path.splitext(filename)[-1]
        extension = extension.strip('.')

        tar_gz = 'tar.gz'
        tar_gz_len = len(tar_gz)
        suffix_gz = sfile[-tar_gz_len:]
        if suffix_gz == tar_gz:
            extension = suffix_gz

        if not extension in ['tar.gz', 'gz', 'zip', 'rar']:
            return mw.returnJson(False, '现在仅支持gz,zip,rar格式解压!')

        if mw.isAppleSystem() and extension == 'rar':
            return mw.returnJson(False, 'macosx暂时不支持rar格式解压')

        try:
            tmps = mw.getRunDir() + '/tmp/panelExec.log'
            if extension == 'zip':
                cmd = "cd " + path + " && unzip -o -d '" + dfile + \
                    "' '" + sfile + "' > " + tmps + " 2>&1 &"
                mw.execShell(cmd)
            if extension == 'tar.gz':
                cmd = "cd " + path + " && tar -zxvf " + sfile + \
                    " -C " + dfile + " > " + tmps + " 2>&1 &"
                mw.execShell(cmd)
            if extension == 'gz':
                cmd = "cd " + path + " && gunzip -k " + sfile + " > " + tmps + " 2>&1 &"
                mw.execShell(cmd)
            if extension == 'rar':
                cmd = "cd " + path + " && unrar x " + sfile + \
                    " " + dfile + " > " + tmps + " 2>&1 &"
                mw.execShell(cmd)

            if os.path.exists(dfile):
                self.setFileAccept(dfile)
            mw.writeLog("文件管理", '文件[{1}]解压[{2}]成功!', (sfile, dfile))
            return mw.returnJson(True, '文件解压成功!')
        except Exception as e:
            return mw.returnJson(False, '文件解压失败!:' + str(e))

    def unzip(self, sfile, dfile, stype, path):
        if not os.path.exists(sfile):
            return mw.returnJson(False, '指定文件不存在!')

        try:
            tmps = mw.getRunDir() + '/tmp/panelExec.log'
            if stype == 'zip':
                mw.execShell("cd " + path + " && unzip -o -d '" + dfile +
                             "' '" + sfile + "' > " + tmps + " 2>&1 &")
            else:
                sfiles = ''
                for sfile in sfile.split(','):
                    if not sfile:
                        continue
                    sfiles += " '" + sfile + "'"
                mw.execShell("cd " + path + " && tar -zxvf " + sfiles +
                             " -C " + dfile + " > " + tmps + " 2>&1 &")

            self.setFileAccept(dfile)
            mw.writeLog("文件管理", '文件[{1}]解压[{2}]成功!', (sfile, dfile))
            return mw.returnJson(True, '文件解压成功!')
        except:
            return mw.returnJson(False, '文件解压失败!')

    def delete(self, path):

        if not os.path.exists(path):
            return mw.returnJson(False, '指定文件不存在!')

        # 检查是否为.user.ini
        if path.find('.user.ini') >= 0:
            mw.execShell("which chattr && chattr -i '" + path + "'")

        try:
            if os.path.exists('data/recycle_bin.pl'):
                if self.mvRecycleBin(path):
                    return mw.returnJson(True, '已将文件移动到回收站!')
            os.remove(path)
            mw.writeLog('文件管理', mw.getInfo(
                '删除文件[{1}]成功!', (path)))
            return mw.returnJson(True, '删除文件成功!')
        except:
            return mw.returnJson(False, '删除文件失败!')

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
            if name == '.':
                continue
            i += 1
        return i

    def getAllDir(self, path, page=1, page_size=10, search=None):
        # print("search:", search)
        data = {}
        dirnames = []
        filenames = []

        count = 0
        max_limit = 3000

        for d_list in os.walk(path):
            if count >= max_limit:
                break

            for d in d_list[1]:
                if count >= max_limit:
                    break
                if d.lower().find(search) != -1:
                    filename = d_list[0] + '/' + d
                    if not os.path.exists(filename):
                        continue
                    dirnames.append(self.__get_stats(filename, path))
                    count += 1

            for f in d_list[2]:
                if count >= max_limit:
                    break

                if f.lower().find(search) != -1:
                    filename = d_list[0] + '/' + f
                    if not os.path.exists(filename):
                        continue
                    filenames.append(self.__get_stats(filename, path))
                    count += 1

        data['DIR'] = sorted(dirnames)
        data['FILES'] = sorted(filenames)
        data['PATH'] = path.replace('//', '/')

        info = {}
        info['count'] = len(dirnames) + len(filenames)
        info['row'] = page_size
        info['p'] = page
        info['tojs'] = 'getFiles'
        pageObj = mw.getPageObject(info, '1,2,3,4,5,6,7,8')
        data['PAGE'] = pageObj[0]

        return mw.getJson(data)

    def getDir(self, path, page=1, page_size=10, search=None):
        data = {}
        dirnames = []
        filenames = []

        info = {}
        info['count'] = self.getCount(path, search)
        info['row'] = page_size
        info['p'] = page
        info['tojs'] = 'getFiles'
        pageObj = mw.getPageObject(info, '1,2,3,4,5,6,7,8')
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
                filePath = path + '/' + filename
                if not os.path.exists(filePath):
                    continue

                file_stats = self.__get_stats(filePath, path)
                if os.path.isdir(filePath):
                    dirnames.append(file_stats)
                else:
                    filenames.append(file_stats)
                n += 1
            except Exception as e:
                continue
        data['DIR'] = sorted(dirnames)
        data['FILES'] = sorted(filenames)
        data['PATH'] = path.replace('//', '/')

        return mw.getJson(data)

    def execShellApi(self):
        # 执行SHELL命令
        shell = request.form.get('shell', '').strip()
        path = request.form.get('path', '').strip()
        disabled = ['vi', 'vim', 'top', 'passwd', 'su']
        tmp = shell.split(' ')
        if tmp[0] in disabled:
            return mw.returnJson(False, '禁止执行[{}]'.format(tmp[0]))
        shellStr = '''#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
cd %s
%s
''' % (path, shell)
        mw.writeFile('/tmp/panelShell.sh', shellStr)
        mw.execShell(
            'nohup bash /tmp/panelShell.sh > /tmp/panelShell.pl 2>&1 &')
        return mw.returnJson(True, 'ok')

    def getExecShellMsgApi(self):
        # 取SHELL执行结果
        fileName = '/tmp/panelShell.pl'
        if not os.path.exists(fileName):
            return ''
        status = not mw.processExists('bash', None, '/tmp/panelShell.sh')
        return mw.returnJson(status, mw.getNumLines(fileName, 200))

    def __get_stats(self, filename, path=None):
        filename = filename.replace('//', '/')
        try:
            stat = os.stat(filename)
            accept = str(oct(stat.st_mode)[-3:])
            mtime = str(int(stat.st_mtime))
            user = ''
            try:
                user = str(pwd.getpwuid(stat.st_uid).pw_name)
            except:
                user = str(stat.st_uid)
            size = str(stat.st_size)
            link = ''
            if os.path.islink(filename):
                link = ' -> ' + os.readlink(filename)

            if path:
                tmp_path = (path + '/').replace('//', '/')
                filename = filename.replace(tmp_path, '', 1)

            return filename + ';' + size + ';' + mtime + ';' + accept + ';' + user + ';' + link
        except Exception as e:
            # print(e)
            return ';;;;;'
