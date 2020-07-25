#!/usr/bin/env python
# encoding: utf-8
"""
下载检测
"""

'''
pl_hash_list 表字段 status说明

0 视频资源 - 正常
1 不含有视频资源
2 3小时下载未反应
4 3个月未下载完成
'''

import hashlib
import os
import time
import datetime
import traceback
import sys
import json
import socket
import threading
from hashlib import sha1
from random import randint
from struct import unpack
from socket import inet_ntoa
from threading import Timer, Thread
from time import sleep

reload(sys)
sys.setdefaultencoding("utf8")

sys.path.append('/usr/local/lib/python2.7/site-packages')


def formatTime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def getRunDir():
    return os.getcwd()


def getRootDir():
    return os.path.dirname(os.path.dirname(getRunDir()))


def toSize(size):
    # 字节单位转换
    d = ('b', 'KB', 'MB', 'GB', 'TB')
    s = d[0]
    for b in d:
        if size < 1024:
            return str(round(size, 2)) + ' ' + b
        size = float(size) / 1024.0
        s = b
    return str(round(size, 2)) + ' ' + b

# import pygeoip
import MySQLdb as mdb

from configparser import ConfigParser
cp = ConfigParser()
cp.read("../qb.conf")
section_db = cp.sections()[0]
DB_HOST = cp.get(section_db, "DB_HOST")
DB_USER = cp.get(section_db, "DB_USER")
DB_PORT = cp.getint(section_db, "DB_PORT")
DB_PASS = cp.get(section_db, "DB_PASS")
DB_NAME = cp.get(section_db, "DB_NAME")


section_qb = cp.sections()[1]
QB_HOST = cp.get(section_qb, "QB_HOST")
QB_PORT = cp.get(section_qb, "QB_PORT")
QB_USER = cp.get(section_qb, "QB_USER")
QB_PWD = cp.get(section_qb, "QB_PWD")

section_file = cp.sections()[2]
FILE_TO = cp.get(section_file, "FILE_TO")
FILE_TRANSFER_TO = cp.get(section_file, "FILE_TRANSFER_TO")
FILE_OWN = cp.get(section_file, "FILE_OWN")
FILE_GROUP = cp.get(section_file, "FILE_GROUP")
FILE_ENC_SWITCH = cp.get(section_file, "FILE_ENC_SWITCH")
FILE_API_URL = cp.get(section_file, "FILE_API_URL")
FILE_ASYNC_SWITCH = cp.get(section_file, "FILE_ASYNC_SWITCH")


section_task = cp.sections()[3]
TASK_SIZE_LIMIT = cp.get(section_task, "TASK_SIZE_LIMIT")
TASK_RATE = cp.getint(section_task, "TASK_RATE")
TASK_COMPLETED_RATE = cp.getint(section_task, "TASK_COMPLETED_RATE")
TASK_DEBUG = cp.getint(section_task, "TASK_DEBUG")

section_setting = cp.sections()[4]
QUEUE_SWITCH = cp.get(section_setting, "QUEUE_SWITCH")
MAX_ACTIVE_UPLOADS = cp.getint(section_setting, "MAX_ACTIVE_UPLOADS")
MAX_ACTIVE_TORRENTS = cp.getint(section_setting, "MAX_ACTIVE_TORRENTS")
MAX_ACTIVE_DOWNLOADS = cp.getint(section_setting, "MAX_ACTIVE_DOWNLOADS")

rooDir = getRootDir()
tmp_cmd = rooDir + "/lib/ffmpeg/ffmpeg"
if os.path.exists(tmp_cmd):
    ffmpeg_cmd = tmp_cmd
else:
    ffmpeg_cmd = "/usr/local/bin/ffmpeg"


