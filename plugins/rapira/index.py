# coding:utf-8

import sys
import io
import os
import time
import re
import json
import shutil

try:
    import tomllib
except ImportError:
    import tomli as tomllib

# reload(sys)
# sys.setdefaultencoding('utf8')

web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'rapira'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile(version):
    current_os = mw.getOs()
    if current_os == 'darwin':
        return '/tmp/' + getPluginName()

    if current_os.startswith('freebsd'):
        return '/etc/rc.d/' + getPluginName()
    return '/etc/init.d/' + getPluginName() + version


def getArgs():
    args = sys.argv[3:]
    tmp = {}
    args_len = len(args)

    if args_len == 1:
        t = args[0].strip('{').strip('}')
        if t.strip() == '':
            tmp = []
        else:
            t = t.split(':', 1)
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


def getConf(version):
    path = getServerDir() + '/' + version + '/rapira.toml'
    return path


def getFpmConfFile(version, pool='www'):
    args = getArgs()
    if 'pool' in args:
        pool = args['pool']
    return getServerDir() + '/' + version + '/etc/php-fpm.d/'+pool+'.conf'

def getFpmFile(version):
    return getServerDir() + '/' + version + '/etc/php-fpm.conf'


def status_progress(version):
    # ps -ef|grep 'php/81' |grep -v grep | grep -v python | awk '{print $2}
    cmd = "ps -ef|grep 'rapira/" + version + \
        "' |grep -v grep | grep -v python | awk '{print $2}'"
    data = mw.execShell(cmd)
    if data[0] == '':
        return 'stop'
    return 'start'


def getPhpSocket(version):
    path = getFpmConfFile(version)
    content = mw.readFile(path)
    rep = r'listen\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def status(version):
    '''
    sock文件判断是否启动
    '''
    # sock = getPhpSocket(version)
    # if sock.find(':')>-1:
    #     return status_progress(version)

    # if not os.path.exists(sock):
    #     return 'stop'
    return status_progress(version)
    # return 'stop'


def contentReplace(content, version):
    service_path = mw.getServerDir()
    content = content.replace('{$ROOT_PATH}', mw.getFatherDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$PHP_VERSION}', version)
    content = content.replace('{$LOCAL_IP}', mw.getLocalIp())
    content = content.replace('{$SSL_CRT}', mw.getSslCrt())

    if mw.isAppleSystem():
        # user = mw.execShell(
        #     "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
        content = content.replace('{$PHP_USER}', 'nobody')
        content = content.replace('{$PHP_GROUP}', 'nobody')

        rep = r'listen.owner\s*=\s*(.+)\r?\n'
        val = ';listen.owner = nobody\n'
        content = re.sub(rep, val, content)

        rep = r'listen.group\s*=\s*(.+)\r?\n'
        val = ';listen.group = nobody\n'
        content = re.sub(rep, val, content)

        rep = r'user\s*=\s*(.+)\r?\n'
        val = ';user = nobody\n'
        content = re.sub(rep, val, content)

        rep = r'[^\.]group\s*=\s*(.+)\r?\n'
        val = ';group = nobody\n'
        content = re.sub(rep, val, content)

    else:
        content = content.replace('{$PHP_USER}', 'www')
        content = content.replace('{$PHP_GROUP}', 'www')
    return content


def phpPrependFile(version):
    app_start = getServerDir() + '/app_start.php'
    if not os.path.exists(app_start):
        tpl = getPluginDir() + '/conf/app_start.php'
        content = mw.readFile(tpl)
        content = contentReplace(content, version)
        mw.writeFile(app_start, content)



def makePhpIni(version):
    dst_ini = getConf(version)
    if not os.path.exists(dst_ini):
        src_ini = getPluginDir() + '/conf/php' + version[0:1] + '.ini'
        # shutil.copyfile(s_ini, d_ini)
        content = mw.readFile(src_ini)
        if version == '52':
            content = content + "auto_prepend_file=/www/server/php/app_start.php"

        content = contentReplace(content, version)
        mw.writeFile(dst_ini, content)


def commonReplace(content,version):
    service_path = mw.getServerDir()
    content = content.replace('{$VERSION}', version)
    content = content.replace('{$SERVER_PATH}', service_path)
    return content

