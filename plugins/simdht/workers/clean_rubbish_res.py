#!/usr/bin/env python
#coding: utf8

import MySQLdb as mdb
import MySQLdb.cursors

SRC_HOST = '127.0.0.1'
SRC_USER = 'root'
SRC_PASS = ''
DATABASE_NAME = ''
DST_HOST = '127.0.0.1'
DST_USER = 'root'
DST_PASS = ''


src_conn = mdb.connect(SRC_HOST, SRC_USER, SRC_PASS, DATABASE_NAME, charset='utf8', cursorclass=MySQLdb.cursors.DictCursor)
src_curr = src_conn.cursor()
src_curr.execute('SET NAMES utf8')

dst_conn = mdb.connect(DST_HOST, DST_USER, DST_PASS, 'rt_main', port=9306, charset='utf8')
dst_curr = dst_conn.cursor()
dst_curr.execute('SET NAMES utf8')

def delete(resname):
    onetimecount = 20;
    while True:
        ret = dst_curr.execute('select id from rt_main where match(\'*%s*\') limit %s'%(resname,onetimecount))
        if ret < 0:
            print 'done'
            break
        result = list(dst_curr.fetchall())
        for id in iter(result):
            src_curr.execute('select info_hash from search_hash where id = %s'%(id))
            info_hash = src_curr.fetchall()
            for hash in iter(info_hash):
                src_curr.execute('delete from search_filelist where info_hash = \'%s\''%(hash['info_hash']))
            src_curr.execute('delete from search_hash where id = %s'%(id))
            dst_curr.execute('delete from rt_main where id = %s'%(id))

if __name__ == '__main__':
    delete(sys.argv[1])