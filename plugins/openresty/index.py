# coding:utf-8

import sys
import io
import os
import time
import threading
import subprocess
import re

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'openresty'


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


def clearTemp():
    path_bin = getServerDir() + "/nginx"
    mw.execShell('rm -rf ' + path_bin + '/client_body_temp')
    mw.execShell('rm -rf ' + path_bin + '/fastcgi_temp')
    mw.execShell('rm -rf ' + path_bin + '/proxy_temp')
    mw.execShell('rm -rf ' + path_bin + '/scgi_temp')
    mw.execShell('rm -rf ' + path_bin + '/uwsgi_temp')


def getConf():
    path = getServerDir() + "/nginx/conf/nginx.conf"
    return path


def getConfTpl():
    path = getPluginDir() + '/conf/nginx.conf'
    return path


def getOs():
    data = {}
    data['os'] = mw.getOs()
    ng_exe_bin = getServerDir() + "/nginx/sbin/nginx"

    # if mw.isAppleSystem():
    #     data['auth'] = True
    #     return mw.getJson(data)

    if checkAuthEq(ng_exe_bin, 'root'):
        data['auth'] = True
    else:
        data['auth'] = False
    return mw.getJson(data)


def getInitDTpl():
    path = getPluginDir() + "/init.d/nginx.tpl"
    return path


def getPidFile():
    file = getConf()
    content = mw.readFile(file)
    rep = 'pid\s*(.*);'
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
    service_path = os.path.dirname(os.getcwd())
    content = mw.readFile(getConfTpl())
    content = content.replace('{$SERVER_PATH}', service_path)

    user = 'www'
    user_group = 'www'

    current_os = mw.getOs()
    if current_os == 'darwin':
        # macosx do
        # user = mw.execShell(
        #     "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
        user = 'midoks'
        user_group = 'staff'
        content = content.replace('{$EVENT_MODEL}', 'kqueue')
    elif current_os.startswith('freebsd'):
        content = content.replace('{$EVENT_MODEL}', 'kqueue')
    else:
        content = content.replace('{$EVENT_MODEL}', 'epoll')

    content = content.replace('{$OS_USER}', user)
    content = content.replace('{$OS_USER_GROUP}', user_group)

    # ng_conf_md5 = ''
    # ng_conf_md5_file = getServerDir() + '/nginx_conf.md5'
    # if not os.path.exists(ng_conf_md5_file):
    #     ng_conf_md5 = mw.md5(content)
    #     mw.writeFile(ng_conf_md5_file, ng_conf_md5)
    # else:
    #     ng_conf_md5 = mw.writeFile(ng_conf_md5_file).strip()

    # 主配置文件
    nconf = getServerDir() + '/nginx/conf/nginx.conf'
    mw.writeFile(nconf, content)

    # lua配置
    lua_conf_dir = mw.getServerDir() + '/web_conf/nginx/lua'
    if not os.path.exists(lua_conf_dir):
        mw.execShell('mkdir -p ' + lua_conf_dir)

    lua_conf = lua_conf_dir + '/lua.conf'
    lua_conf_tpl = getPluginDir() + '/conf/lua.conf'
    lua_content = mw.readFile(lua_conf_tpl)
    lua_content = lua_content.replace('{$SERVER_PATH}', service_path)
    mw.writeFile(lua_conf, lua_content)

    empty_lua = lua_conf_dir + '/empty.lua'
    if not os.path.exists(empty_lua):
        mw.writeFile(empty_lua, '')

    mw.opLuaMakeAll()

    # 静态配置
    php_conf = mw.getServerDir() + '/web_conf/php/conf'
    if not os.path.exists(php_conf):
        mw.execShell('mkdir -p ' + php_conf)
    static_conf = mw.getServerDir() + '/web_conf/php/conf/enable-php-00.conf'
    if not os.path.exists(static_conf):
        mw.writeFile(static_conf, 'set $PHP_ENV 0;')

    # vhost
    vhost_dir = mw.getServerDir() + '/web_conf/nginx/vhost'
    vhost_tpl_dir = getPluginDir() + '/conf/vhost'
    # print(vhost_dir, vhost_tpl_dir)
    vhost_list = ['0.websocket.conf', '0.nginx_status.conf']
    for f in vhost_list:
        a_conf = vhost_dir + '/' + f
        a_conf_tpl = vhost_tpl_dir + '/' + f
        if not os.path.exists(a_conf):
            mw.writeFile(a_conf, mw.readFile(a_conf_tpl))