def initReplace(version):
    initD_path = getServerDir() + '/init.d'
    # if not os.path.exists(initD_path):
    #     os.mkdir(initD_path)

    file_bin = initD_path + '/rapira' + version
    # if not os.path.exists(file_bin):
    #     file_tpl = getPluginDir() + '/init.d/php.tpl'
    #     content = mw.readFile(file_tpl)
    #     content = contentReplace(content, version)

    #     mw.writeFile(file_bin, content)
    #     mw.execShell('chmod +x ' + file_bin)

    toml_file_tpl = getPluginDir()+"/conf/rapira.toml"
    toml_file = getServerDir()+"/"+version+"/rapira.toml"
    if not os.path.exists(toml_file):
        content = mw.readFile(toml_file_tpl)
        content = commonReplace(content, version)
        mw.writeFile(toml_file,content)

    # 模版例子
    exp_ds_file_tpl = getPluginDir()+"/exp/dispatcher-sync.php"
    exp_ds_file = getServerDir()+"/"+version+"/dispatcher-sync.php"
    if not os.path.exists(exp_ds_file):
        content = mw.readFile(exp_ds_file_tpl)
        mw.writeFile(exp_ds_file,exp_ds_file_tpl)

    session_path = getServerDir() + '/tmp/session'
    if not os.path.exists(session_path):
        mw.execShell('mkdir -p ' + session_path)
        mw.execShell('chown -R www:www ' + session_path)

    upload_path = getServerDir() + '/tmp/upload'
    if not os.path.exists(upload_path):
        mw.execShell('mkdir -p ' + upload_path)
        mw.execShell('chown -R www:www ' + upload_path)

    # systemd
    systemDir = mw.systemdCfgDir()
    systemService = systemDir + '/rapira' + version + '.service'
    if os.path.exists(systemDir) and not os.path.exists(systemService):
        systemServiceTpl = getPluginDir() + '/init.d/rapira.service.tpl'
        se_content = mw.readFile(systemServiceTpl)
        se_content = commonReplace(se_content, version)
        mw.writeFile(systemService, se_content)
        mw.execShell('systemctl daemon-reload')

    return file_bin


def phpOp(version, method):
    file = initReplace(version)

    current_os = mw.getOs()
    if current_os == "darwin":
        data = mw.execShell(file + ' ' + method)
        if data[1] == '':
            return 'ok'
        return data[1]

    if current_os.startswith("freebsd"):
        data = mw.execShell('service rapira' + version + ' ' + method)
        if data[1] == '':
            return 'ok'
        return data[1]

    data = mw.execShell('systemctl ' + method + ' rapira' + version)
    if data[1] == '':
        return 'ok'
    return data[1]


def start(version):
    return phpOp(version, 'start')


def stop(version):
    status = phpOp(version, 'stop')
    return status


def restart(version):
    return phpOp(version, 'restart')


def reload(version):
    return phpOp(version, 'reload')


def initdStatus(version):
    current_os = mw.getOs()
    if current_os == 'darwin':
        return "Apple Computer does not support"

    if current_os.startswith('freebsd'):
        initd_bin = getInitDFile(version)
        if os.path.exists(initd_bin):
            return 'ok'

    shell_cmd = 'systemctl status rapira' + version + ' | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'


def initdInstall(version):
    current_os = mw.getOs()
    if current_os == 'darwin':
        return "Apple Computer does not support"

    if current_os.startswith('freebsd'):
        import shutil
        source_bin = initReplace(version)
        initd_bin = getInitDFile(version)
        shutil.copyfile(source_bin, initd_bin)
        mw.execShell('chmod +x ' + initd_bin)
        return 'ok'

    mw.execShell('systemctl enable rapira' + version)
    return 'ok'


def initdUinstall(version):
    current_os = mw.getOs()
    if current_os == 'darwin':
        return "Apple Computer does not support"

    if current_os.startswith('freebsd'):
        initd_bin = getInitDFile(version)
        os.remove(initd_bin)
        return 'ok'

    mw.execShell('systemctl disable rapira' + version)
    return 'ok'


def rapiraLog(version):
    cmd = "journalctl -u rapira"+version+" -n 15 --no-pager"
    data = mw.execShell(cmd)
    return data[0]


def fpmSlowLog(version):
    return getServerDir() + '/' + version + '/var/log/www-slow.log'


def getPhpConfArgs(version):
    phpini = mw.readFile(getConf(version))
    data = tomllib.loads(phpini)
    return data

def getPhpConf(version):
    data = getPhpConfArgs(version)
    return mw.getJson(data)


