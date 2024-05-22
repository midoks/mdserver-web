
```
show global  variables like '%gtid%';
show global  variables like 'server_uuid';
```

```
# 不锁表，需要删除原来数据表
# tables = db.query('show tables from `%s`' % sync_db_import)
# table_key = "Tables_in_" + sync_db_import
# for tname in tables:
#     drop_db_cmd = 'drop table if exists '+sync_db_import+'.'+tname[table_key]
#     # print(drop_db_cmd)
#     db.query(drop_db_cmd)
```

```
# 修改同步位置
# master_info = sync_mdb.query('show master status')
# slave_info = db.query('show slave status')
# if len(master_info)>0:
#     channel_name = slave_info[0]['Channel_Name']
#     change_cmd = "CHANGE MASTER TO  MASTER_LOG_FILE='"+master_info[0]['File']+"', MASTER_LOG_POS="+str(master_info[0]['Position'])+" for channel '"+channel_name+"';"
#     print(change_cmd)
#     r = db.execute(change_cmd)
#     print(r)
```