# coding:utf-8

import sys
import io
import os
import time
import re
import json
import shutil

# reload(sys)
# sys.setdefaultencoding('utf8')

sys.path.append(os.getcwd() + "/class/core")
import mw

if mw.isAppleSystem():
    cmd = 'ls /usr/local/lib/ | grep python  | cut -d \\  -f 1 | awk \'END {print}\''
    info = mw.execShell(cmd)
    p = "/usr/local/lib/" + info[0].strip() + "/site-packages"
    sys.path.append(p)

app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'php'


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


def getConf(version):
    path = getServerDir() + '/' + version + '/etc/php.ini'
    return path


def getFpmConfFile(version):
    return getServerDir() + '/' + version + '/etc/php-fpm.d/www.conf'


def status_progress(version):
    # ps -ef|grep 'php/81' |grep -v grep | grep -v python | awk '{print $2}
    cmd = "ps aux|grep 'php/" + version + \
        "' |grep -v grep | grep -v python | awk '{print $2}'"
    data = mw.execShell(cmd)
    if data[0] == '':
        return 'stop'
    return 'start'


def getPhpSocket(version):
    path = getFpmConfFile(version)
    content = mw.readFile(path)
    rep = 'listen\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def status(version):
    '''
    sock文件判断是否启动
    '''
    sock = getPhpSocket(version)
    if sock.find(':'):
        return status_progress(version)

    if not os.path.exists(sock):
        return 'stop'
    return 'start'


def contentReplace(content, version):
    service_path = mw.getServerDir()
    content = content.replace('{$ROOT_PATH}', mw.getRootDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$PHP_VERSION}', version)
    content = content.replace('{$LOCAL_IP}', mw.getLocalIp())
    content = content.replace('{$SSL_CRT}', mw.getSslCrt())

    if mw.isAppleSystem():
        # user = mw.execShell(
        #     "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
        content = content.replace('{$PHP_USER}', 'nobody')
        content = content.replace('{$PHP_GROUP}', 'nobody')

        rep = 'listen.owner\s*=\s*(.+)\r?\n'
        val = ';listen.owner = nobody\n'
        content = re.sub(rep, val, content)

        rep = 'listen.group\s*=\s*(.+)\r?\n'
        val = ';listen.group = nobody\n'
        content = re.sub(rep, val, content)

        rep = 'user\s*=\s*(.+)\r?\n'
        val = ';user = nobody\n'
        content = re.sub(rep, val, content)

        rep = r'[^\.]group\s*=\s*(.+)\r?\n'
        val = ';group = nobody\n'
        content = re.sub(rep, val, content)

    else:
        content = content.replace('{$PHP_USER}', 'www')
        content = content.replace('{$PHP_GROUP}', 'www')
    return content


def makeOpenrestyConf():
    phpversions = ['00', '52', '53', '54', '55', '56',
                   '70', '71', '72', '73', '74', '80', '81', '82', '83']

    sdir = mw.getServerDir()

    dst_dir = sdir + '/web_conf/php'
    dst_dir_conf = sdir + '/web_conf/php/conf'
    if not os.path.exists(dst_dir):
        mw.execShell('mkdir -p ' + dst_dir)

    if not os.path.exists(dst_dir_conf):
        mw.execShell('mkdir -p ' + dst_dir_conf)

    d_pathinfo = sdir + '/web_conf/php/pathinfo.conf'
    if not os.path.exists(d_pathinfo):
        s_pathinfo = getPluginDir() + '/conf/pathinfo.conf'
        shutil.copyfile(s_pathinfo, d_pathinfo)

    info = getPluginDir() + '/info.json'
    content = mw.readFile(info)
    content = json.loads(content)
    versions = content['versions']
    tpl = getPluginDir() + '/conf/enable-php.conf'
    tpl_content = mw.readFile(tpl)
    for x in phpversions:
        dfile = sdir + '/web_conf/php/conf/enable-php-' + x + '.conf'
        if not os.path.exists(dfile):
            if x == '00':
                mw.writeFile(dfile, 'set $PHP_ENV 0;')
            else:
                w_content = contentReplace(tpl_content, x)
                mw.writeFile(dfile, w_content)


def phpPrependFile(version):
    app_start = getServerDir() + '/app_start.php'
    if not os.path.exists(app_start):
        tpl = getPluginDir() + '/conf/app_start.php'
        content = mw.readFile(tpl)
        content = contentReplace(content, version)
        mw.writeFile(app_start, content)


