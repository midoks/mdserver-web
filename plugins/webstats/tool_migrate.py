# coding:utf-8

import sys
import io
import os
import time
import json

sys.path.append(os.getcwd() + "/class/core")
import mw


app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'webstats'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getTaskConf():
    conf = getServerDir() + "/task_config.json"
    return conf


def getConf():
    conf = getServerDir() + "/lua/config.json"
    return conf


def getGlobalConf():
    conf = getConf()
    content = mw.readFile(conf)
    result = json.loads(content)
    return result


def pSqliteDb(dbname='web_logs', site_name='unset', fn="logs"):

    db_dir = getServerDir() + '/logs/' + site_name
    if not os.path.exists(db_dir):
        mw.execShell('mkdir -p ' + db_dir)

    name = fn
    file = db_dir + '/' + name + '.db'

    if not os.path.exists(file):
        conn = mw.M(dbname).dbPos(db_dir, name)
        sql = mw.readFile(getPluginDir() + '/conf/init.sql')
        sql_list = sql.split(';')
        for index in range(len(sql_list)):
            conn.execute(sql_list[index], ())
    else:
        conn = mw.M(dbname).dbPos(db_dir, name)

    conn.execute("PRAGMA synchronous = 0", ())
    conn.execute("PRAGMA page_size = 4096", ())
    conn.execute("PRAGMA journal_mode = wal", ())

    conn.autoTextFactory()

    # conn.text_factory = lambda x: str(x, encoding="utf-8", errors='ignore')
    # conn.text_factory = lambda x: unicode(x, "utf-8", "ignore")
    return conn


def migrateSiteHotLogs(site_name, query_date):
    print(site_name, query_date)

    migrating_flag = getServerDir() + "/logs/%s/migrating" % site_name
    hot_db = getServerDir() + "/logs/%s/logs.db" % site_name
    hot_db_tmp = getServerDir() + "/logs/%s/logs_tmp.db" % site_name
    history_logs_db = getServerDir() + "/logs/%s/history_logs.db" % site_name
    # 1. copy to tmp file
    try:
        import shutil
        print("coping {} to {} ...".format(hot_db, hot_db_tmp))
        mw.writeFile(migrating_flag, "yes")
        time.sleep(3)
        shutil.copy(hot_db, hot_db_tmp)
        if not os.path.exists(hot_db_tmp):
            return mw.returnMsg(False, "migrating fail, copy tmp file!")
    except:
        return mw.returnMsg(False, "{} migrating fail.".format(site_name))
    finally:
        if os.path.exists(migrating_flag):
            os.remove(migrating_flag)

     # 2. 从临时备份中迁移热日志数据到历史日志
    print("begin tmp to hot log data ...")
    try:
        print("history file: {}".format(history_logs_db))
        logs_conn = pSqliteDb('web_log', site_name, 'logs_tmp')
        history_logs_conn = pSqliteDb('web_log', site_name, 'history_logs')

        hot_db_columns = logs_conn.originExecute(
            "PRAGMA table_info([web_logs])")
        _columns = ",".join([c[1] for c in hot_db_columns if c[1] != "id"])
        query_start = 0
        todayTime = time.strftime('%Y-%m-%d 00:00:00', time.localtime())
        todayUt = int(time.mktime(time.strptime(
            todayTime, "%Y-%m-%d %H:%M:%S")))

        logs_sql = "select {} from web_logs where time<{}".format(
            _columns, todayUt)
        selector = logs_conn.originExecute(logs_sql)
        log = selector.fetchone()
        while log:
            params = ""
            for field in log:
                if params:
                    params += ","
                if field is None:
                    field = "\'\'"
                elif type(field) == str:
                    field = "\'" + field.replace("\'", "\”") + "\'"
                params += str(field)
            insert_sql = "insert into web_logs(" + \
                _columns + ") values(" + params + ")"
            history_logs_conn.execute(insert_sql)
            log = selector.fetchone()

        print("sorting historical data, this action takes a long time...")
        history_logs_conn.execute("VACUUM;")

        gcfg = getGlobalConf()
        save_day = gcfg['global']["save_day"]
        print("delete historical data {} days ago...".format(save_day))
        time_now = time.localtime()
        save_timestamp = time.mktime((time_now.tm_year, time_now.tm_mon, time_now.tm_mday - save_day, 0, 0, 0, 0, 0, 0))
        delete_sql = "delete from web_logs where time <= {}".format(
            save_timestamp)
        print('delete history_logs')
        print(delete_sql)
        history_logs_conn.execute(delete_sql)
        history_logs_conn.commit()

        # 3. delete merged data and clean up statistics
        print("delete merged thermal data...")
        mw.writeFile(migrating_flag, "yes")

        hot_db_conn = pSqliteDb('web_logs', site_name)
        del_hot_log = "delete from web_logs where time<{}".format(todayUt)
        print(del_hot_log)
        r = hot_db_conn.execute(del_hot_log)
        print("delete:", r)
        print("deleting statistics over 180 days...")
        save_time_key = time.strftime(
            '%Y%m%d00', time.localtime(time.time() - 180 * 86400))

        del_request_stat_sql = "delete from request_stat where time<={}".format(
            save_time_key)
        hot_db_conn.execute(del_request_stat_sql)

        hot_db_conn.execute(
            "delete from spider_stat where time<={}".format(save_time_key))
        hot_db_conn.execute(
            "delete from client_stat where time<={}".format(save_time_key))
        hot_db_conn.execute(
            "delete from referer_stat where time<={}".format(save_time_key))
        hot_db_conn.commit()
        print("clean up the hot database...")
        hot_db_conn.execute("VACUUM;")
        hot_db_conn.commit()

        if os.path.exists(migrating_flag):
            os.remove(migrating_flag)
    except Exception as e:
        if site_name:
            print("{} logs to history error:{}".format(site_name, e))
        else:
            print("logs to history error:{}".format(e))
    finally:
        if os.path.exists(hot_db_tmp):
            os.remove(hot_db_tmp)

    print("{} logs migrate ok.".format(site_name))

    if not mw.isAppleSystem():
        mw.execShell("chown -R www:www " + getServerDir())

    mw.opWeb('restart')
    return mw.returnMsg(True, "{} logs migrate ok".format(site_name))


def migrateHotLogs(query_date="today"):
    print("begin migrate hot logs")
    sites = mw.M('sites').field('name').order("addtime").select()

    unset_site = {"name": "unset"}
    sites.append(unset_site)

    # migrateSiteHotLogs('t1.cn', query_date)

    for site_info in sites:
        # print(site_info['name'])
        site_name = site_info["name"]
        migrate_res = migrateSiteHotLogs(site_name, query_date)
        if not migrate_res["status"]:
            print(migrate_res["msg"])
    print("end migrate hot logs")
