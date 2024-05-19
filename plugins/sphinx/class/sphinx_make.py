# coding:utf-8

import sys
import io
import os
import time
import subprocess
import re
import json


sys.path.append(os.getcwd() + "/class/core")
import mw


def getServerDir():
    return mw.getServerDir() + '/mysql'

def getPluginDir():
    return mw.getPluginDir() + '/mysql'

def getConf():
    path = getServerDir() + '/etc/my.cnf'
    return path

def getDbPort():
    file = getConf()
    content = mw.readFile(file)
    rep = 'port\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()

def getSocketFile():
    file = getConf()
    content = mw.readFile(file)
    rep = 'socket\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()

def pSqliteDb(dbname='databases'):
    file = getServerDir() + '/mysql.db'
    name = 'mysql'

    conn = mw.M(dbname).dbPos(getServerDir(), name)
    return conn

def pMysqlDb():
    # pymysql
    db = mw.getMyORM()

    db.setPort(getDbPort())
    db.setSocket(getSocketFile())
    # db.setCharset("utf8")
    db.setPwd(pSqliteDb('config').where('id=?', (1,)).getField('mysql_root'))
    return db

def getTablePk(pdb, db, table):
	# SHOW INDEX FROM bbs.bbs_ucenter_vars WHERE Key_name = 'PRIMARY'
	pkey_sql = "SHOW INDEX FROM {}.{} WHERE Key_name = 'PRIMARY';".format(db,table,);
	pkey_data = pdb.query(pkey_sql)

	# print(db, table)
	# print(pkey_data)

	if len(pkey_data) == 1:
		pkey_name = pkey_data[0]['Column_name']
		sql = "select COLUMN_NAME,DATA_TYPE from information_schema.COLUMNS where `TABLE_SCHEMA`='{}' and `TABLE_NAME` = '{}' and `COLUMN_NAME`='{}';"
		sql = sql.format(db,table,pkey_name,)
		# print(sql)
		fields = pdb.query(sql)

		if len(fields) == 1:
			# print(fields[0]['DATA_TYPE'])
			if mw.inArray(['bigint','smallint','tinyint','int','mediumint'], fields[0]['DATA_TYPE']):
				return pkey_name

	return ''

def getTableFieldStr(pdb, db, table):
	sql = "select COLUMN_NAME,DATA_TYPE from information_schema.COLUMNS where `TABLE_SCHEMA`='{}' and `TABLE_NAME` = '{}';"
	sql = sql.format(db,table,)
	fields = pdb.query(sql)

	field_str = ''
	for x in range(len(fields)):
		field_str += '`'+fields[x]['COLUMN_NAME']+'`,'

	field_str = field_str.strip(',')
	return field_str

def makeSphinxHeader():
	conf = '''
indexer
{
	mem_limit		= 128M
}

searchd
{
	listen			= 9312
	listen			= 9306:mysql41
	log				= {$server_dir}/sphinx/index/searchd.log
	query_log		= {$server_dir}/sphinx/index/query.log
	read_timeout	= 5
	max_children	= 0
	pid_file		= {$server_dir}/sphinx/index/searchd.pid
	seamless_rotate	= 1
	preopen_indexes	= 1
	unlink_old		= 1
	#workers		= threads # for RT to work
	binlog_path		= {$server_dir}/sphinx/index/binlog
}
	'''
	conf = conf.replace("{$server_dir}", mw.getServerDir())
	return conf

def makeSphinxDbSourceRangeSql(pdb, db, table, pkey_name):
	# pkey_name = getTablePk(pdb, db, table)
	sql = "SELECT min("+pkey_name+"), max("+pkey_name+") FROM "+table
	return sql

def makeSphinxDbSourceQuerySql(pdb, db, table,pkey_name):
	field_str = getTableFieldStr(pdb, db,table)
	# print(field_str)
	if pkey_name == 'id':
		sql = "SELECT " + field_str + " FROM " + table + " where id >= $start AND id <= $end"
	else:
		sql = "SELECT "+pkey_name+' as id,' + field_str + " FROM " + table + " where "+pkey_name+" >= $start AND "+pkey_name+" <= $end"
	return sql

