# coding:utf-8

import sys
import io
import os
import time
import re

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'supervisor'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getConf():
    path = getServerDir() + "/supervisor.conf"
    return path


def getConfTpl():
    path = getPluginDir() + "/conf/supervisor.conf"
    return path


def getSubConfDir():
    return getServerDir() + "/conf.d"


def getInitDTpl():
    path = getPluginDir() + "/init.d/" + getPluginName() + ".tpl"
    return path


def getArgs():
    args = sys.argv[2:]
    tmp = {}
    args_len = len(args)

    if args_len == 1:
        t = args[0].strip('{').strip('}')
        t = t.split(':')
        tmp[t[0]] = t[1]
    elif args_len > 1:
        for i in range(len(args)):
            t = args[i].split(':')
            tmp[t[0]] = t[1]

    return tmp


def checkArgs(data, ck=[]):
    for i in range(len(ck)):
        if not ck[i] in data:
            return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, mw.returnJson(True, 'ok'))


def status():

    data = mw.execShell(
        "ps -ef|grep supervisor | grep -v grep | grep -v index.py | awk '{print $2}'")
    if data[0] == '':
        return 'stop'
    return 'start'


def initDreplace():

    # initD_path = getServerDir() + '/init.d'
    # if not os.path.exists(initD_path):
    #     os.mkdir(initD_path)
    # file_bin = initD_path + '/' + getPluginName()

    # file_tpl = getInitDTpl()
    # initd replace
    # content = mw.readFile(file_tpl)
    # content = content.replace('{$SERVER_PATH}', service_path)
    # mw.writeFile(file_bin, content)
    # mw.execShell('chmod +x ' + file_bin)

    if not os.path.exists(getServerDir() + "/conf.d"):
        os.mkdir(getServerDir() + "/conf.d")

    if not os.path.exists(getServerDir() + '/supervisor.conf'):
        # config replace
        service_path = os.path.dirname(os.getcwd())
        conf_content = mw.readFile(getConfTpl())
        conf_content = conf_content.replace('{$SERVER_PATH}', service_path)
        mw.writeFile(getServerDir() + '/supervisor.conf', conf_content)

    return True


def start():
    initDreplace()
    cmd = 'supervisord -c ' + getServerDir() + '/supervisor.conf'
    # print(cmd)
    data = mw.execShell(cmd)
    # print(data)
    if data[1] == '':
        return 'ok'
    return 'fail'

#| awk '{print $2}'|xargs kill


def stop():
    initDreplace()
    data = mw.execShell('supervisorctl shutdown')
    mw.execShell(
        "ps -ef|grep supervisor | grep -v grep | grep -v index.py | awk '{print $2}'|xargs kill")
    if data[1] == '':
        return 'ok'
    return 'fail'


def restart():

    mw.execShell(
        "ps -ef|grep supervisor | grep -v grep | grep -v index.py | awk '{print $2}'|xargs kill")

    return start()
    initDreplace()
    data = mw.execShell('supervisorctl reload')
    if data[1] == '':
        return 'ok'
    return 'fail'


def reload():
    initDreplace()
    data = mw.execShell('supervisorctl reload')
    if data[1] == '':
        return 'ok'
    return 'fail'


def runInfo():
    cmd = getServerDir() + "/bin/redis-cli info"
    data = mw.execShell(cmd)[0]
    res = [
        'tcp_port',
        'uptime_in_days',  # 已运行天数
        'connected_clients',  # 连接的客户端数量
        'used_memory',  # Redis已分配的内存总量
        'used_memory_rss',  # Redis占用的系统内存总量
        'used_memory_peak',  # Redis所用内存的高峰值
        'mem_fragmentation_ratio',  # 内存碎片比率
        'total_connections_received',  # 运行以来连接过的客户端的总数量
        'total_commands_processed',  # 运行以来执行过的命令的总数量
        'instantaneous_ops_per_sec',  # 服务器每秒钟执行的命令数量
        'keyspace_hits',  # 查找数据库键成功的次数
        'keyspace_misses',  # 查找数据库键失败的次数
        'latest_fork_usec'  # 最近一次 fork() 操作耗费的毫秒数
    ]
    data = data.split("\n")
    result = {}
    for d in data:
        if len(d) < 3:
            continue
        t = d.strip().split(':')
        if not t[0] in res:
            continue
        result[t[0]] = t[1]
    return mw.getJson(result)