def initDreplace():

    file_tpl = getInitDTpl()
    service_path = os.path.dirname(os.getcwd())

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

    # give nginx root permission
    ng_exe_bin = getServerDir() + "/nginx/sbin/nginx"
    if not checkAuthEq(ng_exe_bin, 'root'):
        user = 'www'
        user_group = 'www'
        current_os = mw.getOs()
        if current_os == 'darwin':
            user = 'root'
            user_group = 'staff'
        args = getArgs()
        if not 'pwd' in args:
            print("权限不足，需要认证启动!")
            exit(0)

        sudoPwd = args['pwd']
        cmd_own = 'chown -R ' + user+':' + user_group + ' ' + ng_exe_bin
        mw.execShell('echo %s|sudo -S %s' % (sudoPwd, cmd_own))
        cmd_mod = 'chmod 755 ' + ng_exe_bin
        mw.execShell('echo %s|sudo -S %s' % (sudoPwd, cmd_mod))
        cmd_s = 'chmod u+s ' + ng_exe_bin
        mw.execShell('echo %s|sudo -S %s' % (sudoPwd, cmd_s))

    # systemd
    # /usr/lib/systemd/system
    systemDir = mw.systemdCfgDir()
    systemService = systemDir + '/openresty.service'
    if os.path.exists(systemDir) and not os.path.exists(systemService):
        systemServiceTpl = getPluginDir() + '/init.d/openresty.service.tpl'
        se_content = mw.readFile(systemServiceTpl)
        se_content = se_content.replace('{$SERVER_PATH}', service_path)
        mw.writeFile(systemService, se_content)
        mw.execShell('systemctl daemon-reload')

    return file_bin


def status():
    pid_file = getPidFile()
    if not os.path.exists(pid_file):
        return 'stop'
    return 'start'


def restyOp(method):
    file = initDreplace()

    # 启动时,先检查一下配置文件
    check = getServerDir() + "/bin/openresty -t"
    check_data = mw.execShell(check)
    if not check_data[1].find('test is successful') > -1:
        return check_data[1]

    current_os = mw.getOs()
    if current_os == "darwin":
        data = mw.execShell(file + ' ' + method)
        if data[1] == '':
            return 'ok'
        return data[1]

    if current_os.startswith("freebsd"):
        data = mw.execShell('service openresty ' + method)
        if data[1] == '':
            return 'ok'
        return data[1]

    data = mw.execShell('systemctl ' + method + ' openresty')
    if data[1] == '':
        return 'ok'
    return data[1]


def op_submit_systemctl_restart():
    current_os = mw.getOs()
    if current_os.startswith("freebsd"):
        mw.execShell('service openresty restart')
        return True

    mw.execShell('systemctl restart openresty')
    return True


def op_submit_init_restart(file):
    mw.execShell(file + ' restart')


def restyOp_restart():
    file = initDreplace()

    # 启动时,先检查一下配置文件
    check = getServerDir() + "/bin/openresty -t"
    check_data = mw.execShell(check)
    if not check_data[1].find('test is successful') > -1:
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
    pid_file = getPidFile()
    if os.path.exists(pid_file):
        os.remove(pid_file)
    return r


def restart(version=()):
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

    shell_cmd = 'systemctl status openresty | grep loaded | grep "enabled;"'
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
        mw.execShell('sysrc ' + getPluginName() + '_enable="YES"')
        return 'ok'

    mw.execShell('systemctl enable openresty')
    return 'ok'


def initdUinstall():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return "Apple Computer does not support"

    if current_os.startswith('freebsd'):
        initd_bin = getInitDFile()
        os.remove(initd_bin)
        mw.execShell('sysrc ' + getPluginName() + '_enable="NO"')
        return 'ok'

    mw.execShell('systemctl disable openresty')
    return 'ok'


def runInfo():
    # 取Openresty负载状态
    try:
        url = 'http://127.0.0.1/nginx_status'
        result = mw.httpGet(url, timeout=1)
        tmp = result.split()
        data = {}
        data['active'] = tmp[2]
        data['accepts'] = tmp[9]
        data['handled'] = tmp[7]
        data['requests'] = tmp[8]
        data['Reading'] = tmp[11]
        data['Writing'] = tmp[13]
        data['Waiting'] = tmp[15]
        return mw.getJson(data)
    except Exception as e:

        url = 'http://' + mw.getHostAddr() + '/nginx_status'
        result = mw.httpGet(url)
        tmp = result.split()
        data = {}
        data['active'] = tmp[2]
        data['accepts'] = tmp[9]
        data['handled'] = tmp[7]
        data['requests'] = tmp[8]
        data['Reading'] = tmp[11]
        data['Writing'] = tmp[13]
        data['Waiting'] = tmp[15]
        return mw.getJson(data)
    except Exception as e:
        return 'oprenresty not started'


def errorLogPath():
    return getServerDir() + '/nginx/logs/error.log'


def getCfg():
    cfg = getConf()
    content = mw.readFile(cfg)

    unitrep = "[kmgKMG]"
    cfg_args = [
        {"name": "worker_processes", "ps": "处理进程,auto表示自动,数字表示进程数", 'type': 2},
        {"name": "worker_connections", "ps": "最大并发链接数", 'type': 2},
        {"name": "keepalive_timeout", "ps": "连接超时时间", 'type': 2},
        {"name": "gzip", "ps": "是否开启压缩传输", 'type': 1},
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
        rep = "(%s)\s+(\w+)" % i["name"]
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


def setCfg():

    args = getArgs()
    data = checkArgs(args, [
        'worker_processes', 'worker_connections', 'keepalive_timeout',
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
        rep = "%s\s+[^kKmMgG\;\n]+" % k
        if k == "worker_processes" or k == "gzip":
            if not re.search("auto|on|off|\d+", v):
                return mw.returnJson(False, '参数值错误')
        else:
            if not re.search("\d+", v):
                return mw.returnJson(False, '参数值错误,请输入数字整数')

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


def installPreInspection():
    return 'ok'


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
    else:
        print('error')