def submitPhpConf(version):
    gets = ['display_errors', 'cgi.fix_pathinfo', 'date.timezone', 'short_open_tag',
            'asp_tags', 'max_execution_time', 'max_input_time', 'max_input_vars', 'memory_limit',
            'post_max_size', 'file_uploads', 'upload_max_filesize', 'max_file_uploads',
            'default_socket_timeout', 'error_reporting']
    args = getArgs()
    filename = getServerDir() + '/' + version + '/etc/php.ini'
    phpini = mw.readFile(filename)
    for g in gets:
        if g in args:
            rep = g + r'\s*=\s*(.+)\r?\n'
            val = g + ' = ' + args[g] + '\n'
            phpini = re.sub(rep, val, phpini)
    mw.writeFile(filename, phpini)
    # mw.execShell(getServerDir() + '/init.d/php' + version + ' reload')
    reload(version)
    return mw.returnJson(True, '设置成功')


def getLimitConf(version):
    fileini = getConf(version)
    phpini = mw.readFile(fileini)
    filefpm = getFpmConfFile(version)
    phpfpm = mw.readFile(filefpm)

    # print fileini, filefpm
    data = {}
    try:
        rep = r"upload_max_filesize\s*=\s*([0-9]+)M"
        tmp = re.search(rep, phpini).groups()
        data['max'] = tmp[0]
    except:
        data['max'] = '50'

    try:
        rep = r"request_terminate_timeout\s*=\s*([0-9]+)\n"
        tmp = re.search(rep, phpfpm).groups()
        data['maxTime'] = tmp[0]
    except:
        data['maxTime'] = 0

    try:
        rep = r"\n;*\s*cgi\.fix_pathinfo\s*=\s*([0-9]+)\s*\n"
        tmp = re.search(rep, phpini).groups()

        if tmp[0] == '1':
            data['pathinfo'] = True
        else:
            data['pathinfo'] = False
    except:
        data['pathinfo'] = False

    return mw.getJson(data)


def setMaxTime(version):
    args = getArgs()
    data = checkArgs(args, ['time'])
    if not data[0]:
        return data[1]

    time = args['time']
    if int(time) < 30 or int(time) > 86400:
        return mw.returnJson(False, '请填写30-86400间的值!')

    filefpm = getFpmConfFile(version)
    conf = mw.readFile(filefpm)
    rep = r"request_terminate_timeout\s*=\s*([0-9]+)\n"
    conf = re.sub(rep, "request_terminate_timeout = " + time + "\n", conf)
    mw.writeFile(filefpm, conf)

    fileini = getServerDir() + "/" + version + "/etc/php.ini"
    phpini = mw.readFile(fileini)
    rep = r"max_execution_time\s*=\s*([0-9]+)\r?\n"
    phpini = re.sub(rep, "max_execution_time = " + time + "\n", phpini)
    rep = r"max_input_time\s*=\s*([0-9]+)\r?\n"
    phpini = re.sub(rep, "max_input_time = " + time + "\n", phpini)
    mw.writeFile(fileini, phpini)
    return mw.returnJson(True, '设置成功!')


def setMaxSize(version):
    args = getArgs()
    data = checkArgs(args, ['max'])
    if not data[0]:
        return data[1]

    maxVal = args['max']
    if int(maxVal) < 2:
        return mw.returnJson(False, '上传大小限制不能小于2MB!')

    path = getConf(version)
    conf = mw.readFile(path)
    rep = r"\nupload_max_filesize\s*=\s*[0-9]+M"
    conf = re.sub(rep, u'\nupload_max_filesize = ' + maxVal + 'M', conf)
    rep = r"\npost_max_size\s*=\s*[0-9]+M"
    conf = re.sub(rep, u'\npost_max_size = ' + maxVal + 'M', conf)
    mw.writeFile(path, conf)

    msg = mw.getInfo('设置PHP-{1}最大上传大小为[{2}MB]!', (version, maxVal,))
    mw.writeLog('插件管理[PHP]', msg)
    return mw.returnJson(True, '设置成功!')


