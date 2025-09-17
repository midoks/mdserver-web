# coding:utf-8

import sys
import io
import os
import time
import json

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
    return 'mongodb'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getTaskConf():
    conf = getServerDir() + "/task_config.json"
    return conf


def getConfigData():
    conf = getTaskConf()
    if os.path.exists(conf):
        return json.loads(mw.readFile(getTaskConf()))
    return {
        "task_id": -1,
        "period": "minute-n",
        "where1": "1",
        "hour": "0",
        "minute": "0",
    }


def createBgTask():
    removeBgTask()
    createBgTaskByName(getPluginName())


def createBgTaskByName(name):
    args = getConfigData()
    _name = "[MongoDB]检查任务"
    res = mw.M("crontab").field("id, name").where("name=?", (_name,)).find()
    if res:
        return True

    if "task_id" in args and args["task_id"] > 0:
        res = mw.M("crontab").field("id, name").where(
            "id=?", (args["task_id"],)).find()
        if res and res["id"] == args["task_id"]:
            print("计划任务已经存在!")
            return True

    mw_dir = mw.getPanelDir()
    cmd = '''
mw_dir=%s
rname=%s
plugin_path=%s
script_path=%s
''' % (mw_dir, name, getServerDir(), getPluginDir())
    cmd += 'echo "bash $script_path/check.sh"' + "\n"
    cmd += 'cd $mw_dir && bash $script_path/check.sh' + "\n"

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
        'url_address': '',
    }

    task_id = MwCrontab.instance().add(params)
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
            data = MwCrontab.instance().delete(cfg["task_id"])
            if data["status"]:
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