def initdStatus():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"
    initd_bin = getInitDFile()
    if os.path.exists(initd_bin):
        return 'ok'
    return 'fail'


def initdInstall():
    import shutil
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    source_bin = initDreplace()
    initd_bin = getInitDFile()
    shutil.copyfile(source_bin, initd_bin)
    mw.execShell('chmod +x ' + initd_bin)
    mw.execShell('chkconfig --add ' + getPluginName())
    return 'ok'


def initdUinstall():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    mw.execShell('chkconfig --del ' + getPluginName())
    initd_bin = getInitDFile()
    os.remove(initd_bin)
    return 'ok'


def getSupList():
    data = {}

    statusFile = getServerDir() + "/status.txt"
    supCtl = 'supervisorctl -c ' + getServerDir() + "/supervisor.conf"
    cmd = "%s update; %s status > %s" % (supCtl, supCtl, statusFile)
    mw.execShell(cmd)

    with open(statusFile, "r") as fr:
        lines = fr.readlines()

    array_list = []
    process_list = []
    for r in lines:
        array = r.split()
        if array:
            d = dict()
            program = array[0].split(':')[0]
            if program in process_list:
                continue
            process_list.append(program)
            d["program"] = program
            d["runStatus"] = array[1]
            if array[1] == "RUNNING":
                d["status"] = "1"
                d["pid"] = array[3][:-1]
            else:
                d["status"] = "0"
                d["pid"] = ""
            file = getServerDir() + '/conf.d/' + program + ".ini"
            if not os.path.exists(file):
                continue
            with open(file, "r") as fr:
                infos = fr.readlines()
            for line in infos:
                if "command=" in line.strip():
                    d["command"] = line.strip().split('=')[1]
                if "user=" in line.strip():
                    d["user"] = line.strip().split('=')[1]
                if "priority=" in line.strip():
                    d["priority"] = line.strip().split('=')[1]
                if "numprocs=" in line.strip():
                    d["numprocs"] = line.strip().split('=')[1]
            array_list.append(d)

    # print(array_list)
    data = {}
    data['data'] = array_list
    return mw.getJson(data)


def getUserListData():
    user = getServerDir() + "/user.txt"
    if not os.path.isfile(user):
        os.system(r"touch {}".format(user))
    res = mw.execShell("cat /etc/passwd > " + user)
    with open(user, "r") as fr:
        users = fr.readlines()
    fr.close()
    os.remove(user)

    user_list = []
    special = ["bin", "daemon", "adm", "lp", "shutdown", "halt", "mail", "operator", "games",
               "avahi-autoipd", "systemd-bus-proxy", "systemd-network", "dbus", "polkitd", "tss", "ntp"]
    for u in users:
        user = re.split(':', u)[0]
        if user[0] == '#':
            continue
        if user in special:
            continue
        user_list.append(user)
    return user_list


def getUserList():
    user_list = getUserListData()
    return mw.getJson(user_list)


def addJob():
    args = getArgs()
    data = checkArgs(args, ['name', 'user', 'path', 'command', 'numprocs'])
    if not data[0]:
        return data[1]

    program = args['name']
    command = args['command']
    path = args['path']
    numprocs = args['numprocs']
    user = args['user']

    log_dir = getServerDir() + '/log/'

    w_body = ""
    w_body += "[program:" + program + "]" + "\n"
    w_body += "command=" + command + "\n"
    w_body += "directory=" + path + "\n"
    w_body += "autorestart=true" + "\n"
    w_body += "startsecs=3" + "\n"
    w_body += "startretries=3" + "\n"
    w_body += "stdout_logfile=" + log_dir + program + ".out.log" + "\n"
    w_body += "stderr_logfile=" + log_dir + program + ".err.log" + "\n"
    w_body += "stdout_logfile_maxbytes=2MB" + "\n"
    w_body += "stderr_logfile_maxbytes=2MB" + "\n"
    w_body += "user=" + user + "\n"
    w_body += "priority=999" + "\n"
    w_body += "numprocs={0}".format(numprocs) + "\n"
    w_body += "process_name=%(program_name)s_%(process_num)02d"

    dstFile = getSubConfDir() + "/" + program + '.ini'

    mw.writeFile(dstFile, w_body)

    return mw.returnJson(True, '增加守护进程成功!')


