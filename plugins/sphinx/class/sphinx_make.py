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

class sphinxMake():

	pdb = None
	psdb = None

	pkey_name_cache = {}
	delta = 'sph_counter'
	ver = ''


	def __init__(self):
		self.pdb = pMysqlDb()

	def setDeltaName(self, name):
		self.delta = name
		return True

	def setVersion(self, ver):
		self.ver = ver

	def createSql(self, db):
		conf = '''
CREATE TABLE IF NOT EXISTS `{$DB_NAME}`.`{$TABLE_NAME}` (
	`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
	`table` varchar(200) NOT NULL,
	`max_id` bigint(20) unsigned  NOT NULL DEFAULT '0',
	PRIMARY KEY (`id`),
	UNIQUE KEY `table_uniq` (`table`),
	KEY `table` (`table`)
) ENGINE=InnoDB AUTO_INCREMENT=1 CHARSET=utf8mb4;
'''
		conf = conf.replace("{$TABLE_NAME}", self.delta)
		conf = conf.replace("{$DB_NAME}", db)
		return conf

	def eqVerField(self, field):
		ver = self.ver.replace(".1",'')
		if float(ver) >= 3.6:
			if field == 'sql_attr_timestamp':
				return 'attr_bigint'

			if field == 'sql_attr_bigint':
				return 'attr_bigint'

			if field == 'sql_attr_float':
				return 'attr_float'

			if field == 'sql_field_string':
				return 'field_string'

		if float(ver) >= 3.3:
			if field == 'sql_attr_timestamp':
				return 'sql_attr_bigint'

		return field

	def pathVerName(self):
		ver = self.ver.replace(".1",'')
		# if float(ver) >= 3.6:
		# 	return 'datadir'
		return 'path'

	def getTablePk(self, db, table):
		key = db+'_'+table
		if key in self.pkey_name_cache:
			return self.pkey_name_cache[key]

		# SHOW INDEX FROM bbs.bbs_ucenter_vars WHERE Key_name = 'PRIMARY'
		pkey_sql = "SHOW INDEX FROM {}.{} WHERE Key_name = 'PRIMARY';".format(db,table,);
		pkey_data = self.pdb.query(pkey_sql)

		# print(db, table)
		# print(pkey_data)
		key = ''
		if len(pkey_data) == 1:
			pkey_name = pkey_data[0]['Column_name']
			sql = "select COLUMN_NAME,DATA_TYPE from information_schema.COLUMNS where `TABLE_SCHEMA`='{}' and `TABLE_NAME` = '{}' and `COLUMN_NAME`='{}';"
			sql = sql.format(db,table,pkey_name,)
			# print(sql)
			fields = self.pdb.query(sql)

			if len(fields) == 1:
				# print(fields[0]['DATA_TYPE'])
				if mw.inArray(['bigint','smallint','tinyint','int','mediumint'], fields[0]['DATA_TYPE']):
					key = pkey_name
		return key


	def getTableFieldStr(self, db, table):
		sql = "select COLUMN_NAME,DATA_TYPE from information_schema.COLUMNS where `TABLE_SCHEMA`='{}' and `TABLE_NAME` = '{}';"
		sql = sql.format(db,table,)
		fields = self.pdb.query(sql)

		field_str = ''
		for x in range(len(fields)):
			field_str += '`'+fields[x]['COLUMN_NAME']+'`,'

		field_str = field_str.strip(',')
		return field_str

	def makeSphinxHeader(self):
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

	def makeSphinxDbSourceRangeSql(self, db, table):
		pkey_name = self.getTablePk(db,table)
		sql = "SELECT min("+pkey_name+"), max("+pkey_name+") FROM "+table
		return sql

	def makeSphinxDbSourceQuerySql(self, db, table):
		pkey_name = self.getTablePk(db,table)
		field_str = self.getTableFieldStr(db,table)
		# print(field_str)
		if pkey_name == 'id':
			sql = "SELECT " + field_str + " FROM " + table + " where id >= $start AND id <= $end"
		else:
			sql = "SELECT `"+pkey_name+'` as `id`,' + field_str + " FROM " + table + " where "+pkey_name+" >= $start AND "+pkey_name+" <= $end"
		return sql


	def makeSphinxDbSourceDeltaRange(self, db, table):
		pkey_name = self.getTablePk(db,table)
		conf = "SELECT (SELECT max_id FROM `{$SPH_TABLE}` where `table`='{$TABLE_NAME}') as min, (SELECT max({$PK_NAME}) FROM {$TABLE_NAME}) as max"
		conf = conf.replace("{$DB_NAME}", db)
		conf = conf.replace("{$TABLE_NAME}", table)
		conf = conf.replace("{$SPH_TABLE}", self.delta)
		conf = conf.replace("{$PK_NAME}", pkey_name)
		return conf

	def makeSphinxDbSourcePost(self, db, table):
		pkey_name = self.getTablePk(db,table)
		conf = "sql_query_post	=	UPDATE {$SPH_TABLE} SET max_id=(SELECT MAX({$PK_NAME}) FROM {$TABLE_NAME}) where `table`='{$TABLE_NAME}'"
		# conf = "REPLACE INTO {$SPH_TABLE} (`table`,`max_id`) VALUES ('{$TABLE_NAME}',(SELECT MAX({$PK_NAME}) FROM {$TABLE_NAME}))"
		conf = conf.replace("{$DB_NAME}", db)
		conf = conf.replace("{$TABLE_NAME}", table)
		conf = conf.replace("{$SPH_TABLE}", self.delta)
		conf = conf.replace("{$PK_NAME}", pkey_name)
		return conf

	def makeSphinxDbSourceDelta(self, db, table):
		conf = '''
source {$DB_NAME}_{$TABLE_NAME}_delta:{$DB_NAME}_{$TABLE_NAME}
{
    sql_query_pre	=	SET NAMES utf8
    sql_query_range	=	{$DELTA_RANGE}
    sql_query 		=	{$DELTA_QUERY}
    {$DELTA_UPDATE}

{$SPH_FIELD}
}

index {$DB_NAME}_{$TABLE_NAME}_delta:{$DB_NAME}_{$TABLE_NAME}
{
    source 	= {$DB_NAME}_{$TABLE_NAME}_delta
    {$PATH_NAME} 	= {$server_dir}/sphinx/index/db/{$DB_NAME}.{$TABLE_NAME}/delta

    html_strip	= 1
    ngram_len	= 1
    ngram_chars	= U+3000..U+2FA1F

{$SPH_FIELD_INDEX}
}
''';
		conf = conf.replace("{$server_dir}", mw.getServerDir())
		conf = conf.replace("{$PATH_NAME}", self.pathVerName())
		
		conf = conf.replace("{$DB_NAME}", db)
		conf = conf.replace("{$TABLE_NAME}", table)

		delta_range = self.makeSphinxDbSourceDeltaRange(db, table)
		conf = conf.replace("{$DELTA_RANGE}", delta_range)

		delta_query = self.makeSphinxDbSourceQuerySql(db, table)
		conf = conf.replace("{$DELTA_QUERY}", delta_query)

		delta_update = self.makeSphinxDbSourcePost(db, table)
		conf = conf.replace("{$DELTA_UPDATE}", delta_update)


		sph_field = self.makeSqlToSphinxTable(db, table)
		conf = self.makeSphinxDbFieldRepalce(conf, sph_field)
		
		return conf;

	def makeSphinxDbSource(self, db, table, create_sphinx_table = False):
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

	sql_query_pre   	= SET NAMES utf8

	{$UPDATE}

	sql_query_range 	= {$DB_RANGE_SQL}
	sql_range_step 		= 1000

	sql_query 		= {$DB_QUERY_SQL}

