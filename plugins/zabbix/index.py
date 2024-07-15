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
    return 'zabbix'


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


def getConf():
    path = getServerDir() + "/redis.conf"
    return path


def getConfTpl():
    path = getPluginDir() + "/config/redis.conf"
    return path


def getInitDTpl():
    path = getPluginDir() + "/init.d/" + getPluginName() + ".tpl"
    return path


def getArgs():
    args = sys.argv[3:]
    tmp = {}
    args_len = len(args)

    if args_len == 1:
        t = args[0].strip('{').strip('}')
        if t.strip() == '':
            tmp = []
        else:
            t = t.split(':')
            tmp[t[0]] = t[1]
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

def configTpl():
    path = getPluginDir() + '/tpl'
    pathFile = os.listdir(path)
    tmp = []
    for one in pathFile:
        file = path + '/' + one
        tmp.append(file)
    return mw.getJson(tmp)


def readConfigTpl():
    args = getArgs()
    data = checkArgs(args, ['file'])
    if not data[0]:
        return data[1]

    content = mw.readFile(args['file'])
    content = contentReplace(content)
    return mw.returnJson(True, 'ok', content)

def getPidFile():
    file = getConf()
    content = mw.readFile(file)
    rep = 'pidfile\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()

def status():
    cmd = "ps aux|grep zabbix-server |grep -v grep | grep -v python | grep -v mdserver-web | awk '{print $2}'"
    data = mw.execShell(cmd)
    if data[0] == '':
        return 'stop'
    return 'start'

def contentReplace(content):
    service_path = mw.getServerDir()
    content = content.replace('{$ROOT_PATH}', mw.getRootDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$ZABBIX_ROOT}', '/usr/share/zabbix')
    content = content.replace('{$ZABBIX_PORT}', '18888')
    return content


def getMySQLConf():
    path = mw.getServerDir() + '/mysql/etc/my.cnf'
    return path


def getMySQLPort():
    file = getMySQLConf()
    content = mw.readFile(file)
    rep = 'port\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()

def getMySQLSocketFile():
    file = getMySQLConf()
    content = mw.readFile(file)
    rep = 'socket\s*=\s*(.*)'
    tmp = re.search(rep, content)
    return tmp.groups()[0].strip()


def pSqliteDb(dbname='databases'):
    mysql_dir = mw.getServerDir() + '/mysql'
    conn = mw.M(dbname).dbPos(mysql_dir, 'mysql')
    return conn


def pMysqlDb():
    # pymysql
    db = mw.getMyORM()
    db.setPort(getMySQLPort())
    db.setSocket(getMySQLSocketFile())
    db.setPwd(pSqliteDb('config').where('id=?', (1,)).getField('mysql_root'))
    return db

def zabbixNginxConf():
    return mw.getServerDir()+'/web_conf/nginx/vhost/zabbix.conf'


def zabbixImportMySQLData():

    psdb = pSqliteDb('databases')
    find_ps_zabbix = psdb.field('id').where('name = ?', ('zabbix',)).select()
    if len(find_ps_zabbix) > 0:
        return True

    db_pass = mw.getRandomString(16)

    # 创建数据
    cmd = 'python3 plugins/mysql/index.py add_db  {"name":"zabbix","codeing":"utf8mb4","db_user":"zabbix","password":"'+getRandomString+'","dataAccess":"127.0.0.1","ps":"zabbix","address":"127.0.0.1"}'
    mw.execShell(cmd)

    # 初始化导入数据
    # zcat /usr/share/zabbix-sql-scripts/mysql/server.sql.gz | /www/server/mysql/bin/mysql --default-character-set=utf8mb4 -uzabbix -p"4sPhWWwL7zcDyLX5" zabbix
    # service zabbix-server start



    return True

def initDreplace():
    nginx_src_tpl = getPluginDir()+'/conf/zabbix.nginx.conf'
    nginx_dst_vhost = zabbixNginxConf()

    # nginx配置
    if not os.path.exists(nginx_dst_vhost):
        content = mw.readFile(nginx_src_tpl)
        content = contentReplace(content)
        mw.writeFile(nginx_dst_vhost, content)
    # 导入MySQL配置
    zabbixImportMySQLData()
    return True


def zOp(method):

    initDreplace()

    current_os = mw.getOs()
    if current_os.startswith("freebsd"):
        data = mw.execShell('service ' + getPluginName() + ' ' + method)
        if data[1] == '':
            return 'ok'
        return data[1]

    data = mw.execShell('systemctl ' + method + ' ' + getPluginName())
    if data[1] == '':
        return 'ok'
    return data[1]


def start():
    return zOp('start')


def stop():
    val = zOp('stop')
    return val

def restart():
    status = zOp('restart')
    return status

def reload():
    return zOp('reload')

def initdStatus():
    current_os = mw.getOs()
    if current_os == 'darwin':
        return "Apple Computer does not support"

    if current_os.startswith('freebsd'):
        initd_bin = getInitDFile()
        if os.path.exists(initd_bin):
            return 'ok'

    shell_cmd = 'systemctl status ' + \
        getPluginName() + ' | grep loaded | grep "enabled;"'
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

    mw.execShell('systemctl enable ' + getPluginName())
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

    mw.execShell('systemctl disable ' + getPluginName())
    return 'ok'


def installPreInspection():
    openresty_dir = mw.getServerDir() + "/openresty"
    if not os.path.exists(openresty_dir):
        return '需要安装Openresty插件'

    mysql_dir = mw.getServerDir() + "/mysql"
    if not os.path.exists(mysql_dir):
        return '需要安装MySQL插件,至少8.0!'

    return 'ok'


def uninstallPreInspection():
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
    elif func == 'uninstall_pre_inspection':
        print(uninstallPreInspection())
    elif func == 'conf':
        print(getConf())
    elif func == 'run_log':
        print(runLog())
    elif func == 'config_tpl':
        print(configTpl())
    else:
        print('error')
