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


def getConfigData():
    try:
        return json.loads(mw.readFile(getTaskConf()))
    except:
        pass
    return {
        "task_id": -1,
        "task_list": ["migrate_hot_logs"],
        "default_execute_hour": 3,
        "default_execute_minute": 15,
    }


def createBgTask():
    cfg = getConfigData()
    name = "[勿删]网站统计插件定时任务"
    res = mw.M("crontab").field("id, name").where("name=?", (name,)).find()
    if res:
        return True

    if "task_id" in cfg.keys() and cfg["task_id"] > 0:
        res = mw.M("crontab").field("id, name").where(
            "id=?", (cfg["task_id"],)).find()
        if res and res["id"] == cfg["task_id"]:
            print("计划任务已经存在!")
            return True
    import crontab_api
    api = crontab_api.crontab_api()

    cmd = "cd " + mw.getRunDir() + " && nice -n 10 python3 " + \
        getPluginDir() + "/tool_task.py execute"
    params = {
        'name': name,
        'type': 'day',
        'week': "",
        'where1': "",
        'hour': cfg['default_execute_hour'],
        'minute': cfg['default_execute_minute'],
        'save': "",
        'backup_to': "",
        'stype': "toShell",
        'sname': '',
        'sbody': cmd,
        'urladdress': '',
    }

    task_id = api.add(params)
    if task_id > 0:
        cfg["task_id"] = task_id
        mw.writeFile(getTaskConf(), json.dumps(cfg))


def removeBgTask():
    cfg = getConfigData()
    if "task_id" in cfg.keys() and cfg["task_id"] > 0:
        res = mw.M("crontab").field("id, name").where(
            "id=?", (cfg["task_id"],)).find()
        if res and res["id"] == cfg["task_id"]:
            import crontab_api
            api = crontab_api.crontab_api()

            data = api.delete(cfg["task_id"])
            if data[0]:
                print(data[1])
                cfg["task_id"] = -1
                mw.writeFile(getTaskConf(), json.dumps(cfg))
                return True
    return False


def execute():
    try:
        import time
        now = time.strftime("%Y-%m-%d", time.localtime())
        print("-" * 30)
        cfg = getConfigData()
        task_list = cfg["task_list"]
        for task in task_list:
            # print(task)
            if task == "migrate_hot_logs":
                try:
                    import tool_migrate
                    tool_migrate.migrateHotLogs("yesterday")
                except Exception as e:
                    print(e)
        print(now)
        print("-" * 30)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "execute":
            execute()
        elif action == "remove":
            removeBgTask()
        elif action == "add":
            createBgTask()
