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
    mw.execShell('rm -rf ' + path_bin + '/client_body_temp')


def getConf():
    path = getServerDir() + "/httpd/conf/httpd.conf"
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
    return getServerDir() + '/httpd/logs/error_log'


def getCfg():
    cfg = getConf()
    content = mw.readFile(cfg)

    unitrep = "[kmgKMG]"
    cfg_args = [
        {"name": "worker_processes", "ps": "处理进程,auto表示自动,数字表示进程数", 'type': 2},
        {"name": "worker_connections", "ps": "最大并发链接数", 'type': 2},
        {"name": "keepalive_timeout", "ps": "连接超时时间", 'type': 2},
        {"name": "zstd", "ps": "是否开启zstd压缩传输", 'type': 1},
        {"name": "brotli", "ps": "是否开启brotli压缩传输", 'type': 1},
        {"name": "gzip", "ps": "是否开启gzip压缩传输", 'type': 1},
        {"name": "gzip_min_length", "ps": "最小压缩文件", 'type': 2},
        {"name": "gzip_comp_level", "ps": "压缩率", 'type': 2},
        {"name": "client_max_body_size", "ps": "最大上传文件", 'type': 2},
        {"name": "server_names_hash_bucket_size",
            "ps": "服务器名字的hash表大小", 'type': 2},
        {"name": "client_header_buffer_size", "ps": "客户端请求头buffer大小", 'type': 2},
    ]

    # {"name": "client_body_buffer_size", "ps": "请求主体缓冲区"}
    rdata = []
    for i in cfg_args:
        rep = r"(%s)\s+(\w+)" % i["name"]
        k = re.search(rep, content)
        if not k:
            return mw.returnJson(False, "获取 key {} 失败".format(k))
        k = k.group(1)
        v = re.search(rep, content)
        if not v:
            return mw.returnJson(False, "获取 value {} 失败".format(v))
        v = v.group(2)

        if re.search(unitrep, v):
            u = str.upper(v[-1])
            v = v[:-1]
            if len(u) == 1:
                psstr = u + "B，" + i["ps"]
            else:
                psstr = u + "，" + i["ps"]
        else:
            u = ""

        kv = {"name": k, "value": v, "unit": u,
              "ps": i["ps"], "type": i["type"]}
        rdata.append(kv)

    return mw.returnJson(True, "ok", rdata)

def replaceChar(value, index, new_char):
    return value[:index] + new_char + value[index+1:]

def makeWorkerCpuAffinity(val):
    if val == "auto":
        return "auto"

    if mw.isNumber(val):
        core_num = int(val)
        default_core_str = "0"*core_num
        core_num_arr = []
        for x in range(core_num):
            t = replaceChar(default_core_str, x , "1")
            core_num_arr.append(t)
        return " ".join(core_num_arr)

    return 'auto'

def setCfg():

    args = getArgs()
    data = checkArgs(args, [
        'worker_processes', 'worker_connections', 'keepalive_timeout','zstd','brotli',
        'gzip', 'gzip_min_length', 'gzip_comp_level', 'client_max_body_size',
        'server_names_hash_bucket_size', 'client_header_buffer_size'
    ])
    if not data[0]:
        return data[1]

    cfg = getConf()
    mw.backFile(cfg)
    content = mw.readFile(cfg)

    unitrep = "[kmgKMG]"
    cfg_args = [
        {"name": "worker_processes", "ps": "处理进程,auto表示自动,数字表示进程数", 'type': 2},
        {"name": "worker_connections", "ps": "最大并发链接数", 'type': 2},
        {"name": "keepalive_timeout", "ps": "连接超时时间", 'type': 2},
        {"name": "zstd", "ps": "是否开启zstd压缩传输", 'type': 1},
        {"name": "brotli", "ps": "是否开启brotli压缩传输", 'type': 1},
        {"name": "gzip", "ps": "是否开启压缩传输", 'type': 1},
        {"name": "gzip_min_length", "ps": "最小压缩文件", 'type': 2},
        {"name": "gzip_comp_level", "ps": "压缩率", 'type': 2},
        {"name": "client_max_body_size", "ps": "最大上传文件", 'type': 2},
        {"name": "server_names_hash_bucket_size",
            "ps": "服务器名字的hash表大小", 'type': 2},
        {"name": "client_header_buffer_size", "ps": "客户端请求头buffer大小", 'type': 2},
    ]

    # print(args)
    for k, v in args.items():
        # print(k, v)
        rep = r"%s\s+[^kKmMgG\;\n]+" % k
        if k == "worker_processes" or k == "gzip":
            if not re.search(r"auto|on|off|\d+", v):
                return mw.returnJson(False, '参数值错误')
        elif k == "zstd" or k == "brotli":
            if not re.search(r"auto|on|off|\d+", v):
                return mw.returnJson(False, '参数值错误')
        else:
            if not re.search(r"\d+", v):
                return mw.returnJson(False, '参数值错误,请输入数字整数')

        if k == "worker_processes" :
            k_wca = "worker_cpu_affinity"
            rep_wca = r"%s\s+[^\;\n]+" % k_wca
            v_wca = makeWorkerCpuAffinity(v)
            newconf = "%s %s" % (k_wca, v_wca)
            content = re.sub(rep_wca, newconf, content)


        if re.search(rep, content):
            newconf = "%s %s" % (k, v)
            content = re.sub(rep, newconf, content)
        elif re.search(rep, content):
            newconf = "%s %s" % (k, v)
            content = re.sub(rep, newconf, content)

    mw.writeFile(cfg, content)
    isError = mw.checkWebConfig()
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
