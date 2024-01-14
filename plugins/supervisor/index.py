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
            t = args[i].split(':', 1)
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

    confD = getServerDir() + "/conf.d"
    conf = getServerDir() + "/supervisor.conf"
    systemDir = mw.systemdCfgDir()
    systemService = systemDir + '/supervisor.service'
    systemServiceTpl = getPluginDir() + '/init.d/supervisor.service'

    service_path = os.path.dirname(os.getcwd())

    if not os.path.exists(confD):
        os.mkdir(confD)

    if not os.path.exists(conf):
        # config replace
        user = 'root'
        if mw.isAppleSystem():
            cmd = "who | sed -n '2, 1p' |awk '{print $1}'"
            user = mw.execShell(cmd)[0].strip()

        conf_content = mw.readFile(getConfTpl())
        conf_content = conf_content.replace('{$SERVER_PATH}', service_path)
        conf_content = conf_content.replace('{$OS_USER}', user)
        mw.writeFile(conf, conf_content)

    if os.path.exists(systemDir) and not os.path.exists(systemService):
        activate_file = mw.getRunDir() + '/bin/activate'
        if os.path.exists(activate_file):
            supervisord_bin = mw.execShell(
                'source ' + activate_file + '&& which supervisord')[0].strip()
        else:
            supervisord_bin = mw.execShell('which supervisord')[0].strip()

        se_content = mw.readFile(systemServiceTpl)
        se_content = se_content.replace('{$SERVER_PATH}', service_path)
        se_content = se_content.replace('{$SUP_BIN}', supervisord_bin)
        mw.writeFile(systemService, se_content)
        mw.execShell('systemctl daemon-reload')

    return True


def supOp(method):
    initDreplace()

    if not mw.isAppleSystem():
        data = mw.execShell('systemctl ' + method + ' supervisor')
        if data[1] == '':
            return 'ok'
        return data[1]

    if method in ('reload', 'restart'):
        return 'ok'

    cmd = 'supervisord -c ' + getServerDir() + '/supervisor.conf'
    if method == 'stop':
        cmd = "ps -ef|grep supervisor | grep -v grep | grep -v index.py | awk '{print $2}'|xargs kill"
    data = mw.execShell(cmd)
    if data[1] == '':
        return 'ok'
    return data[1]


def start():
    return supOp('start')


def stop():
    return supOp('stop')


def restart():
    return supOp('restart')


def reload():
    return supOp('reload')


def initdStatus():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    shell_cmd = 'systemctl status supervisor | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'


def initdInstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl enable supervisor')
    return 'ok'


def initdUinstall():
    if not app_debug:
        if mw.isAppleSystem():
            return "Apple Computer does not support"

    mw.execShell('systemctl diable supervisor')
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
                    # d["command"] = line.strip().split('=')[1]
                    d["command"] = "子配置查看"
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

def confDList():
    confd_dir = getServerDir() + '/conf.d'
    clist = os.listdir(confd_dir)
    array_list = []
    for x in range(len(clist)):
        t = {}
        t['name'] = clist[x]
        array_list.append(t)

    data = {}
    data['data'] = array_list
    return mw.getJson(data)


def confDlistTraceLog():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    confd_dir = getServerDir() + '/conf.d/' + args['name']
    content = mw.readFile(confd_dir)
    rep = 'stdout_logfile\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def confDlistErrorLog():
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    confd_dir = getServerDir() + '/conf.d/' + args['name']
    content = mw.readFile(confd_dir)
    rep = 'stderr_logfile\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()

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

    if mw.isAppleSystem():
        cmd = "who | sed -n '2, 1p' |awk '{print $1}'"
        user = mw.execShell(cmd)[0].strip()
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
    w_body += "stdout_logfile_maxbytes=1MB" + "\n"
    w_body += "stderr_logfile_maxbytes=1MB" + "\n"
    w_body += "user=" + user + "\n"
    w_body += "priority=999" + "\n"
    w_body += "numprocs={0}".format(numprocs) + "\n"
    w_body += "process_name=%(program_name)s"
    # _%(process_num)02d

    dstFile = getSubConfDir() + "/" + program + '.ini'

    mw.writeFile(dstFile, w_body)

    return mw.returnJson(True, '增加守护进程成功!')


def startJob():
    args = getArgs()
    data = checkArgs(args, ['name', 'status'])
    if not data[0]:
        return data[1]

    supCtl = 'supervisorctl -c ' + getServerDir() + "/supervisor.conf"

    name = args['name']
    status = args['status']

    action = "启动"
    cmd = supCtl + " start " + name
    if status == 'start':
        action = "停止"
        cmd = supCtl + " stop " + name
    # print(cmd)
    data = mw.execShell(cmd)
    # print(data)

    if data[1] != '':
        return mw.returnJson(False, action + '[' + name + ']失败!')
    return mw.returnJson(True, action + '[' + name + ']成功!')


