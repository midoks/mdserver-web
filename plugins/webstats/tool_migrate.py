# coding:utf-8

import sys
import io
import os
import time
import json
import fcntl
import shutil

web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw
from utils.crontab import crontab as MwCrontab

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'webstats'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


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

    return conn


def batch_delete(conn, table, where_clause, batch_size=5000, pause_sec=0.05):
    """分批删除，缩短单次持锁时间，WAL 模式下可与 OpenResty 并发写入。"""
    total = 0
    while True:
        sql = (
            f"DELETE FROM {table} WHERE rowid IN "
            f"(SELECT rowid FROM {table} WHERE {where_clause} LIMIT {batch_size})"
        )
        affected = conn.execute(sql)
        if not isinstance(affected, int) or affected == 0:
            break
        total += affected
        if pause_sec > 0:
            time.sleep(pause_sec)
    return total


def migrateSiteHotLogs(site_name, query_date):
    start_time = time.time()
    print(f"[{site_name}] 开始迁移日志...")

    migrating_flag = getServerDir() + "/logs/%s/migrating" % site_name
    hot_db = getServerDir() + "/logs/%s/logs.db" % site_name
    hot_db_tmp = getServerDir() + "/logs/%s/logs_tmp.db" % site_name
    history_logs_db = getServerDir() + "/logs/%s/history_logs.db" % site_name

    if not os.path.exists(hot_db):
        print(f"[{site_name}] 热日志数据库不存在，跳过")
        return mw.returnMsg(True, f"{site_name} logs not exist, skip")

    # 检查是否正在迁移
    if os.path.exists(migrating_flag):
        print(f"[{site_name}] 正在迁移中，跳过")
        return mw.returnMsg(True, f"{site_name} is migrating, skip")

    todayTime = time.strftime('%Y-%m-%d 00:00:00', time.localtime())
    todayUt = int(time.mktime(time.strptime(
        todayTime, "%Y-%m-%d %H:%M:%S")))

    # 1. 备份到临时文件（copy 期间短暂互斥，完成后立即解除）
    try:
        print(f"[{site_name}] 备份 {hot_db} -> {hot_db_tmp} ...")
        mw.writeFile(migrating_flag, "yes")
        time.sleep(0.5)
        copy_start = time.time()
        # import shutil
        # shutil.copy(hot_db, hot_db_tmp)
        mw.fastCopy(hot_db, hot_db_tmp, 256 * 1024)
        print(f"[{site_name}] 备份完成，耗时 {time.time() - copy_start:.2f}s")
        if not os.path.exists(hot_db_tmp):
            return mw.returnMsg(False, f"{site_name} migrating fail, copy tmp file!")
    except Exception as e:
        return mw.returnMsg(False, f"{site_name} migrating fail: {e}")
    finally:
        if os.path.exists(migrating_flag):
            os.remove(migrating_flag)

    # 2. 从临时备份中迁移热日志数据到历史日志（读 logs_tmp，不阻塞 live 写入）
    try:
        logs_conn = pSqliteDb('web_log', site_name, 'logs_tmp')
        history_logs_conn = pSqliteDb('web_log', site_name, 'history_logs')

        hot_db_columns = logs_conn.originExecute(
            "PRAGMA table_info([web_logs])")
        _columns = [c[1] for c in hot_db_columns if c[1] != "id"]
        columns_str = ",".join(_columns)
        placeholders = ",".join(["?"] * len(_columns))

        logs_sql = f"select {columns_str} from web_logs where time<{todayUt}"
        selector = logs_conn.originExecute(logs_sql)

        # 批量插入配置
        batch_size = 10000
        batch_count = 0
        total_count = 0
        insert_sql = f"insert into web_logs({columns_str}) values({placeholders})"

        while True:
            logs = selector.fetchmany(batch_size)
            if not logs:
                break

            batch_count += 1
            total_count += len(logs)
            # 使用原生 executemany 批量插入
            history_logs_conn.executemany(insert_sql, logs)
            history_logs_conn.commit()

            if batch_count % 10 == 0:
                elapsed = time.time() - start_time
                print(f"[{site_name}] 已迁移 {total_count} 条记录, 耗时 {elapsed:.2f}s")

        print(f"[{site_name}] 共迁移 {total_count} 条记录")

        # 清理历史数据
        gcfg = getGlobalConf()
        save_day = gcfg['global']["save_day"]
        print(f"[{site_name}] 删除 {save_day} 天前的历史数据...")

        time_now = time.localtime()
        save_timestamp = time.mktime((time_now.tm_year, time_now.tm_mon, time_now.tm_mday - save_day, 0, 0, 0, 0, 0, 0))
        delete_sql = f"delete from web_logs where time <= {save_timestamp}"
        history_logs_conn.execute(delete_sql)
        history_logs_conn.commit()

        history_logs_conn.execute("VACUUM;")
        history_logs_conn.commit()

    except Exception as e:
        if os.path.exists(hot_db_tmp):
            os.remove(hot_db_tmp)
        print(f"[{site_name}] logs to history error: {e}")
        return mw.returnMsg(False, f"{site_name} logs migrate error: {e}")

    # 3. 分批删除已迁移的热日志并清理统计（不设 migrating 锁，不阻塞 OpenResty 写入）
    try:
        hot_db_conn = pSqliteDb('web_logs', site_name)
        hot_db_conn.execute("PRAGMA busy_timeout = 30000")

        print(f"[{site_name}] 分批删除已迁移的热日志...")
        deleted = batch_delete(hot_db_conn, 'web_logs', f"time<{todayUt}")
        print(f"[{site_name}] 已删除 {deleted} 条热日志")

        print(f"[{site_name}] 分批删除180天前的统计数据...")
        save_time_key = time.strftime(
            '%Y%m%d00', time.localtime(time.time() - 180 * 86400))
        stat_where = f"time<='{save_time_key}'"
        for stat_table in ('request_stat', 'spider_stat', 'client_stat', 'referer_stat'):
            stat_deleted = batch_delete(hot_db_conn, stat_table, stat_where)
            print(f"[{site_name}] {stat_table} 已删除 {stat_deleted} 条")

        print(f"[{site_name}] 执行 WAL checkpoint...")
        hot_db_conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")

    except Exception as e:
        print(f"[{site_name}] delete hot logs error: {e}")
    finally:
        if os.path.exists(hot_db_tmp):
            os.remove(hot_db_tmp)
        if os.path.exists(hot_db_tmp+"-shm"):
            os.remove(hot_db_tmp+"-shm")
        if os.path.exists(hot_db_tmp+"-wal"):
            os.remove(hot_db_tmp+"-wal")

    elapsed = time.time() - start_time
    print(f"[{site_name}] 日志迁移完成，耗时 {elapsed:.2f}s")

    if not mw.isAppleSystem():
        mw.execShell("chown -R www:www " + getServerDir())

    return mw.returnMsg(True, f"{site_name} logs migrate ok")