def delJob():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]
    name = args['name']

    supCtl = 'supervisorctl'
    log_dir = getServerDir() + '/log/'

    result = mw.execShell("{0} stop ".format(supCtl) + name)
    program = getServerDir() + "/conf.d/" + name + ".ini"

    # 删除日志文件
    outlog = log_dir + name + ".out.log"
    if os.path.isfile(outlog):
        os.remove(outlog)
    errlog = log_dir + name + ".err.log"
    if os.path.isfile(errlog):
        os.remove(errlog)

    # 删除ini文件
    if os.path.isfile(program):
        os.remove(program)
        result = mw.execShell(
            "{0} update".format(supCtl))
        return mw.returnJson(True, '删除守护进程成功!')
    else:
        result = mw.execShell(
            "{0} update".format(supCtl))
        return mw.returnJson(False, '该守护进程不存在!')


def updateJob():
    args = getArgs()
    data = checkArgs(args, ["name", 'user', 'numprocs', 'priority'])
    if not data[0]:
        return data[1]
    user = args['user']
    numprocs = args['numprocs']
    priority = args['priority']
    name = args['name']
    programFile = getServerDir() + "/conf.d/" + name + ".ini"

    with open(programFile, "r") as fr:
        infos = fr.readlines()

    mess = {}
    infos = []
    for line in infos:
        if "command=" in line.strip():
            mess["command"] = line.strip().split('=')[1]
        if "path=" in line.strip():
            mess["path"] = line.strip().split('=')[1]

    log_dir = getServerDir() + '/log/'

    w_body = ""
    w_body += "[program:" + name + "]" + "\n"
    w_body += "command=" + mess["command"] + "\n"
    w_body += "directory=" + mess["path"] + "\n"
    w_body += "autorestart=true" + "\n"
    w_body += "startsecs=3" + "\n"
    w_body += "startretries=3" + "\n"
    w_body += "stdout_logfile=" + log_dir + name + ".out.log" + "\n"
    w_body += "stderr_logfile=" + log_dir + name + ".err.log" + "\n"
    w_body += "stdout_logfile_maxbytes=2MB" + "\n"
    w_body += "stderr_logfile_maxbytes=2MB" + "\n"
    w_body += "user=" + user + "\n"
    w_body += "priority=" + priority + "\n"
    w_body += "numprocs={0}".format(numprocs) + "\n"
    w_body += "process_name=%(program_name)s_%(process_num)02d"

    mw.writeFile(programFile, w_body)

    return mw.returnJson(True, '修改守护进程成功!')


def getJobInfo():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]
    name = args['name']

    mess = {}
    infos = []
    info = {}
    program = getServerDir() + "/conf.d/" + name + ".ini"
    with open(program, "r") as fr:
        infos = fr.readlines()
    mess = {}
    for line in infos:
        if "user=" in line.strip():
            mess["user"] = line.strip().split('=')[1]
        if "numprocs=" in line.strip():
            mess["numprocs"] = line.strip().split('=')[1]
        if "priority=" in line.strip():
            mess["priority"] = line.strip().split('=')[1]
    userlist = getUserListData()
    info["userlist"] = userlist
    info["daemoninfo"] = mess
    return mw.getJson(info)


def runLog():
    return getServerDir() + '/log/supervisor.log'

if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print(status())
    elif func == 'start':
        print(start())
    elif func == 'stop':
        print(stop())
    elif func == 'restart':
        print(restart())
    elif func == 'reload':
        print(reload())
    elif func == 'initd_status':
        print(initdStatus())
    elif func == 'initd_install':
        print(initdInstall())
    elif func == 'initd_uninstall':
        print(initdUinstall())
    elif func == 'run_info':
        print(runInfo())
    elif func == 'conf':
        print(getConf())
    elif func == 'run_log':
        print(runLog())
    elif func == 'get_user_list':
        print(getUserList())
    elif func == 'get_sup_list':
        print(getSupList())
    elif func == 'add_job':
        print(addJob())
    elif func == 'del_job':
        print(delJob())
    elif func == 'update_job':
        print(updateJob())
    elif func == 'get_job_info':
        print(getJobInfo())
    else:
        print('error')