def getFpmConfig(version, pool = 'www'):
    args = getArgs()
    pool = 'www'
    if 'pool' in args:
        pool = args['pool']

    filefpm = getServerDir() + '/' + version + '/etc/php-fpm.d/'+pool+'.conf'
    conf = mw.readFile(filefpm)
    data = {}
    rep = r"\s*pm.max_children\s*=\s*([0-9]+)\s*"
    tmp = re.search(rep, conf).groups()
    data['max_children'] = tmp[0]

    rep = r"\s*pm.start_servers\s*=\s*([0-9]+)\s*"
    tmp = re.search(rep, conf).groups()
    data['start_servers'] = tmp[0]

    rep = r"\s*pm.min_spare_servers\s*=\s*([0-9]+)\s*"
    tmp = re.search(rep, conf).groups()
    data['min_spare_servers'] = tmp[0]

    rep = r"\s*pm.max_spare_servers \s*=\s*([0-9]+)\s*"
    tmp = re.search(rep, conf).groups()
    data['max_spare_servers'] = tmp[0]

    rep = r"\s*pm\s*=\s*(\w+)\s*"
    tmp = re.search(rep, conf).groups()
    data['pm'] = tmp[0]
    return mw.getJson(data)


def setFpmConfig(version):
    args = getArgs()
    # if not 'max' in args:
    #     return 'missing time args!'

    version = args['version']
    max_children = args['max_children']
    start_servers = args['start_servers']
    min_spare_servers = args['min_spare_servers']
    max_spare_servers = args['max_spare_servers']
    pm = args['pm']
    pool = args['pool']


    file = getServerDir() + '/' + version + '/etc/php-fpm.d/'+pool+'.conf'
    conf = mw.readFile(file)

    rep = r"\s*pm.max_children\s*=\s*([0-9]+)\s*"
    conf = re.sub(rep, "\npm.max_children = " + max_children, conf)

    rep = r"\s*pm.start_servers\s*=\s*([0-9]+)\s*"
    conf = re.sub(rep, "\npm.start_servers = " + start_servers, conf)

    rep = r"\s*pm.min_spare_servers\s*=\s*([0-9]+)\s*"
    conf = re.sub(rep, "\npm.min_spare_servers = " +
                  min_spare_servers, conf)

    rep = r"\s*pm.max_spare_servers \s*=\s*([0-9]+)\s*"
    conf = re.sub(rep, "\npm.max_spare_servers = " +
                  max_spare_servers + "\n", conf)

    rep = r"\s*pm\s*=\s*(\w+)\s*"
    conf = re.sub(rep, "\npm = " + pm + "\n", conf)

    mw.writeFile(file, conf)
    reload(version)

    msg = mw.getInfo('设置PHP-{1}并发设置,max_children={2},start_servers={3},min_spare_servers={4},max_spare_servers={5}', (version, max_children,
                                                                                                                      start_servers, min_spare_servers, max_spare_servers,))
    mw.writeLog('插件管理[PHP]', msg)
    return mw.returnJson(True, '设置成功!')


# def checkFpmStatusFile(version):
#     if not mw.isInstalledWeb():
#         return False

#     dfile = getServerDir() + '/nginx/conf/php_status/phpfpm_status_' + version + '.conf'
#     if not os.path.exists(dfile):
#         tpl = getPluginDir() + '/conf/phpfpm_status.conf'
#         content = mw.readFile(tpl)
#         content = contentReplace(content, version)
#         mw.writeFile(dfile, content)
#         mw.restartWeb()
#     return True


def getRapiraAddress(version):
    data = getPhpConfArgs(version)
    return data["observability"]["listen"]


def getRapiraStatus(version):
    stat = status(version)
    if stat == 'stop':
        return mw.returnJson(False, 'rapira[' + version + ']未启动!!!')

    args = getArgs()
    addr = getRapiraAddress(version)
    data = mw.httpGet("http://"+addr+"/metrics")
    return data


def getSessionConf(version):
    filename = getConf(version)
    if not os.path.exists(filename):
        return mw.returnJson(False, '指定PHP版本不存在!')

    phpini = mw.readFile(filename)

    rep = r'session.save_handler\s*=\s*([0-9A-Za-z_& ~]+)(\s*;?|\r?\n)'
    save_handler = re.search(rep, phpini)
    if save_handler:
        save_handler = save_handler.group(1)
    else:
        save_handler = "files"

    reppath = r'\nsession.save_path\s*=\s*"tcp\:\/\/([\d\.]+):(\d+).*\r?\n'
    passrep = r'\nsession.save_path\s*=\s*"tcp://[\w\.\?\:]+=(.*)"\r?\n'
    memcached = r'\nsession.save_path\s*=\s*"([\d\.]+):(\d+)"'
    save_path = re.search(reppath, phpini)
    if not save_path:
        save_path = re.search(memcached, phpini)
    passwd = re.search(passrep, phpini)
    port = ""
    if passwd:
        passwd = passwd.group(1)
    else:
        passwd = ""
    if save_path:
        port = save_path.group(2)
        save_path = save_path.group(1)

    else:
        save_path = ""

    data = {"save_handler": save_handler, "save_path": save_path,
            "passwd": passwd, "port": port}
    return mw.returnJson(True, 'ok', data)


