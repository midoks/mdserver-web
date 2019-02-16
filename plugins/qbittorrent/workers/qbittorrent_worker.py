#!/usr/bin/env python
# encoding: utf-8
"""
下载检测
"""

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

section_task = cp.sections()[3]
TASK_RATE = cp.getint(section_task, "TASK_RATE")
TASK_COMPLETED_RATE = cp.getint(section_task, "TASK_COMPLETED_RATE")


def formatTime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


class downloadBT(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.setDaemon(True)
        self.dbconn = mdb.connect(
            DB_HOST, DB_USER, DB_PASS, DB_NAME, port=DB_PORT, charset='utf8')
        self.dbconn.autocommit(False)
        self.dbcurr = self.dbconn.cursor()
        self.dbcurr.execute('SET NAMES utf8')
        self.qb = self.qb()

        _has_suffix = ['mp4', 'rmvb', 'flv', 'avi', 'mpg', 'mkv', 'wmv', 'avi']
        has_suffix = []
        for x in range(len(_has_suffix)):
            has_suffix.append('.' + _has_suffix[x])
            has_suffix.append('.' + _has_suffix[x].upper())
        self.has_suffix = has_suffix

    def query(self, sql):
        self.dbcurr.execute(sql)
        result = self.dbcurr.fetchall()
        data = map(list, result)
        return data

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

    def get_transfer_ts_file(self, to):
        return FILE_TRANSFER_TO + '/' + to + '.ts'

    def get_transfer_mp4_file(self, to):
        return FILE_TRANSFER_TO + '/' + to + '.mp4'

    def get_lock_file(self, to):
        return FILE_TRANSFER_TO + '/' + to + '.lock'

    def get_transfer_m3u5_dir(self, dirname):
        return FILE_TO + '/m3u8/' + dirname

    def fg_transfer_mp4_cmd(self, sfile, dfile):
        cmd = 'ffmpeg -y -i "' + sfile + \
            '" -threads 1  -preset veryslow -crf 28 -c:v libx264 -strict -2 ' + dfile
        return cmd

    def fg_transfer_ts_cmd(self, file, to_file):
        cmd = 'ffmpeg -y -i ' + file + \
            ' -s 480x360 -vcodec copy -acodec copy -vbsf h264_mp4toannexb ' + to_file
        return cmd

    def fg_m3u8_cmd(self, ts_file, m3u8_file, to_file):
        cmd = 'ffmpeg -y -i ' + ts_file + ' -c copy -map 0 -f segment -segment_list ' + \
            m3u8_file + ' -segment_time 3 ' + to_file
        return cmd

    def debug(self, msg):
        return formatTime() + ":" + msg

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

    def ffmpeg(self, file=''):

        md5file = self.md5(file)[0:6]

        if not os.path.exists(file):
            print formatTime(), 'file not exists:', file
            return
        print self.debug('source file ' + file)

        mp4file = self.get_transfer_mp4_file(md5file)
        cmd_mp4 = self.fg_transfer_mp4_cmd(file, mp4file)
        print self.debug('cmd_mp4:' + cmd_mp4)

        if not os.path.exists(mp4file):
            os.system(cmd_mp4)
        else:
            print self.debug('mp4 exists:' + mp4file)

        if not os.path.exists(mp4file):
            print self.debug('mp4 not exists')
            return

        tsfile = self.get_transfer_ts_file(md5file)
        cmd_ts = self.fg_transfer_ts_cmd(mp4file, tsfile)
        print self.debug('cmd_ts:' + cmd_ts)
        if not os.path.exists(tsfile):
            os.system(cmd_ts)
        else:
            print self.debug('data_ts exists:' + mp4file)

        if not os.path.exists(tsfile):
            print self.debug('ts not exists')
            return

        m3u8_dir = self.get_transfer_m3u5_dir(md5file)
        if not os.path.exists(m3u8_dir):
            self.execShell('mkdir -p ' + m3u8_dir)

        m3u8_file = m3u8_dir + '/' + md5file + '.m3u8'
        tofile = m3u8_dir + '/%010d.ts'
        cmd_m3u8 = self.fg_m3u8_cmd(tsfile, m3u8_file, tofile)
        print self.debug('cmd_m3u8:' + cmd_m3u8)
        if not os.path.exists(m3u8_file):
            os.system(cmd_m3u8)
            self.execShell('chown -R ' + FILE_OWN + ':' +
                           FILE_GROUP + ' ' + m3u8_dir)
            self.add_hash(md5file)
        else:
            self.add_hash(md5file)
            print self.debug('m3u8 exists:' + tofile)

    def add_hash_file(self):
        pass

    def add_hash(self, m3u8_name):
        print '-------------------------add_hash---start-----------------------'
        ct = formatTime()
        # print (self.sign_torrent)
        total_size = str(self.sign_torrent['total_size'])
        shash = self.sign_torrent['hash']
        sname = self.sign_torrent['name']

        info = self.query(
            "select id from pl_hash_list where info_hash='" + shash + "'")

        sname = mdb.escape_string(sname)
        if len(info) > 0:
            pid = str(info[0][0])
            file_data = self.query(
                "select id from pl_hash_file where name='" + sname + "' and pid='" + pid + "'")
            if len(file_data) == 0:
                self.query("insert into pl_hash_file (`pid`,`name`,`m3u8`,`length`,`create_time`) values('" +
                           pid + "','" + sname + "','" + m3u8_name + "','" + total_size + "','" + ct + "')")
            else:
                print shash, 'already is exists!'
        else:
            print 'insert into pl_hash_list'
            pid = self.dbcurr.execute("insert into pl_hash_list (`name`,`info_hash`,`length`,`create_time`) values('" +
                                      sname + "','" + shash + "','" + total_size + "','" + ct + "')")
            file_data = self.query(
                "select id from pl_hash_file where name='" + sname + "' and pid='" + pid + "'")
            if len(file_data) == 0:
                self.query("insert into pl_hash_file (`pid`,`name`,`m3u8`,`length`,`create_time`) values('" +
                           pid + "','" + sname + "','" + m3u8_name + "','" + total_size + "','" + ct + "')")
            else:
                print shash, 'already is exists!'
        print '-------------------------add_hash---end--------------------------'

    def file_arr(self, path, filters=['.DS_Store']):
        file_list = []
        flist = os.listdir(path)
        # print flist
        for i in range(len(flist)):
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
            t = os.path.splitext(flist[i])
            if t[1] in self.has_suffix:
                video.append(flist[i])
        return video

    def video_do(self, path):
        if os.path.isfile(path):
            t = os.path.splitext(path)
            if t[1] in self.has_suffix:
                self.ffmpeg(path)
        else:
            vlist = self.find_dir_video(path)
            for i in range(len(vlist)):
                self.ffmpeg(vlist[i])
        return ''

    def checkTask(self):
        while True:
            torrents = self.qb.torrents(filter='downloading')
            tlen = len(torrents)
            if tlen > 0:
                print "downloading torrents count:", tlen
                for torrent in torrents:
                    print torrent['name'], ' task downloading!'
            else:
                print formatTime(), "no downloading task!"
            time.sleep(TASK_RATE)

    def completed(self):
        while True:

            torrents = self.qb.torrents(filter='completed')
            tlen = len(torrents)
            print "completed torrents count:", tlen
            if tlen > 0:
                for torrent in torrents:
                    self.sign_torrent = torrent
                    # print torrent
                    path = torrent['save_path'] + torrent['name']
                    path = path.encode()
                    try:
                        self.video_do(path)
                    except Exception as e:
                        print formatTime(), str(e)

                print formatTime(), "done task!"
            else:
                print formatTime(), "no completed task!"
            time.sleep(TASK_COMPLETED_RATE)


def test():
    while True:
        print formatTime(), "no download task!",
        time.sleep(1)
        test()

if __name__ == "__main__":

    dl = downloadBT()

    import threading
    task = threading.Thread(target=dl.checkTask)
    task.start()

    completed = threading.Thread(target=dl.completed)
    completed.start()

    # test()
