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
    return 'op_waf'


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
    return []


def getConfigTpl():
    tpl = {
        "name": "",
        "task_id": -1,
    }
    return tpl


def createBgTask():
    removeBgTask()
    args = {
        "period": "minute-n",
        "minute-n": "1",
    }

    if mw.isAppleSystem():
        createBgTaskByName(getPluginName(), args)


def createBgTaskByName(name, args):
    cfg = getConfigTpl()
    _name = "[勿删]OP防火墙后台任务[" + name + "]"
    res = mw.M("crontab").field("id, name").where("name=?", (_name,)).find()
    if res:
        return True

    if "task_id" in cfg.keys() and cfg["task_id"] > 0:
        res = mw.M("crontab").field("id, name").where(
            "id=?", (cfg["task_id"],)).find()
        if res and res["id"] == cfg["task_id"]:
            print("计划任务已经存在!")
            return True
    import crontab_api
    cron_api = crontab_api.crontab_api()

    period = args['period']
    _hour = ''
    _minute = ''
    _where1 = ''
    _type_day = "day"
    if period == 'day':
        _type_day = 'day'
        _hour = args['hour']
        _minute = args['minute']
    elif period == 'minute-n':
        _type_day = 'minute-n'
        _where1 = args['minute-n']
        _minute = ''

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

    if mw.isAppleSystem():
        cmd += 'echo "cd $mw_dir && source bin/activate && python3 $script_path/tool_task.py run >> $logs_file 2>&1"' + "\n"
        cmd += 'cd $mw_dir && source bin/activate && python3 $script_path/tool_task.py run >> $logs_file 2>&1' + "\n"
    else:
        cmd += 'echo "cd $mw_dir && source bin/activate && bash $script_path/shell/cpu_usage_file.sh >> $logs_file 2>&1"' + "\n"
        cmd += 'cd $mw_dir && source bin/activate && bash $script_path/shell/cpu_usage.sh >> $logs_file 2>&1' + "\n"

    cmd += 'echo "【`date +"%Y-%m-%d %H:%M:%S"`】 END★" >> $logs_file' + "\n"
    cmd += 'echo "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<" >> $logs_file' + "\n"

    params = {
        'name': _name,
        'type': _type_day,
        'week': "",
        'where1': _where1,
        'hour': _hour,
        'minute': _minute,
        'save': "",
        'backup_to': "",
        'stype': "toShell",
        'sname': '',
        'sbody': cmd,
        'urladdress': '',
    }

    task_id = cron_api.add(params)
    if task_id > 0:
        cfg["task_id"] = task_id
        cfg["name"] = name

        _dd = getConfigData()
        _dd.append(cfg)
        mw.writeFile(getTaskConf(), json.dumps(_dd))


def removeBgTask():
    if not mw.isAppleSystem():
        return False

    cfg_list = getConfigData()
    for x in range(len(cfg_list)):
        cfg = cfg_list[x]
        if "task_id" in cfg.keys() and cfg["task_id"] > 0:
            res = mw.M("crontab").field("id, name").where(
                "id=?", (cfg["task_id"],)).find()
            if res and res["id"] == cfg["task_id"]:
                import crontab_api
                api = crontab_api.crontab_api()
                data = api.delete(cfg["task_id"])
                if data[0]:
                    cfg["task_id"] = -1
                    cfg_list[x] = cfg
                    mw.writeFile(getTaskConf(), '[]')
                    return True
    return False


def getCpuUsed():
    path = getServerDir() + "/cpu.info"
    if mw.isAppleSystem():
        import psutil
        used = psutil.cpu_percent(interval=1)
        mw.writeFile(path, str(int(used)))
    else:
        cmd = "top -bn 1 | fgrep 'Cpu(s)' | awk '{print 100 -$8}' | awk -F . '{print $1}'"
        data = mw.execShell(cmd)
        mw.writeFile(path, str(int(data[0].strip())))


def run():
    getCpuUsed()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "remove":
            removeBgTask()
        elif action == "add":
            createBgTask()
        elif action == "run":
            run()