def phpFpmReplace(version):
    desc_php_fpm = getServerDir() + '/' + version + '/etc/php-fpm.conf'
    if not os.path.exists(desc_php_fpm):
        tpl_php_fpm = getPluginDir() + '/conf/php-fpm.conf'
        content = mw.readFile(tpl_php_fpm)
        content = contentReplace(content, version)
        mw.writeFile(desc_php_fpm, content)
    else:
        if version == '52':
            tpl_php_fpm = tpl_php_fpm = getPluginDir() + '/conf/php-fpm-52.conf'
            content = mw.readFile(tpl_php_fpm)
            mw.writeFile(desc_php_fpm, content)


def phpFpmWwwReplace(version):
    service_php_fpm_dir = getServerDir() + '/' + version + '/etc/php-fpm.d/'

    if not os.path.exists(service_php_fpm_dir):
        os.mkdir(service_php_fpm_dir)

    service_php_fpmwww = service_php_fpm_dir + '/www.conf'
    if not os.path.exists(service_php_fpmwww):
        tpl_php_fpmwww = getPluginDir() + '/conf/www.conf'
        content = mw.readFile(tpl_php_fpmwww)
        content = contentReplace(content, version)
        mw.writeFile(service_php_fpmwww, content)


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


def initReplace(version):
    makeOpenrestyConf()
    makePhpIni(version)

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)

    file_bin = initD_path + '/php' + version
    if not os.path.exists(file_bin):
        file_tpl = getPluginDir() + '/init.d/php.tpl'

        if version == '52':
            file_tpl = getPluginDir() + '/init.d/php52.tpl'

        content = mw.readFile(file_tpl)
        content = contentReplace(content, version)

        mw.writeFile(file_bin, content)
        mw.execShell('chmod +x ' + file_bin)

    phpPrependFile(version)
    phpFpmWwwReplace(version)
    phpFpmReplace(version)

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
    systemService = systemDir + '/php' + version + '.service'

    if os.path.exists(systemDir) and not os.path.exists(systemService):
        systemServiceTpl = getPluginDir() + '/init.d/php.service.tpl'
        if version == '52':
            systemServiceTpl = getPluginDir() + '/init.d/php.service.52.tpl'
        service_path = mw.getServerDir()
        se_content = mw.readFile(systemServiceTpl)
        se_content = se_content.replace('{$VERSION}', version)
        se_content = se_content.replace('{$SERVER_PATH}', service_path)
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
        data = mw.execShell('service php' + version + ' ' + method)
        if data[1] == '':
            return 'ok'
        return data[1]

    if method == 'stop' or method == 'restart':
        mw.execShell(file + ' ' + 'stop')

    data = mw.execShell('systemctl ' + method + ' php' + version)
    if data[1] == '':
        return 'ok'
    return data[1]


def getFpmAddress(version):
    fpm_address = '/tmp/php-cgi-{}.sock'.format(version)
    php_fpm_file = getFpmConfFile(version)
    try:
        content = readFile(php_fpm_file)
        tmp = re.findall(r"listen\s*=\s*(.+)", content)
        if not tmp:
            return fpm_address
        if tmp[0].find('sock') != -1:
            return fpm_address
        if tmp[0].find(':') != -1:
            listen_tmp = tmp[0].split(':')
            if bind:
                fpm_address = (listen_tmp[0], int(listen_tmp[1]))
            else:
                fpm_address = ('127.0.0.1', int(listen_tmp[1]))
        else:
            fpm_address = ('127.0.0.1', int(tmp[0]))
        return fpm_address
    except:
        return fpm_address


def getPhpinfo(version):
    stat = status(version)
    if stat == 'stop':
        return 'PHP[' + version + ']未启动,不可访问!!!'

    sock_file = getFpmAddress(version)
    root_dir = mw.getRootDir() + '/phpinfo'

    mw.execShell("rm -rf " + root_dir)
    mw.execShell("mkdir -p " + root_dir)
    mw.writeFile(root_dir + '/phpinfo.php', '<?php phpinfo(); ?>')
    sock_data = mw.requestFcgiPHP(sock_file, '/phpinfo.php', root_dir)
    os.system("rm -rf " + root_dir)
    phpinfo = str(sock_data, encoding='utf-8')
    return phpinfo


def libConfCommon(version):
    fname = getConf(version)
    if not os.path.exists(fname):
        return mw.returnJson(False, '指定PHP版本不存在!')

    phpini = mw.readFile(fname)

    libpath = getPluginDir() + '/versions/phplib.conf'
    phplib = json.loads(mw.readFile(libpath))

    libs = []
    tasks = mw.M('tasks').where(
        "status!=?", ('1',)).field('status,name').select()
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


def get_php_info(args):
    return getPhpinfo(args['version'])


def get_lib_conf(data):
    libs = libConfCommon(data['version'])
    return mw.returnData(True, 'OK!', libs)