def migrateHotLogs(query_date="today"):
    # 使用文件锁防止并发迁移
    lock_file = getServerDir() + "/logs/migrate_hot_logs.lock"
    lock_fd = None

    try:
        lock_fd = open(lock_file, 'w')
        fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

        print("开始迁移热日志...")
        sites = mw.M('sites').field('name').order("add_time").select()

        unset_site = {"name": "unset"}
        sites.append(unset_site)

        total_sites = len(sites)
        success_count = 0
        fail_count = 0

        for i, site_info in enumerate(sites):
            site_name = site_info["name"]
            print(f"\n[{i+1}/{total_sites}] 处理站点: {site_name}")
            migrate_res = migrateSiteHotLogs(site_name, query_date)
            if migrate_res["status"]:
                success_count += 1
            else:
                fail_count += 1
                print(f"[{site_name}] 迁移失败: {migrate_res['msg']}")

        print(f"\n迁移完成! 成功: {success_count}, 失败: {fail_count}")

        return mw.returnMsg(True, f"logs migrate ok, success: {success_count}, fail: {fail_count}")

    except BlockingIOError:
        print("正在迁移中，跳过")
        return mw.returnMsg(True, "正在迁移中，跳过")
    except Exception as e:
        print(f"migrateHotLogs error: {e}")
        return mw.returnMsg(False, f"migrateHotLogs error: {e}")
    finally:
        if lock_fd:
            try:
                fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
                lock_fd.close()
                if os.path.exists(lock_file):
                    os.remove(lock_file)
            except:
                pass