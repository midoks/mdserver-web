# coding:utf-8

import sys
import io
import os
import time
import threading
import subprocess
import re


web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'apache'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return '/tmp/' + getPluginName()

    if current_os.startswith('freebsd'):
        return '/etc/rc.d/' + getPluginName()

    return '/etc/init.d/' + getPluginName()


def getArgs():
    args = sys.argv[2:]
    # print(args)
    tmp = {}
    args_len = len(args)

    if args_len == 1:
        t = args[0].strip('{').strip('}')
        t = t.split(':',2)
        tmp[t[0]] = t[1]
    elif args_len > 1:
        for i in range(len(args)):
            t = args[i].split(':',2)
            tmp[t[0]] = t[1]
    # print(tmp)
    return tmp


def checkArgs(data, ck=[]):
    for i in range(len(ck)):
        if not ck[i] in data:
            return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, mw.returnJson(True, 'ok'))


def clearTemp():
    path_bin = getServerDir() + "/httpd"


def getConf():
    path = getServerDir() + "/httpd/conf/httpd.conf"
    return path


def getConfMpm():
    path = getServerDir() + "/httpd/conf/extra/httpd-mpm.conf"
    return path


def getConfTpl():
    path = getPluginDir() + '/conf/httpd.conf'
    return path


def getOs():
    data = {}
    data['os'] = mw.getOs()
    data['auth'] = True
    return mw.getJson(data)


def getInitDTpl():
    path = getPluginDir() + "/init.d/httpd.tpl"
    return path


def getPidFile():
    file = getConf()
    content = mw.readFile(file)
    rep = r'pid\s*(.*);'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def getFileOwner(filename):
    import pwd
    stat = os.lstat(filename)
    uid = stat.st_uid
    pw = pwd.getpwuid(uid)
    return pw.pw_name


def checkAuthEq(file, owner='root'):
    fowner = getFileOwner(file)
    if (fowner == owner):
        return True
    return False


def confReplace():
    service_path = mw.getServerDir()
    content = mw.readFile(getConfTpl())
    content = content.replace('{$SERVER_PATH}', service_path)

    # 主配置文件
    nconf = getServerDir() + '/httpd/conf/httpd.conf'
    mw.writeFile(nconf, content)


def initDreplace():

    file_tpl = getInitDTpl()
    service_path = mw.getServerDir()

    initD_path = getServerDir() + '/init.d'

    # OpenResty is not installed
    if not os.path.exists(getServerDir()):
        print("ok")
        exit(0)

    # init.d
    file_bin = initD_path + '/' + getPluginName()
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)

        # initd replace
        content = mw.readFile(file_tpl)
        content = content.replace('{$SERVER_PATH}', service_path)
        mw.writeFile(file_bin, content)
        mw.execShell('chmod +x ' + file_bin)

        # config replace
        confReplace()

    # systemd
    # /usr/lib/systemd/system
    systemDir = mw.systemdCfgDir()
    systemService = systemDir + '/httpd.service'
    if os.path.exists(systemDir) and not os.path.exists(systemService):
        systemServiceTpl = getPluginDir() + '/init.d/httpd.service.tpl'
        se_content = mw.readFile(systemServiceTpl)
        se_content = se_content.replace('{$SERVER_PATH}', service_path)
        mw.writeFile(systemService, se_content)
        mw.execShell('systemctl daemon-reload')

    return file_bin


def status():
    cmd = "ps -ef|grep 'httpd/bin/httpd' |grep -v grep | grep -v python | awk '{print $2}'"
    data = mw.execShell(cmd)
    if data[0] == '':
        return 'stop'
    return 'start'


def restyOp(method):
    file = initDreplace()

    # 启动时,先检查一下配置文件
    check = getServerDir() + "/httpd/bin/httpd -t"
    check_data = mw.execShell(check)
    if not check_data[1].find('Syntax OK') > -1:
        return check_data[1]

    current_os = mw.getOs()
    if current_os == "darwin":
        data = mw.execShell(file + ' ' + method)
        if data[1] == '':
            return 'ok'
        return data[1]

    if current_os.startswith("freebsd"):
        mw.execShell('service httpd '+method)
        if data[1] == '':
            return 'ok'
        return data[1]

    data = mw.execShell('systemctl ' + method + ' httpd')
    if data[1] == '':
        return 'ok'
    return data[1]


