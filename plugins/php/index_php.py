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