def makeSphinxDbSource(pdb, db, table, pkey_name):

	db_info = pSqliteDb('databases').field('username,password').where('name=?', (db,)).find()
	port = getDbPort()


	conf = '''

source {$DB_NAME}_{$TABLE_NAME}
{
	type			= mysql
	sql_host		= 127.0.0.1
	sql_user		= {$DB_USER}
	sql_pass		= {$DB_PASS}
	sql_db			= {$DB_NAME}
	sql_port		= {$DB_PORT}

	sql_query_range 	= {$DB_RANGE_SQL}
	sql_range_step 		= 1000

	sql_query_pre   	= SET NAMES utf8
	sql_query 		= {$DB_QUERY_SQL}

{$SPH_FIELD}
}

index {$DB_NAME}_{$TABLE_NAME}
{
    source	= {$DB_NAME}_{$TABLE_NAME}
    path	= {$server_dir}/sphinx/index/db/{$DB_NAME}.{$TABLE_NAME}/index

    ngram_len	= 1
    ngram_chars	= U+3000..U+2FA1F
}
'''
	conf = conf.replace("{$server_dir}", mw.getServerDir())

	conf = conf.replace("{$DB_NAME}", db)
	conf = conf.replace("{$TABLE_NAME}", table)
	conf = conf.replace("{$DB_USER}", db_info['username'])
	conf = conf.replace("{$DB_PASS}", db_info['password'])
	conf = conf.replace("{$DB_PORT}", port)

	range_sql = makeSphinxDbSourceRangeSql(pdb, db, table,pkey_name)
	conf = conf.replace("{$DB_RANGE_SQL}", range_sql)

	query_sql = makeSphinxDbSourceQuerySql(pdb, db, table, pkey_name)
	conf = conf.replace("{$DB_QUERY_SQL}", query_sql)

	sph_field = makeSqlToSphinxTable(pdb, db, table, pkey_name)
	conf = conf.replace("{$SPH_FIELD}", sph_field)

	return conf


def makeSqlToSphinxAll():
    filter_db = ['information_schema','performance_schema','sys','mysql']

    pdb = pMysqlDb()
    dblist = pdb.query('show databases')

    conf = ''
    conf += makeSphinxHeader()

    conf += makeSqlToSphinxDb(pdb, 'bbs', ['bbs_ucenter_admins'])


    # for x in range(len(dblist)):
    #     dbname = dblist[x]['Database']
    #     if mw.inArray(filter_db, dbname):
    #         continue
    #     conf += makeSqlToSphinxDb(pdb, dbname)
    return conf



def makeSqlToSphinxDb(pdb, db, table = []):
	conf = ''

	for t in table:
		pkey_name = getTablePk(pdb, db, t)
		if pkey_name == '':
			continue
		conf += makeSphinxDbSource(pdb, db, t, pkey_name)

	if len(table) == 0:
		tables = pdb.query("show tables in "+ db)
		for x in range(len(tables)):
			key = 'Tables_in_'+db
			table_name = tables[x][key]
			pkey_name = getTablePk(pdb, db, table_name)

			if pkey_name == '':
				continue

			conf += makeSphinxDbSource(pdb, db, table_name, pkey_name)
	return conf

def makeSqlToSphinxTable(pdb,db,table,pkey_name):

	sql = "select COLUMN_NAME,DATA_TYPE from information_schema.COLUMNS where `TABLE_SCHEMA`='{}' and `TABLE_NAME` = '{}';"
	sql = sql.format(db,table,)
	cols = pdb.query(sql)
	cols_len = len(cols)
	conf = ''
	run_pos = 0
	for x in range(cols_len):
		data_type = cols[x]['DATA_TYPE']
		column_name = cols[x]['COLUMN_NAME']
		# print(column_name+":"+data_type)

		# if mw.inArray(['tinyint'], data_type):
		# 	conf += 'sql_attr_bool = '+ column_name + "\n"

		if pkey_name == column_name:
			run_pos += 1
			conf += '\tsql_attr_bigint = '+column_name+"\n"
			continue

		if mw.inArray(['enum'], data_type):
			run_pos += 1
			conf += '\tsql_attr_string = '+ column_name + "\n"
			continue

		if mw.inArray(['decimal'], data_type):
			run_pos += 1
			conf += '\tsql_attr_float = '+ column_name + "\n"

		if mw.inArray(['bigint','smallint','tinyint','int','mediumint'], data_type):
			run_pos += 1
			conf += '\tsql_attr_bigint = '+ column_name + "\n"
			continue


		if mw.inArray(['float'], data_type):
			run_pos += 1
			conf += '\tsql_attr_float = '+ column_name + "\n"
			continue

		if mw.inArray(['varchar','char'], data_type):
			run_pos += 1
			conf += '\tsql_attr_string = '+ column_name + "\n"
			continue

		if mw.inArray(['text','mediumtext','tinytext','longtext'], data_type):
			run_pos += 1
			conf += '\tsql_field_string = '+ column_name + "\n"
			continue

		if mw.inArray(['datetime','date'], data_type):
			run_pos += 1
			conf += '\tsql_attr_timestamp = '+ column_name + "\n"
			continue

	# if cols_len != run_pos:
	# 	print(db,table)
	# print(cols_len,run_pos)
	# print(conf)
	return conf

	