def op_submit_systemctl_restart():
    current_os = mw.getOs()
    if current_os.startswith("freebsd"):
        mw.execShell('service httpd restart')
        return True

    mw.execShell('systemctl restart httpd')
    return True


def op_submit_init_restart(file):
    mw.execShell(file + ' restart')


def restyOp_restart():
    file = initDreplace()

    # 启动时,先检查一下配置文件
    check = getServerDir() + "/httpd/bin/httpd -t"
    check_data = mw.execShell(check)
    if not check_data[1].find('Syntax OK') > -1:
        return 'ERROR: 配置出错<br><a style="color:red;">' + check_data[1].replace("\n", '<br>') + '</a>'

    if not mw.isAppleSystem():
        threading.Timer(2, op_submit_systemctl_restart).start()
        return 'ok'

    threading.Timer(2, op_submit_init_restart, args=(file,)).start()
    return 'ok'


def start():
    return restyOp('start')


def stop():
    r = restyOp('stop')

    mw.execShell("ps -ef|grep httpd | grep -v grep | awk '{print $2}'|xargs -r kill")
    return r


def restart():
    return restyOp_restart()


def reload():
    confReplace()
    return restyOp('reload')


def initdStatus():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return "Apple Computer does not support"

    if current_os.startswith('freebsd'):
        initd_bin = getInitDFile()
        if os.path.exists(initd_bin):
            return 'ok'

    shell_cmd = 'systemctl status httpd | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'


def initdInstall():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return "Apple Computer does not support"

    # freebsd initd install
    if current_os.startswith('freebsd'):
        import shutil
        source_bin = initDreplace()
        initd_bin = getInitDFile()
        shutil.copyfile(source_bin, initd_bin)
        mw.execShell('chmod +x ' + initd_bin)
        mw.execShell('sysrc httpd_enable="YES"')
        return 'ok'

    mw.execShell('systemctl enable httpd')
    return 'ok'


def initdUinstall():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return "Apple Computer does not support"

    if current_os.startswith('freebsd'):
        initd_bin = getInitDFile()
        os.remove(initd_bin)
        mw.execShell('sysrc httpd_enable="NO"')
        return 'ok'

    mw.execShell('systemctl disable httpd')
    return 'ok'

def getHttpdStatusPort():
    conf = mw.getServerDir() + '/apache/httpd/conf/httpd.conf'
    content = mw.readFile(conf)
    if not content:
        return None
    rep = r'^\s*Listen\s*(?:\d+\.\d+\.\d+\.\d+:)?(\d+)'  # 匹配非注释行的 Listen 指令，忽略大小写
    tmp = re.search(rep, content, re.IGNORECASE | re.MULTILINE)
    if tmp:
        port = tmp.groups()[0].strip()
        return port
    return None


def runInfoDone(data):
    result = {}
    if not data:
        return result
    
    # 解析服务器状态数据
    lines = data.strip().split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            result[key] = value
    
    return result


def runInfo():
    op_status = status()
    if op_status == 'stop':
        return mw.returnJson(False, "未启动!")

    port = getHttpdStatusPort()
    if not port:
        return mw.returnJson(False, "无法获取端口信息!")
    
    # 取Openresty负载状态
    try:
        url = 'http://127.0.0.1:%s/server-status?auto' % port
        result = mw.httpGet(url, timeout=3)
        data = runInfoDone(result)
        return mw.getJson(data)
    except Exception as e:
        try:
            url = 'http://' + mw.getHostAddr() + ':%s/server-status?auto' % port
            result = mw.httpGet(url)
            data = runInfoDone(result)
            return mw.getJson(data)
        except Exception as e:
            return mw.returnJson(False, "apache异常!")
        
    except Exception as e:
        return mw.returnJson(False, "apache not started!")


def errorLogPath():
    return getServerDir() + '/httpd/logs/error.log'


