
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