def setSessionConf(version):

    args = getArgs()

    ip = args['ip']
    port = args['port']
    passwd = args['passwd']
    save_handler = args['save_handler']

    if save_handler != "files":
        iprep = r"(2(5[0-5]{1}|[0-4]\d{1})|[0-1]?\d{1,2})\.(2(5[0-5]{1}|[0-4]\d{1})|[0-1]?\d{1,2})\.(2(5[0-5]{1}|[0-4]\d{1})|[0-1]?\d{1,2})\.(2(5[0-5]{1}|[0-4]\d{1})|[0-1]?\d{1,2})"
        if not re.search(iprep, ip):
            return mw.returnJson(False, '请输入正确的IP地址')

        try:
            port = int(port)
            if port >= 65535 or port < 1:
                return mw.returnJson(False, '请输入正确的端口号')
        except:
            return mw.returnJson(False, '请输入正确的端口号')
        prep = r"[\~\`\/\=]"
        if re.search(prep, passwd):
            return mw.returnJson(False, '请不要输入以下特殊字符 " ~ ` / = "')

    filename = getConf(version)
    if not os.path.exists(filename):
        return mw.returnJson(False, '指定PHP版本不存在!')
    phpini = mw.readFile(filename)

    session_tmp = getServerDir() + "/tmp/session"

    rep = r'session.save_handler\s*=\s*(.+)\r?\n'
    val = r'session.save_handler = ' + save_handler + '\n'
    phpini = re.sub(rep, val, phpini)

    if save_handler == "memcached":
        if not re.search("memcached.so", phpini):
            return mw.returnJson(False, '请先安装%s扩展' % save_handler)
        rep = r'\nsession.save_path\s*=\s*(.+)\r?\n'
        val = r'\nsession.save_path = "%s:%s" \n' % (ip, port)
        if re.search(rep, phpini):
            phpini = re.sub(rep, val, phpini)
        else:
            phpini = re.sub('\n;session.save_path = "' + session_tmp + '"',
                            '\n;session.save_path = "' + session_tmp + '"' + val, phpini)

    if save_handler == "memcache":
        if not re.search("memcache.so", phpini):
            return mw.returnJson(False, '请先安装%s扩展' % save_handler)
        rep = r'\nsession.save_path\s*=\s*(.+)\r?\n'
        val = r'\nsession.save_path = "%s:%s" \n' % (ip, port)
        if re.search(rep, phpini):
            phpini = re.sub(rep, val, phpini)
        else:
            phpini = re.sub('\n;session.save_path = "' + session_tmp + '"',
                            '\n;session.save_path = "' + session_tmp + '"' + val, phpini)

    if save_handler == "redis":
        if not re.search("redis.so", phpini):
            return mw.returnJson(False, '请先安装%s扩展' % save_handler)
        if passwd:
            passwd = "?auth=" + passwd
        else:
            passwd = ""
        rep = r'\nsession.save_path\s*=\s*(.+)\r?\n'
        val = r'\nsession.save_path = "tcp://%s:%s%s"\n' % (ip, port, passwd)
        res = re.search(rep, phpini)
        if res:
            phpini = re.sub(rep, val, phpini)
        else:
            phpini = re.sub('\n;session.save_path = "' + session_tmp + '"',
                            '\n;session.save_path = "' + session_tmp + '"' + val, phpini)

    if save_handler == "files":
        rep = r'\nsession.save_path\s*=\s*(.+)\r?\n'
        val = r'\nsession.save_path = "' + session_tmp + '"\n'
        if re.search(rep, phpini):
            phpini = re.sub(rep, val, phpini)
        else:
            phpini = re.sub('\n;session.save_path = "' + session_tmp + '"',
                            '\n;session.save_path = "' + session_tmp + '"' + val, phpini)

    mw.writeFile(filename, phpini)
    reload(version)
    return mw.returnJson(True, '设置成功!')


