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
    return 'clean'


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
        "period": "day-n",
        "where1": "7",
        "hour": "0",
        "minute": "15",
    }


def createBgTask():
    removeBgTask()
    createBgTaskByName(getPluginName())


def createBgTaskByName(name):
    args = getConfigData()
    _name = "[勿删]日志清理[" + name + "]"
    res = mw.M("crontab").field("id, name").where("name=?", (_name,)).find()
    if res:
        return True

    if "task_id" in args and args["task_id"] > 0:
        res = mw.M("crontab").field("id, name").where(
            "id=?", (args["task_id"],)).find()
        if res and res["id"] == args["task_id"]:
            print("计划任务已经存在!")
            return True
    import crontab_api
    api = crontab_api.crontab_api()

    mw_dir = mw.getRunDir()
    cmd = '''
mw_dir=%s
rname=%s
plugin_path=%s
script_path=%s
logs_file=$plugin_path/${rname}.log
''' % (mw_dir, name, getServerDir(), getPluginDir())
    cmd += 'echo "★【`date +"%Y-%m-%d %H:%M:%S"`】 STSRT★" >> $logs_file' + "\n"
    cmd += 'echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" >> $logs_file' + "\n"
    cmd += 'echo "python3 $script_path/index.py clean >> $logs_file 2>&1"' + "\n"
    cmd += 'cd $mw_dir && python3 $script_path/index.py clean >> $logs_file 2>&1' + "\n"
    cmd += 'echo "【`date +"%Y-%m-%d %H:%M:%S"`】 END★" >> $logs_file' + "\n"
    cmd += 'echo "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<" >> $logs_file' + "\n"

    params = {
        'name': _name,
        'type': args['period'],
        'week': "",
        'where1': args['where1'],
        'hour': args['hour'],
        'minute': args['minute'],
        'save': "",
        'backup_to': "",
        'stype': "toShell",
        'sname': '',
        'sbody': cmd,
        'urladdress': '',
    }

    task_id = api.add(params)
    if task_id > 0:
        args["task_id"] = task_id
        args["name"] = name
        mw.writeFile(getTaskConf(), json.dumps(args))


def removeBgTask():
    cfg = getConfigData()
    if "task_id" in cfg and cfg["task_id"] > 0:
        res = mw.M("crontab").field("id, name").where(
            "id=?", (cfg["task_id"],)).find()
        if res and res["id"] == cfg["task_id"]:
            import crontab_api
            api = crontab_api.crontab_api()
            data = api.delete(cfg["task_id"])
            if data[0]:
                cfg["task_id"] = -1
                mw.writeFile(getTaskConf(), json.dumps(cfg))
                return True
    return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "remove":
            removeBgTask()
        elif action == "add":
            createBgTask()