class downloadBT(Thread):

    __db_err = None

    def __init__(self):
        Thread.__init__(self)
        self.setDaemon(True)
        self.qb = self.qb()

        self.qb.set_preferences(max_active_uploads=MAX_ACTIVE_UPLOADS)
        self.qb.set_preferences(max_active_torrents=MAX_ACTIVE_TORRENTS)
        self.qb.set_preferences(max_active_downloads=MAX_ACTIVE_DOWNLOADS)

        _has_suffix = ['mp4', 'rmvb', 'flv', 'avi',
                       'mpg', 'mkv', 'wmv', 'avi', 'rm']
        has_suffix = []
        for x in range(len(_has_suffix)):
            has_suffix.append('.' + _has_suffix[x])
            has_suffix.append('.' + _has_suffix[x].upper())
        self.has_suffix = has_suffix
        self.__conn()

    def __conn(self):
        try:
            self.dbconn = mdb.connect(
                DB_HOST, DB_USER, DB_PASS, DB_NAME, port=DB_PORT, charset='utf8')
            self.dbconn.autocommit(False)
            self.dbcurr = self.dbconn.cursor()
            self.dbcurr.execute('SET NAMES utf8')
            return True
        except Exception as e:
            self.__db_err = e
            return False

    def __check(self):
        if self.__db_err:
            sys.exit('未连接数据库!')

    def __close(self):
        self.dbcurr.close()
        self.dbconn.close()

    def query(self, sql):
        # 执行SQL语句返回数据集
        if not self.__conn():
            return self.__db_err
        try:
            self.dbcurr.execute(sql)
            result = self.dbcurr.fetchall()
            # print result
            # 将元组转换成列表
            data = map(list, result)
            self.__close()
            return data
        except Exception, ex:
            return ex

    def execute(self, sql):
        if not self.__conn():
            return self.__db_err
        try:
            self.dbcurr.execute(sql)
            self.dbcurr.execute('SELECT LAST_INSERT_ID();')
            result = self.dbcurr.fetchone()
            self.dbconn.commit()
            self.__close()
            return result[0]
        except Exception, ex:
            return ex

    def qb(self):
        from qbittorrent import Client
        url = 'http://' + QB_HOST + ':' + QB_PORT + '/'
        qb = Client(url)
        qb.login(QB_USER, QB_PWD)
        return qb

    def execShell(self, cmdstring, cwd=None, timeout=None, shell=True):
        import subprocess
        if shell:
            cmdstring_list = cmdstring
        else:
            cmdstring_list = shlex.split(cmdstring)
        if timeout:
            end_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)

        sub = subprocess.Popen(cmdstring_list, cwd=cwd, stdin=subprocess.PIPE,
                               shell=shell, bufsize=4096, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while sub.poll() is None:
            time.sleep(0.1)
            if timeout:
                if end_time <= datetime.datetime.now():
                    raise Exception("Timeout：%s" % cmdstring)

        return sub.communicate()

    def md5(self, str):
        # 生成MD5
        try:
            m = hashlib.md5()
            m.update(str)
            return m.hexdigest()
        except:
            return False

    def readFile(self, filename):
        # 读文件内容
        try:
            fp = open(filename, 'r')
            fBody = fp.read()
            fp.close()
            return fBody
        except:
            return False

    def get_transfer_ts_file(self, to):
        return FILE_TRANSFER_TO + '/' + to + '.ts'

    def get_transfer_mp4_file(self, to):
        return FILE_TRANSFER_TO + '/' + to + '.mp4'

    def get_transfer_m3u5_dir(self, dirname, fname):
        return FILE_TO + '/m3u8/' + dirname + '/' + fname

    def get_transfer_hash_dir(self, dirname):
        return FILE_TO + '/m3u8/' + dirname

    def fg_transfer_mp4_cmd(self, sfile, dfile):
        cmd = ffmpeg_cmd + ' -y -i "' + sfile + \
            '" -threads 1  -preset veryslow -crf 28 -c:v libx264 -strict -2 ' + dfile
        return cmd

    def fg_transfer_ts_cmd(self, file, to_file):
        cmd = ffmpeg_cmd + ' -y -i ' + file + \
            ' -s 480x360 -vcodec copy -acodec copy -vbsf h264_mp4toannexb ' + to_file
        return cmd

    def fg_m3u8_cmd(self, ts_file, m3u8_file, to_file):
        cmd = ffmpeg_cmd + ' -y -i ' + ts_file + ' -c copy -map 0 -f segment -segment_list ' + \
            m3u8_file + ' -segment_time 3 ' + to_file
        return cmd

    def fg_m3u8enc_cmd(self, ts_file, m3u8_file, to_file, enc_dir):
        cmd = ffmpeg_cmd + ' -y -i ' + ts_file + ' -threads 1 -strict -2 -hls_time 3 -hls_key_info_file ' + \
            enc_dir + '/enc.keyinfo.txt -hls_playlist_type vod -hls_segment_filename ' + \
            to_file + ' ' + m3u8_file
        return cmd

    def debug(self, msg):
        return formatTime() + ":" + msg

    def get_lock_file(self, to):
        return '/tmp/mdw_qb_' + to + '.lock'

    def lock(self, sign):
        l = self.get_lock_file(sign)
        self.execShell('touch ' + l)

    def unlock(self, sign):
        l = self.get_lock_file(sign)
        self.execShell('rm -rf ' + l)

    def islock(self, sign):
        l = self.get_lock_file(sign)
        if os.path.exists(l):
            return True
        return False

    def ffmpeg_file_sync(self):
        if FILE_ASYNC_SWITCH == '1':
            runDir = getRunDir()
            sign = 'sync'

            print 'file_sync... start'
            if self.islock(sign):
                print self.debug('sync doing,already lock it!!!')
            else:
                self.lock(sign)

                r = self.execShell('sh -x ' + runDir + '/rsync.sh')
                print self.debug('file_sync:' + r[0])
                print self.debug('file_sync_error:' + r[1])
                self.unlock(sign)
            print 'file_sync... end'

    def ffmpeg_del_file(self, mp4, ts, m3u8_dir):
        print self.debug('delete middle file ... start ' + mp4)
        self.execShell('rm -rf ' + mp4)
        self.execShell('rm -rf ' + ts)
        print self.debug('delete middle file ... end ' + ts)

        # if os.path.exists(m3u8_dir):
        #     self.execShell('rm -rf ' + m3u8_dir)

    def ffmpeg_del_hfile(self, shash_dir):
        pass
        # print self.debug('delete middle hash dir ... start ' + shash_dir)

        # if os.path.exists(shash_dir):
        #     self.execShell('rm -rf ' + shash_dir)

        # print self.debug('delete middle hash dir ... end ' + shash_dir)

    def ffmpeg(self, file=''):
        if not os.path.exists(FILE_TRANSFER_TO):
            self.execShell('mkdir -p ' + FILE_TRANSFER_TO)

        fname = os.path.basename(file)
        shash = self.sign_torrent['hash']
        md5file = self.md5(file)
        if not os.path.exists(file):
            print formatTime(), 'file not exists:', file
            return
        print self.debug('source file ' + file)

        mp4file = self.get_transfer_mp4_file(md5file)
        cmd_mp4 = self.fg_transfer_mp4_cmd(file, mp4file)
        if not os.path.exists(mp4file):
            print self.debug('cmd_mp4:' + cmd_mp4)
            os.system(cmd_mp4)
        else:
            print self.debug('mp4 exists:' + mp4file)

        if not os.path.exists(mp4file):
            print self.debug('mp4 not exists')
            return

        tsfile = self.get_transfer_ts_file(md5file)
        cmd_ts = self.fg_transfer_ts_cmd(mp4file, tsfile)
        if not os.path.exists(tsfile):
            print self.debug('cmd_ts:' + cmd_ts)
            os.system(cmd_ts)
        else:
            print self.debug('data_ts exists:' + mp4file)

        if not os.path.exists(tsfile):
            print self.debug('ts not exists')
            return

        md5Fname = self.md5(fname)
        m3u8_dir = self.get_transfer_m3u5_dir(shash, md5Fname)
        if not os.path.exists(m3u8_dir):
            self.execShell('mkdir -p ' + m3u8_dir)

        m3u8_file = m3u8_dir + '/index.m3u8'
        tofile = m3u8_dir + '/%010d.ts'
        print self.debug('tofile:' + tofile)
        # 加密m3u8
        if FILE_ENC_SWITCH != '0':
            enc_dir = '/tmp/qb_m3u8'
            cmd = self.fg_m3u8enc_cmd(tsfile, m3u8_file, tofile, enc_dir)
            if os.path.exists(m3u8_file):
                print self.debug('cmd_m3u8_enc exists:' + m3u8_file)
                print self.debug('cmd_m3u8_enc:' + cmd)
                self.ffmpeg_file_sync()
                self.ffmpeg_del_file(mp4file, tsfile, m3u8_dir)
                return

            self.execShell('mkdir -p ' + enc_dir)
            self.execShell('openssl rand  -base64 16 > ' +
                           enc_dir + '/enc.key')
            self.execShell('rm -rf ' + enc_dir + '/enc.keyinfo.txt')

            try:
                fid = self.add_hash(fname, md5Fname)
            except Exception as e:
                print 'add_hash_enc:' + str(e)
                return
            fid = self.add_hash(fname, md5Fname)
            key = self.readFile(enc_dir + '/enc.key').strip()
            self.set_hashfile_key(fid, key)

            # FILE_API_URL
            url = FILE_API_URL.replace('{$KEY}', fid)
            enc_url = 'echo ' + url + ' >> ' + enc_dir + '/enc.keyinfo.txt'
            self.execShell(enc_url)
            enc_path = 'echo ' + enc_dir + '/enc.key >> ' + enc_dir + '/enc.keyinfo.txt'
            self.execShell(enc_path)
            enc_iv = 'openssl rand -hex 16 >> ' + enc_dir + '/enc.keyinfo.txt'
            self.execShell(enc_iv)

            os.system(cmd)
        else:

            if os.path.exists(m3u8_file):
                print self.debug('m3u8 exists:' + tofile)
                if TASK_DEBUG == 0:
                    self.ffmpeg_file_sync()
                    self.ffmpeg_del_file(mp4file, tsfile, m3u8_dir)
            else:
                cmd_m3u8 = self.fg_m3u8_cmd(tsfile, m3u8_file, tofile)
                print self.debug('cmd_m3u8:' + cmd_m3u8)
                os.system(cmd_m3u8)

            try:
                self.add_hash(fname, md5Fname)
            except Exception as e:
                print 'add_hash', str(e)

        self.execShell('chown -R ' + FILE_OWN + ':' +
                       FILE_GROUP + ' ' + m3u8_dir)
        self.execShell('chmod -R 755 ' + m3u8_dir)

        if TASK_DEBUG == 0:
            self.ffmpeg_file_sync()
            self.ffmpeg_del_file(mp4file, tsfile, m3u8_dir)

    def get_bt_size(self, torrent):
        total_size = '0'
        if 'size' in torrent:
            total_size = str(torrent['size'])

        if 'total_size' in torrent:
            total_size = str(torrent['total_size'])
        return total_size

    def get_hashlist_id(self):
        ct = formatTime()

        total_size = self.get_bt_size(self.sign_torrent)

        shash = self.sign_torrent['hash']
        sname = self.sign_torrent['name']
        sname = mdb.escape_string(sname)

        info = self.query(
            "select id from pl_hash_list where info_hash='" + shash + "'")
        if len(info) > 0:
            pid = info[0][0]
        else:
            print 'insert into pl_hash_list data'
            pid = self.execute("insert into pl_hash_list (`name`,`info_hash`,`length`,`create_time`) values('" +
                               sname + "','" + shash + "','" + total_size + "','" + str(ct) + "')")
        return pid

    def set_hashlist_status(self, torrent, status):
        ct = formatTime()

        shash = torrent['hash']

        info = self.query(
            "select id from pl_hash_list where info_hash='" + shash + "'")
        if len(info) > 0:
            print 'set_hashlist_status update'
            usql = "update pl_hash_list set `status`='" + \
                str(status) + "' where info_hash='" + shash + "'"
            self.execute(usql)
        else:
            print 'set_hashlist_status insert'
            total_size = self.get_bt_size(torrent)
            sname = torrent['name']
            sname = mdb.escape_string(sname)
            return self.execute("insert into pl_hash_list (`name`,`info_hash`,`length`,`status`,`create_time`) values('" +
                                sname + "','" + shash + "','" + total_size + "','" + str(status) + "','" + ct + "')")

    def get_hashfile_id(self, fname, m3u8_name, pid):
        ct = formatTime()

        info = self.query(
            "select id from pl_hash_file where name='" + fname + "' and pid='" + str(pid) + "'")
        if len(info) == 0:
            print 'insert into pl_hash_file data !'
            fid = self.execute("insert into pl_hash_file (`pid`,`name`,`m3u8`,`create_time`) values('" +
                               str(pid) + "','" + fname + "','" + m3u8_name + "','" + ct + "')")
        else:
            print fname, ':', m3u8_name, 'already is exists!'
            fid = str(info[0][0])
        return fid

    def set_hashfile_key(self, fid, key):
        self.execute("update pl_hash_file set `key`='" +
                     mdb.escape_string(key) + "' where id=" + fid)

    def add_queue(self, shash, size):
        ct = formatTime()

        info = self.query(
            "select id from pl_hash_queue where info_hash='" + shash + "'")
        if len(info) == 0:
            sql = "insert into pl_hash_queue (`info_hash`,`length`,`created_at`,`updated_at`) values('" + \
                shash + "','" + str(size) + "','" + ct + "','" + ct + "')"
            return self.execute(sql)
        else:
            print 'queue:', shash,  'already is exists!'

    def add_hash(self, fname, m3u8_name):
        print '-------------------------add_hash---start-----------------------'

        pid = self.get_hashlist_id()
        fid = 0
        if pid:
            fid = self.get_hashfile_id(fname, m3u8_name, pid)

        print '-------------------------add_hash---end--------------------------'
        return fid

    def file_arr(self, path, filters=['.DS_Store']):
        file_list = []
        flist = os.listdir(path)

        for i in range(len(flist)):
            # 下载缓存文件过滤
            if flist[i] == '.unwanted':
                continue

            file_path = os.path.join(path, flist[i])
            if flist[i] in filters:
                continue
            if os.path.isdir(file_path):
                tmp = self.file_arr(file_path, filters)
                file_list.extend(tmp)
            else:
                file_list.append(file_path)
        return file_list

    def find_dir_video(self, path):
        flist = self.file_arr(path)
        video = []
        for i in range(len(flist)):
            if self.is_video(flist[i]):
                video.append(flist[i])
        return video

    def video_do(self, path):
        if os.path.isfile(path):
            if self.is_video(path):
                self.ffmpeg(path)
        else:
            vlist = self.find_dir_video(path)
            for v in vlist:
                self.ffmpeg(v)
        return ''

    def is_video(self, path):
        t = os.path.splitext(path)
        if t[1] in self.has_suffix:
            return True
        return False

    def non_download(self, torrent):
        flist = self.qb.get_torrent_files(torrent['hash'])
        is_video = False
        for pos in range(len(flist)):
            file = torrent['save_path'] + flist[pos]['name']
            if not self.is_video(file):
                self.qb.set_file_priority(torrent['hash'], pos, 0)
            else:
                is_video = True

        # is video
        if not is_video:
            self.set_status(torrent, 1)

    def set_status(self, torrent, status):
        self.set_hashlist_status(torrent, status)
        if TASK_DEBUG == 0 and status != 0:
            self.qb.delete_permanently(torrent['hash'])

    def is_downloading(self, torrent):
        if torrent['name'] == torrent['hash']:
            return True
        else:
            return False

    def is_nondownload_overtime(self, torrent, sec):
        ct = time.time()
        use_time = int(ct) - int(torrent['added_on'])

        flist = self.qb.get_torrent_files(torrent['hash'])
        # print flist
        flist_len = len(flist)
        # 没有获取种子信息
        # print 'ddd:',flist_len,use_time,sec
        if flist_len == 0 and use_time > sec:
            self.set_status(torrent, 2)
            return True

        is_video_download = False

        # 获取了种子信息,但是没有下载
        for pos in range(len(flist)):
            file = torrent['save_path'] + flist[pos]['name']
            if self.is_video(file):
                if flist[pos]['progress'] != '0':
                    is_video_download = True

        if not is_video_download and use_time > sec:
            self.set_status(torrent, 3)
            return True
        return False

    def is_downloading_overtime(self, torrent, sec):
        ct = time.time()
        use_time = int(ct) - int(torrent['added_on'])
        if use_time > sec:
            self.set_status(torrent, 4)
            return True
        return False

    def is_downloading_overlimit(self, torrent):
        sz = self.get_bt_size(torrent)
        ct = formatTime()
        size_limit = float(TASK_SIZE_LIMIT) * 1024 * 1024 * 1024
        size_limit = int(size_limit)
        print 'is_downloading_overlimit:', toSize(sz), toSize(size_limit)
        if int(sz) > int(size_limit):
            print 'overlimit sz:' + sz
            self.add_queue(torrent['hash'], str(sz))
            self.qb.delete_permanently(torrent['hash'])

    def check_task(self):
        while True:
            self.__check()
            torrents = self.qb.torrents(filter='downloading')
            tlen = len(torrents)
            if tlen > 0:
                print "downloading torrents count:", tlen
                for torrent in torrents:
                    if self.is_nondownload_overtime(torrent, 5 * 60):
                        pass
                    elif self.is_downloading_overtime(torrent, 7 * 24 * 60 * 60):
                        pass
                    elif self.is_downloading(torrent):
                        pass
                    elif self.is_downloading_overlimit(torrent):
                        pass
                    else:
                        self.non_download(torrent)
                    print torrent['name'], ' task downloading!'
            else:
                print self.debug("no downloading task!")
            time.sleep(TASK_RATE)

    def completed(self):
        while True:
            self.__check()
            torrents = self.qb.torrents(filter='completed')
            if not torrents:
                continue
            tlen = len(torrents)
            print "completed torrents count:", tlen
            if tlen > 0:
                for torrent in torrents:
                    self.sign_torrent = torrent
                    path = torrent['save_path'] + torrent['name']
                    path = path.encode()
                    try:
                        self.video_do(path)

                        hash_dir = self.get_transfer_hash_dir(torrent['hash'])
                        if TASK_DEBUG == 0:
                            self.ffmpeg_del_hfile(hash_dir)
                            self.qb.delete_permanently(torrent['hash'])
                    except Exception as e:
                        print formatTime(), str(e)
                print self.debug("done task!")
            else:
                print self.debug("no completed task!")
            time.sleep(TASK_COMPLETED_RATE)

    def add_hash_task(self, shash):
        url = 'magnet:?xt=urn:btih:' + shash
        self.qb.download_from_link(url)
        print self.debug('queue add_hash_task is ok ... ')

    def queue(self):
        while True:
            if QUEUE_SWITCH == '1':
                print self.debug("------------ do queue task start! ---------------")

                setting = self.qb.preferences()
                torrents = self.qb.torrents()
                tlen = len(torrents)
                # print tlen, setting['max_active_torrents']
                add = int(setting['max_active_torrents']) - tlen

                if add == 0:
                    print self.debug('the download queue is full ... ')
                else:
                    size_limit = float(TASK_SIZE_LIMIT) * 1024 * 1024 * 1024
                    size_limit = int(size_limit)
                    size_sql_where = ''
                    size_sql = ''
                    if size_limit != 0:
                        size_sql = ',`length` desc '
                        size_sql_where = 'where `length`<=' + str(size_limit)

                    sql = "select * from pl_hash_queue " + size_sql_where + \
                        " order by created_at desc " + \
                        size_sql + "  limit " + str(add)
                    info = self.query(sql)
                    info_len = len(info)

                    if info_len == 0:
                        print self.debug('queue data is empty ... ')
                    else:
                        for x in range(info_len):
                            self.add_hash_task(info[x][1])
                            self.execute(
                                'delete from pl_hash_queue where id=' + str(info[x][0]))
                        print self.debug("------------ do queue task end ! ---------------")
            time.sleep(TASK_RATE)


def test():
    while True:
        print self.debug("no download task!")
        time.sleep(1)
        test()

if __name__ == "__main__":

    dl = downloadBT()

    import threading
    check_task = threading.Thread(target=dl.check_task)
    check_task.start()

    completed = threading.Thread(target=dl.completed)
    completed.start()

    queue = threading.Thread(target=dl.queue)
    queue.start()