def getSessionCount_Origin(version):
    session_tmp = getServerDir() + "/tmp/session"
    d = [session_tmp]
    count = 0
    for i in d:
        if not os.path.exists(i):
            mw.execShell('mkdir -p %s' % i)
        list = os.listdir(i)
        for l in list:
            if os.path.isdir(i + "/" + l):
                l1 = os.listdir(i + "/" + l)
                for ll in l1:
                    if "sess_" in ll:
                        count += 1
                continue
            if "sess_" in l:
                count += 1

    s = "find /tmp -mtime +1 |grep 'sess_' | wc -l"
    old_file = int(mw.execShell(s)[0].split("\n")[0])

    s = "find " + session_tmp + " -mtime +1 |grep 'sess_'|wc -l"
    old_file += int(mw.execShell(s)[0].split("\n")[0])
    return {"total": count, "oldfile": old_file}


def getSessionCount(version):
    data = getSessionCount_Origin(version)
    return mw.returnJson(True, 'ok!', data)


def cleanSessionOld(version):
    s = "find /tmp -mtime +1 |grep 'sess_'|xargs rm -f"
    mw.execShell(s)

    session_tmp = getServerDir() + "/tmp/session"
    s = "find " + session_tmp + " -mtime +1 |grep 'sess_' |xargs rm -f"
    mw.execShell(s)
    old_file_conf = getSessionCount_Origin(version)["oldfile"]
    if old_file_conf == 0:
        return mw.returnJson(True, '清理成功')
    else:
        return mw.returnJson(True, '清理失败')


def getDisableFunc(version):
    filename = getConf(version)
    if not os.path.exists(filename):
        return mw.returnJson(False, '指定PHP版本不存在!')

    phpini = mw.readFile(filename)
    data = {}
    rep = r"disable_functions\s*=\s{0,1}(.*)\n"
    tmp = re.search(rep, phpini).groups()
    data['disable_functions'] = tmp[0]
    return mw.getJson(data)


def setDisableFunc(version):
    filename = getConf(version)
    if not os.path.exists(filename):
        return mw.returnJson(False, '指定PHP版本不存在!')

    args = getArgs()
    disable_functions = args['disable_functions']

    phpini = mw.readFile(filename)
    rep = r"disable_functions\s*=\s*.*\n"
    phpini = re.sub(rep, 'disable_functions = ' +
                    disable_functions + "\n", phpini)

    msg = mw.getInfo('修改PHP-{1}的禁用函数为[{2}]', (version, disable_functions,))
    mw.writeLog('插件管理[PHP]', msg)
    mw.writeFile(filename, phpini)
    reload(version)
    return mw.returnJson(True, '设置成功!')


def getPhpinfo(version):
    stat = status(version)
    if stat == 'stop':
        return 'PHP[' + version + ']未启动,不可访问!!!'

    sock_file = getFpmAddress(version)
    root_dir = mw.getFatherDir() + '/phpinfo'

    mw.execShell("rm -rf " + root_dir)
    mw.execShell("mkdir -p " + root_dir)
    mw.writeFile(root_dir + '/phpinfo.php', '<?php phpinfo(); ?>')
    sock_data = mw.requestFcgiPHP(sock_file, '/phpinfo.php', root_dir)
    os.system("rm -rf " + root_dir)
    phpinfo = str(sock_data, encoding='utf-8')
    return phpinfo


def get_php_info(args):
    return getPhpinfo(args['version'])


def libConfCommon(version):
    fname = getConf(version)
    if not os.path.exists(fname):
        return mw.returnJson(False, '指定PHP版本不存在!')

    phpini = mw.readFile(fname)

    libpath = getPluginDir() + '/versions/phplib.conf'
    phplib = json.loads(mw.readFile(libpath))

    libs = []
    tasks = mw.M('tasks').where("status!=?", ('1',)).field('status,name').select()
    for lib in phplib:
        lib['task'] = '1'
        for task in tasks:
            tmp = mw.getStrBetween('[', ']', task['name'])
            if not tmp:
                continue
            tmp1 = tmp.split('-')
            if tmp1[0].lower() == lib['name'].lower():
                lib['task'] = task['status']
                lib['phpversions'] = []
                lib['phpversions'].append(tmp1[1])
        if phpini.find(lib['check']) == -1:
            lib['status'] = False
        else:
            lib['status'] = True
        libs.append(lib)
    return libs