def getCfg():
    cfg = getConfMpm()
    content = mw.readFile(cfg)

    unitrep = "[kmgKMG]"
    
    # 获取当前 MPM 模块
    mpm_module = ""
    mpm_match = re.search(r"mpm_(\w+)_module", content)
    if mpm_match:
        mpm_module = mpm_match.group(1)
    
    # MPM 配置参数
    mpm_cfg_args = {
        "prefork": [
            {"name": "StartServers", "ps": "服务器进程启动数量", 'type': 2},
            {"name": "MinSpareServers", "ps": "保持空闲的最小服务器进程数", 'type': 2},
            {"name": "MaxSpareServers", "ps": "保持空闲的最大服务器进程数", 'type': 2},
            {"name": "MaxRequestWorkers", "ps": "允许启动的最大服务器进程数", 'type': 2},
            {"name": "MaxConnectionsPerChild", "ps": "服务器进程服务的最大连接数", 'type': 2},
        ],
        "worker": [
            {"name": "StartServers", "ps": "初始服务器进程数", 'type': 2},
            {"name": "MinSpareThreads", "ps": "保持空闲的最小工作线程数", 'type': 2},
            {"name": "MaxSpareThreads", "ps": "保持空闲的最大工作线程数", 'type': 2},
            {"name": "ThreadsPerChild", "ps": "每个服务器进程的工作线程数", 'type': 2},
            {"name": "MaxRequestWorkers", "ps": "最大工作线程数", 'type': 2},
            {"name": "MaxConnectionsPerChild", "ps": "服务器进程服务的最大连接数", 'type': 2},
        ],
        "event": [
            {"name": "StartServers", "ps": "初始服务器进程数", 'type': 2},
            {"name": "MinSpareThreads", "ps": "保持空闲的最小工作线程数", 'type': 2},
            {"name": "MaxSpareThreads", "ps": "保持空闲的最大工作线程数", 'type': 2},
            {"name": "ThreadsPerChild", "ps": "每个服务器进程的工作线程数", 'type': 2},
            {"name": "MaxRequestWorkers", "ps": "最大工作线程数", 'type': 2},
            {"name": "MaxConnectionsPerChild", "ps": "服务器进程服务的最大连接数", 'type': 2},
        ],
        "netware": [
            {"name": "ThreadStackSize", "ps": "每个工作线程分配的堆栈大小", 'type': 2},
            {"name": "StartThreads", "ps": "服务器启动时启动的工作线程数", 'type': 2},
            {"name": "MinSpareThreads", "ps": "保持空闲的最小线程数", 'type': 2},
            {"name": "MaxSpareThreads", "ps": "保持空闲的最大线程数", 'type': 2},
            {"name": "MaxThreads", "ps": "同时活跃的最大工作线程数", 'type': 2},
            {"name": "MaxConnectionsPerChild", "ps": "线程服务的最大连接数", 'type': 2},
        ],
        "mpmt_os2": [
            {"name": "StartServers", "ps": "维护的服务器进程数", 'type': 2},
            {"name": "MinSpareThreads", "ps": "每个进程的最小空闲线程数", 'type': 2},
            {"name": "MaxSpareThreads", "ps": "每个进程的最大空闲线程数", 'type': 2},
            {"name": "MaxConnectionsPerChild", "ps": "每个服务器进程的最大连接数", 'type': 2},
        ],
        "winnt": [
            {"name": "ThreadsPerChild", "ps": "服务器进程中的工作线程数", 'type': 2},
            {"name": "MaxConnectionsPerChild", "ps": "服务器进程服务的最大连接数", 'type': 2},
        ]
    }
    
    # 通用配置参数
    common_cfg_args = [
        {"name": "MaxMemFree", "ps": "每个分配器允许持有的最大空闲KB数", 'type': 2},
    ]
    
    # 合并配置参数
    cfg_args = []
    if mpm_module in mpm_cfg_args:
        cfg_args.extend(mpm_cfg_args[mpm_module])
    cfg_args.extend(common_cfg_args)

    rdata = []
    for i in cfg_args:
        # 匹配 MPM 特定配置
        rep = r"<IfModule mpm_%s_module>.*?(%s)\s+(\w+).*?</IfModule>" % (mpm_module, i["name"])
        k = re.search(rep, content, re.DOTALL)
        
        # 如果没有找到 MPM 特定配置，尝试匹配通用配置
        if not k:
            rep = r"(%s)\s+(\w+)" % i["name"]
            k = re.search(rep, content)
        
        if not k:
            continue
        
        key = k.group(1)
        v = k.group(2) if len(k.groups()) > 1 else ""

        if re.search(unitrep, v):
            u = str.upper(v[-1])
            v = v[:-1]
            if len(u) == 1:
                psstr = u + "B，" + i["ps"]
            else:
                psstr = u + "，" + i["ps"]
        else:
            u = ""

        kv = {"name": key, "value": v, "unit": u,
              "ps": i["ps"], "type": i["type"]}
        rdata.append(kv)
    return mw.returnJson(True, "ok", rdata)

