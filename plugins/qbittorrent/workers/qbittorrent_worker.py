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
        self.has_suffix = ['.mp4']

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

    def ffmpeg(self, file=''):
        md5file = self.md5(file)
        m3u8_dir = FILE_TO + '/m3u8/' + md5file[0:6]
        os.system('mkdir -p ' + m3u8_dir)
        m3u8_file = m3u8_dir + '/' + md5file[0:6] + '.m3u8'

        tofile = FILE_TO + '/m3u8/' + md5file[0:6] + '/%03d.ts'
        cmd = 'ffmpeg -i ' + file + ' -c copy -map 0 -f segment -segment_list ' + \
            m3u8_file + ' -segment_time 5 ' + tofile
        print cmd
        data = self.execShell(cmd)
        print data
        if data[0] != '':
            print data

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
            torrents = self.qb.torrents()
            tlen = len(torrents)
            if tlen > 0:
                print "downloading torrents count:", tlen
                for torrent in torrents:
                    print torrent
            else:
                print time.time(), "no task!"
            time.sleep(10)

    def completed(self):
        while True:
            torrents = self.qb.torrents(filter='completed')
            tlen = len(torrents)
            print "completed torrents count:", tlen
            if tlen > 0:
                for torrent in torrents:
                    path = torrent['save_path'] + torrent['name']
                    self.video_do(path)
                print time.time(), "done task!"
            else:
                print time.time(), "no task!"
            time.sleep(3)


def test():
    while True:
        print time.time(), "no download task!",
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