def get_lib_conf(data):
    libs = libConfCommon(data['version'])
    # print(libs)
    return mw.returnData(True, 'OK!', libs)


def getLibConf(version):
    libs = libConfCommon(version)
    return mw.returnJson(True, 'OK!', libs)


def installLib(version):
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    name = args['name']
    cmd = "cd " + getPluginDir() + "/versions && /bin/bash  common.sh " + version + ' install ' + name
    install_name = '安装[' + name + '-' + version + ']'
    import thisdb
    thisdb.addTask(name=install_name,cmd=cmd)

    mw.triggerTask()
    return mw.returnJson(True, '已将下载任务添加到队列!')


def uninstallLib(version):
    args = getArgs()
    data = checkArgs(args, ['name'])
    if not data[0]:
        return data[1]

    name = args['name']
    execstr = "cd " + getPluginDir() + "/versions && /bin/bash  common.sh " + version + ' uninstall ' + name

    data = mw.execShell(execstr)
    # data[0] == '' and
    if data[1] == '':
        return mw.returnJson(True, '已经卸载成功!')
    else:
        return mw.returnJson(False, '卸载信息![通道0]:' + data[0] + "[通道0]:" + data[1])


def getConfAppStart():
    pstart = mw.getServerDir() + '/php/app_start.php'
    return pstart

def opcacheBlacklistFile():
    op_bl = mw.getServerDir() + '/php/opcache-blacklist.txt'
    return op_bl


def installPreInspection(version):
    sys = mw.execShell(
        "cat /etc/*-release | grep PRETTY_NAME |awk -F = '{print $2}' | awk -F '\"' '{print $2}'| awk '{print $1}'")
    if sys[1] != '':
        return '不支持改系统'

    sys_id = mw.execShell(
        "cat /etc/*-release | grep VERSION_ID | awk -F = '{print $2}' | awk -F '\"' '{print $2}'")

    sysName = sys[0].strip().lower()
    sysId = sys_id[0].strip()
    return 'ok'


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print('missing parameters')
        exit(0)

    func = sys.argv[1]
    version = sys.argv[2]

    if func == 'status':
        print(status(version))
    elif func == 'start':
        print(start(version))
    elif func == 'stop':
        print(stop(version))
    elif func == 'restart':
        print(restart(version))
    elif func == 'reload':
        print(reload(version))
    elif func == 'install_pre_inspection':
        print(installPreInspection(version))
    elif func == 'initd_status':
        print(initdStatus(version))
    elif func == 'initd_install':
        print(initdInstall(version))
    elif func == 'initd_uninstall':
        print(initdUinstall(version))
    elif func == 'rapira_log':
        print(rapiraLog(version))
    elif func == 'fpm_slow_log':
        print(fpmSlowLog(version))
    elif func == 'conf':
        print(getConf(version))
    elif func == 'app_start':
        print(getConfAppStart())
    elif func == 'opcache_blacklist_file':
        print(opcacheBlacklistFile())
    elif func == 'get_php_conf':
        print(getPhpConf(version))
    elif func == 'get_fpm_conf_file':
        print(getFpmConfFile(version))
    elif func == 'get_fpm_file':
        print(getFpmFile(version))
    elif func == 'submit_php_conf':
        print(submitPhpConf(version))
    elif func == 'get_limit_conf':
        print(getLimitConf(version))
    elif func == 'set_max_time':
        print(setMaxTime(version))
    elif func == 'set_max_size':
        print(setMaxSize(version))
    elif func == 'get_fpm_conf':
        print(getFpmConfig(version))
    elif func == 'set_fpm_conf':
        print(setFpmConfig(version))
    elif func == 'get_rapira_status':
        print(getRapiraStatus(version))
    elif func == 'get_session_conf':
        print(getSessionConf(version))
    elif func == 'set_session_conf':
        print(setSessionConf(version))
    elif func == 'get_session_count':
        print(getSessionCount(version))
    elif func == 'clean_session_old':
        print(cleanSessionOld(version))
    elif func == 'get_disable_func':
        print(getDisableFunc(version))
    elif func == 'set_disable_func':
        print(setDisableFunc(version))
    elif func == 'get_phpinfo':
        print(getPhpinfo(version))
    elif func == 'get_lib_conf':
        print(getLibConf(version))
    elif func == 'install_lib':
        print(installLib(version))
    elif func == 'uninstall_lib':
        print(uninstallLib(version))
    else:
        print("fail")