def replaceChar(value, index, new_char):
    return value[:index] + new_char + value[index+1:]

def setCfg():
    # return mw.returnJson(False, '暂时不支持')

    args = getArgs()
    
    # 检查参数，允许动态参数
    cfg = getConfMpm()
    mw.backFile(cfg)
    content = mw.readFile(cfg)

    # 获取当前 MPM 模块
    mpm_module = ""
    mpm_match = re.search(r"mpm_(\w+)_module", content)
    if mpm_match:
        mpm_module = mpm_match.group(1)

    # 验证参数值
    for k, v in args.items():
        # 检查是否为数字参数
        if not re.search(r"\d+", v):
            return mw.returnJson(False, '参数值错误,请输入数字整数')

        # 替换 MPM 特定配置
        if mpm_module:
            def replace_mpm_config(match):
                return match.group(1) + k + match.group(2) + v + match.group(3)
            rep = r"(<IfModule mpm_%s_module>.*?)%s(\s+)\d+(.*?</IfModule>)" % (mpm_module, k)
            if re.search(rep, content, re.DOTALL):
                content = re.sub(rep, replace_mpm_config, content, flags=re.DOTALL)
        
        # 替换通用配置
        def replace_common_config(match):
            return k + match.group(1) + v
        rep = r"%s(\s+)\d+" % k
        if re.search(rep, content):
            content = re.sub(rep, replace_common_config, content)

    mw.writeFile(cfg, content)
    isError = mw.checkHttpdConfig()
    if (isError != True):
        mw.restoreFile(cfg)
        return mw.returnJson(False, 'ERROR: 配置出错<br><a style="color:red;">' + isError.replace("\n", '<br>') + '</a>')

    mw.restartWeb()
    return mw.returnJson(True, '设置成功')


def cronAddCheck():
    try:
        import tool_task
        tool_task.createBgTask()
        return mw.returnJson(True, '添加检查任务成功')
    except Exception as e:
        return mw.returnJson(False, '添加检查任务失败:'+str(e))

def cronDelCheck():
    try:
        import tool_task
        tool_task.removeBgTask()
        return mw.returnJson(True, '删除检查任务成功')
    except Exception as e:
        return mw.returnJson(False, '删除检查任务失败:'+str(e))

def cronCheck():
    return 'ok'


def installPreInspection():
    return 'ok'


if __name__ == "__main__":

    version = '2.4'
    version_pl = getServerDir() + "/version.pl"
    if os.path.exists(version_pl):
        version = mw.readFile(version_pl)


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
    elif func == 'install_pre_inspection':
        print(installPreInspection())
    elif func == 'conf':
        print(getConf())
    elif func == 'get_os':
        print(getOs())
    elif func == 'run_info':
        print(runInfo())
    elif func == 'error_log':
        print(errorLogPath())
    elif func == 'get_cfg':
        print(getCfg())
    elif func == 'set_cfg':
        print(setCfg())
    elif func == 'check':
        print(cronCheck())
    elif func == 'cron_add_check':
        print(cronAddCheck())
    elif func == 'cron_del_check':
        print(cronDelCheck())
    else:
        print('error')