{$SPH_FIELD}
}

index {$DB_NAME}_{$TABLE_NAME}
{
    source	= {$DB_NAME}_{$TABLE_NAME}
    {$PATH_NAME}	= {$server_dir}/sphinx/index/db/{$DB_NAME}.{$TABLE_NAME}/index

    ngram_len	= 1
    ngram_chars	= U+3000..U+2FA1F

{$SPH_FIELD_INDEX}
}
	'''
		conf = conf.replace("{$server_dir}", mw.getServerDir())
		conf = conf.replace("{$PATH_NAME}", self.pathVerName())

		conf = conf.replace("{$DB_NAME}", db)
		conf = conf.replace("{$TABLE_NAME}", table)
		conf = conf.replace("{$DB_USER}", db_info['username'])
		conf = conf.replace("{$DB_PASS}", db_info['password'])
		conf = conf.replace("{$DB_PORT}", port)

		range_sql = self.makeSphinxDbSourceRangeSql(db, table)
		conf = conf.replace("{$DB_RANGE_SQL}", range_sql)

		query_sql = self.makeSphinxDbSourceQuerySql(db, table)
		conf = conf.replace("{$DB_QUERY_SQL}", query_sql)

		sph_field = self.makeSqlToSphinxTable(db, table)
		# conf = conf.replace("{$SPH_FIELD}", sph_field)


		conf = self.makeSphinxDbFieldRepalce(conf, sph_field)

		if create_sphinx_table:
			update = self.makeSphinxDbSourcePost(db, table)
			conf = conf.replace("{$UPDATE}", update)
		else:
			conf = conf.replace("{$UPDATE}", '')

		if create_sphinx_table:
			sph_sql = self.createSql(db)
			self.pdb.query(sph_sql)
			sql_find = "select * from {}.{} where `table`='{}'".format(db,self.delta,table)
			find_data = self.pdb.query(sql_find)
			if len(find_data) == 0:
				insert_sql = "insert into `{}`.`{}`(`table`,`max_id`) values ('{}',{}) ".format(db,self.delta,table,0)
				# print(insert_sql)
				self.pdb.execute(insert_sql)
			conf += self.makeSphinxDbSourceDelta(db,table)

		# print(ver)
		# print(conf)

		return conf

	def makeSphinxDbFieldRepalce(self, content, sph_field):
		ver = self.ver.replace(".1",'')
		ver = float(ver)
		if ver >= 3.6:
			content = content.replace("{$SPH_FIELD}", '')
			content = content.replace("{$SPH_FIELD_INDEX}", '')
		else:
			content = content.replace("{$SPH_FIELD}", sph_field)
			content = content.replace("{$SPH_FIELD_INDEX}", '')

		return content


	def makeSqlToSphinxDb(self, db, table = [], is_delta = False):
		conf = ''


		for tn in table:
			pkey_name = self.getTablePk(db,tn)
			if pkey_name == '':
				continue
			conf += self.makeSphinxDbSource(db, tn,is_delta)

		if len(table) == 0:
			tables = self.pdb.query("show tables in "+ db)
			for x in range(len(tables)):
				key = 'Tables_in_'+db
				table_name = tables[x][key]
				pkey_name = self.getTablePk(db, table_name, is_delta)
				if pkey_name == '':
					continue

				if self.makeSqlToSphinxTableIsHaveFulltext(db, table_name):
					conf += self.makeSphinxDbSource(db, table_name)
		return conf

	def makeSqlToSphinxTableIsHaveFulltext(self, db, table):
		sql = "select COLUMN_NAME,DATA_TYPE from information_schema.COLUMNS where `TABLE_SCHEMA`='{}' and `TABLE_NAME` = '{}';"
		sql = sql.format(db,table,)
		cols = self.pdb.query(sql)
		cols_len = len(cols)

		for x in range(cols_len):
			data_type = cols[x]['DATA_TYPE']
			column_name = cols[x]['COLUMN_NAME']

			if mw.inArray(['varchar'], data_type):
				return True
			if mw.inArray(['text','mediumtext','tinytext','longtext'], data_type):
				return True
		return False

	def makeSqlToSphinxTable(self,db,table):
		pkey_name = self.getTablePk(db,table)
		sql = "select COLUMN_NAME,DATA_TYPE from information_schema.COLUMNS where `TABLE_SCHEMA`='{}' and `TABLE_NAME` = '{}';"
		sql = sql.format(db,table,)
		cols = self.pdb.query(sql)
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
				# run_pos += 1
				# conf += '\tsql_attr_bigint = '+column_name+"\n"
				continue

			if mw.inArray(['enum'], data_type):
				run_pos += 1
				conf += '\t'+self.eqVerField('sql_attr_string')+' = '+ column_name + "\n"
				continue

			if mw.inArray(['decimal'], data_type):
				run_pos += 1
				conf += '\t'+self.eqVerField('sql_attr_float')+' = '+ column_name + "\n"
				continue

			if mw.inArray(['bigint','smallint','tinyint','int','mediumint'], data_type):
				run_pos += 1
				conf += '\t'+self.eqVerField('sql_attr_bigint')+' = '+ column_name + "\n"
				continue


			if mw.inArray(['float'], data_type):
				run_pos += 1
				conf += '\t'+self.eqVerField('sql_attr_float')+' = '+ column_name + "\n"
				continue

			if mw.inArray(['char'], data_type):
				conf += '\t'+self.eqVerField('sql_attr_string')+' = '+ column_name + "\n"
				continue

			if mw.inArray(['varchar'], data_type):
				run_pos += 1
				conf += '\t'+self.eqVerField('sql_field_string')+' = '+ column_name + "\n"
				continue

			if mw.inArray(['text','mediumtext','tinytext','longtext'], data_type):
				run_pos += 1
				conf += '\t'+self.eqVerField('sql_field_string')+' = '+ column_name + "\n"
				continue

			if mw.inArray(['datetime','date'], data_type):
				run_pos += 1
				conf += '\t'+self.eqVerField('sql_attr_timestamp')+' = '+ column_name + "\n"
				continue

		return conf

	def checkDbName(self, db):
	    filter_db = ['information_schema','performance_schema','sys','mysql']
	    if db in filter_db:
	        return False
	    return True

	def makeSqlToSphinx(self, db, tables = [], is_delta = False):
	    conf = ''
	    conf += self.makeSphinxHeader()
	    conf += self.makeSqlToSphinxDb(db, tables, is_delta)
	    return conf

	def makeSqlToSphinxAll(self):
	    filter_db = ['information_schema','performance_schema','sys','mysql']

	    dblist = self.pdb.query('show databases')

	    conf = ''
	    conf += self.makeSphinxHeader()

	    # conf += makeSqlToSphinxDb(pdb, 'bbs')
	    for x in range(len(dblist)):
	        dbname = dblist[x]['Database']
	        if mw.inArray(filter_db, dbname):
	            continue
	        conf += self.makeSqlToSphinxDb(dbname)
	    return conf


