# coding:utf-8

import sys
import io
import os
import time
import re
import json
import shutil

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


def getConf(version):
    path = getServerDir() + '/' + version + '/rapira.toml'
    return path

def getConfIni(version):
    path = getServerDir() + '/' + version + '/php.ini'
    return path


def status_progress(version):
    # ps -ef|grep 'php/81' |grep -v grep | grep -v python | awk '{print $2}
    cmd = "ps -ef|grep 'rapira/" + version + \
        "' |grep -v grep | grep -v python | awk '{print $2}'"
    data = mw.execShell(cmd)
    if data[0] == '':
        return 'stop'
    return 'start'


def status(version):
    '''
    sock文件判断是否启动
    '''
    return status_progress(version)

def getPhpinfo(version):
    stat = status(version)
    if stat == 'stop':
        return 'PHP[' + version + ']未启动,不可访问!!!'

    php_path = getServerDir() + "/" + version + "/link/bin/php"
    php_ini = getConfIni(version)
    php_path = php_path + " -c " + php_ini
    cmd = php_path + " -d display_startup_errors=0 -r 'phpinfo();' 2>/dev/null"
    cmd_data = mw.execShell(cmd)
    return cmd_data[0]


def libConfCommon(version):
    fname = getConfIni(version)
    if not os.path.exists(fname):
        return mw.returnJson(False, '指定PHP版本不存在!')

    phpini = mw.readFile(fname)

    libpath = getPluginDir() + '/versions/phplib.conf'
    phplib = json.loads(mw.readFile(libpath))

    php_dir = getServerDir() + "/" + version
    ext_dir = php_dir+"/link/lib/php/extensions"
    
    ext_list = os.listdir(ext_dir)
    for sodir in ext_list:
        if sodir.find("no-debug-non-zts") > -1:
            ext_dir += "/"+ sodir
            break

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

        lib['status'] = False
        if phpini.find(lib['check']) > -1:
            lib['status'] = True
        sofile = ext_dir+"/"+lib['check']
        # 自定义，比较特殊的方式
        if os.path.exists(sofile):
            if os.path.getsize(sofile) == 7:
                lib['status'] = True
        libs.append(lib)
    return libs


def get_php_info(args):
    return getPhpinfo(args['version'])


def get_lib_conf(data):
    libs = libConfCommon(data['version'])
    return mw.returnData(True, 'OK!', libs)
