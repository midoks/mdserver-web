#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import random
import sys
import subprocess
import time

sys.path.append("/usr/local/lib/python2.7/site-packages")

conn = mdb.connect(host='0.0.0.0',
                   port=3306,
                   user='xxx',
                   passwd='xxx',
                   db='xxx',
                   charset='utf8')
conn.autocommit(True)
cursor = conn.cursor()


sql = 'select id from xxx order by id desc limit 1'
r = cursor.execute(sql)

count = 0
for info in cursor.fetchall():
    count = info[0]
conn.close()


def execShell(cmdstring, cwd=None, timeout=None, shell=True):

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

length = 100
for x in xrange(1, count / length + 1):
    y = x * length
    cmd = 'curl  --basic -u admin:admin "http://127.0.0.1:8983/solr/sodht/dataimport?command=full-import&wt=json&clean=false&commit=true&length=' + \
        str(length) + '&offset=' + str(y) + '"'
    print execShell(cmd)
