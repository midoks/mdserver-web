# coding: utf-8

import sys
import os
import json
import time

sys.path.append(os.getcwd() + "/class/core")
import mw
import db

cmd = 'ls /usr/local/lib/ | grep python  | cut -d \\  -f 1 | awk \'END {print}\''
info = mw.execShell(cmd)
p = "/usr/local/lib/" + info[0].strip() + "/site-packages"
sys.path.append(p)


def set_mysql_root(password):
    # 设置MySQL密码
    import db
    import os
    sql = db.Sql()

    root_mysql = '''#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
pwd=$1
${server}/init.d/mysql stop
${server}/bin/mysqld_safe --skip-grant-tables&
echo '正在修改密码...';
echo 'The set password...';
sleep 6
m_version=$(cat ${server}/version.pl|grep -E "(5.1.|5.5.|5.6.|mariadb)")
if [ "$m_version" != "" ];then
    ${server}/bin/mysql -uroot -e "insert into mysql.user(Select_priv,Insert_priv,Update_priv,Delete_priv,Create_priv,Drop_priv,Reload_priv,Shutdown_priv,Process_priv,File_priv,Grant_priv,References_priv,Index_priv,Alter_priv,Show_db_priv,Super_priv,Create_tmp_table_priv,Lock_tables_priv,Execute_priv,Repl_slave_priv,Repl_client_priv,Create_view_priv,Show_view_priv,Create_routine_priv,Alter_routine_priv,Create_user_priv,Event_priv,Trigger_priv,Create_tablespace_priv,User,Password,host)values('Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','root',password('${pwd}'),'127.0.0.1')"
    ${server}/bin/mysql -uroot -e "insert into mysql.user(Select_priv,Insert_priv,Update_priv,Delete_priv,Create_priv,Drop_priv,Reload_priv,Shutdown_priv,Process_priv,File_priv,Grant_priv,References_priv,Index_priv,Alter_priv,Show_db_priv,Super_priv,Create_tmp_table_priv,Lock_tables_priv,Execute_priv,Repl_slave_priv,Repl_client_priv,Create_view_priv,Show_view_priv,Create_routine_priv,Alter_routine_priv,Create_user_priv,Event_priv,Trigger_priv,Create_tablespace_priv,User,Password,host)values('Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','Y','root',password('${pwd}'),'localhost')"
    ${server}/bin/mysql -uroot -e "UPDATE mysql.user SET password=PASSWORD('${pwd}') WHERE user='root'";
else
    ${server}/bin/mysql -uroot -e "UPDATE mysql.user SET authentication_string='' WHERE user='root'";
    ${server}/bin/mysql -uroot -e "FLUSH PRIVILEGES";
    ${server}/bin/mysql -uroot -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '${pwd}';";
fi
${server} -uroot -e "FLUSH PRIVILEGES";
pkill -9 mysqld_safe
pkill -9 mysqld
sleep 2
${server}/init.d/mysql start

echo '==========================================='
echo "root密码成功修改为: ${pwd}"
echo "The root password set ${pwd}  successuful"'''

    server = mw.getServerDir() + '/mysql'
    root_mysql = root_mysql.replace('${server}', server)
    mw.writeFile('mysql_root.sh', root_mysql)
    os.system("/bin/bash mysql_root.sh " + password)
    os.system("rm -f mysql_root.sh")

    pos = mw.getServerDir() + '/mysql'
    result = sql.table('config').dbPos(pos, 'mysql').where(
        'id=?', (1,)).setField('mysql_root', password)


def set_panel_pwd(password, ncli=False):
    # 设置面板密码
    import db
    sql = db.Sql()
    result = sql.table('users').where('id=?', (1,)).setField(
        'password', mw.md5(password))
    username = sql.table('users').where('id=?', (1,)).getField('username')
    if ncli:
        print("|-用户名: " + username)
        print("|-新密码: " + password)
    else:
        print(username)


def set_panel_username(username=None):
    # 随机面板用户名
    import db
    sql = db.Sql()
    if username:
        if len(username) < 5:
            print("|-错误，用户名长度不能少于5位")
            return
        if username in ['admin', 'root']:
            print("|-错误，不能使用过于简单的用户名")
            return

        sql.table('users').where('id=?', (1,)).setField('username', username)
        print("|-新用户名: %s" % username)
        return

    username = sql.table('users').where('id=?', (1,)).getField('username')
    if username == 'admin':
        username = mw.getRandomString(8).lower()
        sql.table('users').where('id=?', (1,)).setField('username', username)
    print('username: ' + username)


def getServerIp():
    version = sys.argv[2]
    ip = mw.execShell(
        "curl -{} -sS --connect-timeout 5 -m 60 https://v6r.ipip.net/?format=text".format(version))
    print(ip[0])


if __name__ == "__main__":
    type = sys.argv[1]
    if type == 'root':
        set_mysql_root(sys.argv[2])
    elif type == 'panel':
        set_panel_pwd(sys.argv[2])
    elif type == 'username':
        set_panel_username()
    elif type == 'getServerIp':
        getServerIp()
    else:
        print('ERROR: Parameter error')
