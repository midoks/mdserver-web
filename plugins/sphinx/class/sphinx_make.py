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

def makeSqlToSphinx():
	pass

def makeSqlToSphinxDb(db, table = []):
	pdb = pMysqlDb()

	tables = pdb.query("show tables in "+ db)
	for x in range(len(tables)):
		key = 'Tables_in_'+db
		table_name = tables[x][key]
		pkey_name = getTablePk(db,table_name)

		if pkey_name == '':
			continue

		# print(table_name+':'+pkey_name)
		makeSqlToSphinxTable(db,table_name)


def getTablePk(db, table):
	pdb = pMysqlDb()
	pkey_sql = "SHOW INDEX FROM {}.{} WHERE Key_name = 'PRIMARY';".format(db,table,);
	pkey_data = pdb.query(pkey_sql)

	if len(pkey_data) == 1:
		return pkey_data[0]['Column_name']

	return ''

def makeSqlToSphinxTable(db,table):
	pdb = pMysqlDb()

	sql = "select COLUMN_NAME,DATA_TYPE from information_schema.COLUMNS where `TABLE_SCHEMA`='{}' and `TABLE_NAME` = '{}';"
	sql = sql.format(db,table,)
	cols = pdb.query(sql)
	cols_len = len(cols)
	conf = ''
	run_pos = 0
	for x in range(cols_len):
		data_type = cols[x]['DATA_TYPE']
		column_name = cols[x]['COLUMN_NAME']
		print(column_name+":"+data_type)

		# if mw.inArray(['tinyint'], data_type):
		# 	conf += 'sql_attr_bool = '+ column_name + "\n"

		if mw.inArray(['enum'], data_type):
			run_pos += 1
			conf += 'sql_attr_string = '+ column_name + "\n"

		if mw.inArray(['decimal'], data_type):
			run_pos += 1
			conf += 'sql_attr_float = '+ column_name + "\n"

		if mw.inArray(['bigint','smallint','tinyint','int','mediumint'], data_type):
			run_pos += 1
			conf += 'sql_attr_bigint = '+ column_name + "\n"


		if mw.inArray(['float'], data_type):
			run_pos += 1
			conf += 'sql_attr_float = '+ column_name + "\n"

		if mw.inArray(['varchar','char'], data_type):
			run_pos += 1
			conf += 'sql_attr_string = '+ column_name + "\n"

		if mw.inArray(['text','mediumtext','tinytext','longtext'], data_type):
			run_pos += 1
			conf += 'sql_field_string = '+ column_name + "\n"

		if mw.inArray(['datetime','date'], data_type):
			run_pos += 1
			conf += 'sql_attr_timestamp = '+ column_name + "\n"

	if cols_len != run_pos:
		print(db,table)

	print(cols_len,run_pos)


	# print(conf)
	return conf

	








