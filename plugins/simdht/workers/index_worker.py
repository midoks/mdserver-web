#!/usr/bin/env python
#coding: utf8
"""
从MySQL数据库中读取未索引的资源，更新到Sphinx的实时索引中。
xiaoxia@xiaoxia.org
2015.5 created
"""

import time
import MySQLdb as mdb
import MySQLdb.cursors

SRC_HOST = '127.0.0.1'
SRC_USER = 'root'
SRC_PASS = ''
DST_HOST = '127.0.0.1'
DST_USER = 'root'
DST_PASS = ''

src_conn = mdb.connect(SRC_HOST, SRC_USER, SRC_PASS, 'ssbc', charset='utf8', cursorclass=MySQLdb.cursors.DictCursor)
src_curr = src_conn.cursor()
src_curr.execute('SET NAMES utf8')

dst_conn = mdb.connect(DST_HOST, DST_USER, DST_PASS, 'rt_main', port=9306, charset='utf8')
dst_curr = dst_conn.cursor()
dst_curr.execute('SET NAMES utf8')

def work():
    src_curr.execute('SELECT id, name, CRC32(category) AS category, length, UNIX_TIMESTAMP(create_time) AS create_time, ' +
        'UNIX_TIMESTAMP(last_seen) AS last_seen FROM search_hash WHERE tagged=false LIMIT 10000')
    total = src_curr.rowcount
    print 'fetched', total
    for one in src_curr:
        ret = dst_curr.execute('insert into rt_main(id,name,category,length,create_time,last_seen) values(%s,%s,%s,%s,%s,%s)',
            (one['id'], one['name'], one['category'], one['length'], one['create_time'], one['last_seen']))
        if ret:
            src_curr.execute('UPDATE search_hash SET tagged=True WHERE id=%s', (one['id'],))
            print 'Indexed', one['name'].encode('utf8')
    print 'Done!'
    return total

if __name__ == '__main__':
    while True:
        if work() == 10000:
            print 'Continue...'
            continue
        print 'Wait 10mins...'
        time.sleep(600)