def restartJob():
    args = getArgs()
    data = checkArgs(args, ['name', 'status'])
    if not data[0]:
        return data[1]

    supCtl = 'supervisorctl -c ' + getServerDir() + "/supervisor.conf"

    name = args['name']
    status = args['status']

    cmd = supCtl + " stop " + name
    data = mw.execShell(cmd)
    cmd = supCtl + " start " + name
    data = mw.execShell(cmd)

    if data[1] != '':
        return mw.returnJson(False,  '[' + name + ']重启失败!')
    return mw.returnJson(True,  '[' + name + ']重启成功!')


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

    mess = {}
    infos = []
    with open(programFile, "r") as fr:
        infos = fr.readlines()

    for line in infos:
        if "command=" in line.strip():
            mess["command"] = line.strip().split('=')[1]
        if "directory=" in line.strip():
            mess["path"] = line.strip().split('=')[1]

    # print(mess)
    log_file_name = getServerDir() + '/log/' + name

    w_body = ""
    w_body += "[program:" + name + "]" + "\n"
    w_body += "command=" + mess["command"] + "\n"
    w_body += "directory=" + mess["path"] + "\n"
    w_body += "autorestart=true" + "\n"
    w_body += "startsecs=3" + "\n"
    w_body += "startretries=3" + "\n"
    w_body += "stdout_logfile=" + log_file_name + ".out.log" + "\n"
    w_body += "stderr_logfile=" + log_file_name + ".err.log" + "\n"
    w_body += "stdout_logfile_maxbytes=2MB" + "\n"
    w_body += "stderr_logfile_maxbytes=2MB" + "\n"
    w_body += "user=" + user + "\n"
    w_body += "priority=" + priority + "\n"
    w_body += "numprocs={0}".format(numprocs) + "\n"
    w_body += "process_name=%(program_name)s%"

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


def configTpl():
    path = getServerDir() + '/conf.d'
    pathFile = os.listdir(path)
    tmp = []
    for one in pathFile:
        if one.endswith(".ini"):
            file = path + '/' + one
            tmp.append(file)
    return mw.getJson(tmp)


def readConfigTpl():
    args = getArgs()
    data = checkArgs(args, ['file'])
    if not data[0]:
        return data[1]

    content = mw.readFile(args['file'])
    return mw.returnJson(True, 'ok', content)


def readConfigLogTpl():
    args = getArgs()
    data = checkArgs(args, ['file'])
    if not data[0]:
        return data[1]
    file_log = args['file']
    line_log = args['line']

    with open(file_log, "r") as fr:
        infos = fr.readlines()

    stdout_logfile = ''
    for line in infos:
        if "stdout_logfile=" in line.strip():
            stdout_logfile = line.strip().split('=')[1]

    if stdout_logfile != '':
        data = mw.getLastLine(stdout_logfile, int(line_log))
        return mw.returnJson(True, 'OK', data)
    return mw.returnJson(False, 'OK', '')


def readConfigLogErrorTpl():
    args = getArgs()
    data = checkArgs(args, ['file'])
    if not data[0]:
        return data[1]
    file_log = args['file']
    line_log = args['line']

    with open(file_log, "r") as fr:
        infos = fr.readlines()

    stderr_logfile = ''
    for line in infos:
        if "stderr_logfile=" in line.strip():
            stderr_logfile = line.strip().split('=')[1]

    if stderr_logfile != '':
        data = mw.getLastLine(stderr_logfile, int(line_log))
        return mw.returnJson(True, 'OK', data)
    return mw.returnJson(False, 'OK', '')


def supClearLog():
    args = getArgs()
    data = checkArgs(args, ['file'])
    if not data[0]:
        return data[1]
    file_log = args['file']

    with open(file_log, "r") as fr:
        infos = fr.readlines()

    stdout_logfile = ''
    stderr_logfile = ''
    for line in infos:
        if "stdout_logfile=" in line.strip():
            stdout_logfile = line.strip().split('=')[1]
        if "stderr_logfile=" in line.strip():
            stderr_logfile = line.strip().split('=')[1]

    cmd_stdout = "echo '' > " + stdout_logfile
    cmd_stderr = "echo '' > " + stderr_logfile
    mw.execShell(cmd_stdout)
    mw.execShell(cmd_stderr)
    return mw.returnJson(True, '清空成功')


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
    elif func == 'config_tpl':
        print(configTpl())
    elif func == 'read_config_tpl':
        print(readConfigTpl())
    elif func == 'read_config_log_tpl':
        print(readConfigLogTpl())
    elif func == 'read_config_log_error_tpl':
        print(readConfigLogErrorTpl())
    elif func == 'sup_clear_log':
        print(supClearLog())
    elif func == 'conf':
        print(getConf())
    elif func == 'run_log':
        print(runLog())
    elif func == 'get_user_list':
        print(getUserList())
    elif func == 'get_sup_list':
        print(getSupList())
    elif func == 'confd_list':
        print(confDList())
    elif func == 'confd_list_trace_log':
        print(confDlistTraceLog())
    elif func == 'confd_list_error_log':
        print(confDlistErrorLog())
    elif func == 'add_job':
        print(addJob())
    elif func == 'start_job':
        print(startJob())
    elif func == 'restart_job':
        print(restartJob())
    elif func == 'del_job':
        print(delJob())
    elif func == 'update_job':
        print(updateJob())
    elif func == 'get_job_info':
        print(getJobInfo())
    else:
        print('error')
