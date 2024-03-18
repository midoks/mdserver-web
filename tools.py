# coding: utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------
# 工具箱
# ---------------------------------------------------------------------------------


import sys
import os
import json
import time
import re

sys.path.append(os.getcwd() + "/class/core")
import mw
import db

# cmd = 'ls /usr/local/lib/ | grep python  | cut -d \\  -f 1 | awk \'END {print}\''
# info = mw.execShell(cmd)
# p = "/usr/local/lib/" + info[0].strip() + "/site-packages"
# sys.path.append(p)

INIT_DIR = "/etc/rc.d/init.d"
if mw.isAppleSystem():
    INIT_DIR = mw.getRunDir() + "/scripts/init.d"

INIT_CMD = INIT_DIR + "/mw"


def mw_input_cmd(msg):
    if sys.version_info[0] == 2:
        in_val = raw_input(msg)
    else:
        in_val = input(msg)
    return in_val


def mwcli(mw_input=0):
    raw_tip = "======================================================"
    if not mw_input:
        print("===============mdserver-web cli tools=================")
        print("(1)      重启面板服务")
        print("(2)      停止面板服务")
        print("(3)      启动面板服务")
        print("(4)      重载面板服务")
        print("(5)      修改面板端口")
        print("(10)     查看面板默认信息")
        print("(11)     修改面板密码")
        print("(12)     修改面板用户名")
        print("(13)     显示面板错误日志")
        print("(20)     关闭BasicAuth认证")
        print("(21)     解除域名绑定")
        print("(22)     开启IPV6支持")
        print("(23)     关闭IPV6支持")
        print("(24)     开启防火墙SSH端口")
        print("(25)     关闭二次验证")
        print("(100)    开启PHP52显示")
        print("(101)    关闭PHP52显示")
        print("(200)    切换Linux系统软件源")
        print("(201)    简单速度测试")
        print("(0)      取消")
        print(raw_tip)
        try:
            mw_input = input("请输入命令编号：")
            if sys.version_info[0] == 3:
                mw_input = int(mw_input)
        except:
            mw_input = 0

    nums = [1, 2, 3, 4, 5, 10, 11, 12, 13, 20, 21, 22, 23, 24, 25, 100, 101, 200, 201]
    if not mw_input in nums:
        print(raw_tip)
        print("已取消!")
        exit()

    if mw_input == 1:
        os.system(INIT_CMD + " restart")
    elif mw_input == 2:
        os.system(INIT_CMD + " stop")
    elif mw_input == 3:
        os.system(INIT_CMD + " start")
    elif mw_input == 4:
        os.system(INIT_CMD + " reload")
    elif mw_input == 5:
        in_port = mw_input_cmd("请输入新的面板端口：")
        in_port_int = int(in_port.strip())
        if in_port_int < 65536 and in_port_int > 0:
            import firewall_api
            firewall_api.firewall_api().addAcceptPortArgs(
                in_port, 'WEB面板[TOOLS修改]', 'port')
            mw.writeFile('data/port.pl', in_port)
            os.system(INIT_CMD + " restart_panel")
            os.system(INIT_CMD + " default")
        else:
            print("|-端口范围在0-65536之间")
        return
    elif mw_input == 10:
        os.system(INIT_CMD + " default")
    elif mw_input == 11:
        input_pwd = mw_input_cmd("请输入新的面板密码：")
        if len(input_pwd.strip()) < 5:
            print("|-错误，密码长度不能小于5位")
            return
        set_panel_pwd(input_pwd.strip(), True)
    elif mw_input == 12:
        input_user = mw_input_cmd("请输入新的面板用户名(>=5位)：")
        set_panel_username(input_user.strip())
    elif mw_input == 13:
        os.system('tail -100 ' + mw.getRunDir() + '/logs/error.log')
    elif mw_input == 20:
        basic_auth = 'data/basic_auth.json'
        if os.path.exists(basic_auth):
            os.remove(basic_auth)
            os.system(INIT_CMD + " restart")
            print("|-关闭basic_auth成功")
    elif mw_input == 21:
        bind_domain = 'data/bind_domain.pl'
        if os.path.exists(bind_domain):
            os.remove(bind_domain)
            os.system(INIT_CMD + " unbind_domain")
            print("|-解除域名绑定成功")
    elif mw_input == 22:
        listen_ipv6 = 'data/ipv6.pl'
        if not os.path.exists(listen_ipv6):
            mw.writeFile(listen_ipv6,'True')
            os.system(INIT_CMD + " restart")
            print("|-开启IPv6支持了")
        else:
            print("|-已开启IPv6支持!")
    elif mw_input == 23:
        listen_ipv6 = 'data/ipv6.pl'
        if not os.path.exists(listen_ipv6):
            print("|-已关闭IPv6支持!")
        else:
            os.remove(listen_ipv6)
            os.system(INIT_CMD + " restart")
            print("|-关闭IPv6支持了")
    elif mw_input == 24:
        open_ssh_port()
        print("|-已开启!")
    elif mw_input == 25:
        auth_secret = 'data/auth_secret.pl'
        if os.path.exists(auth_secret):
            os.remove(auth_secret)
            print("|-关闭二次验证成功!")
        else:
            print("|-二次验证已关闭!")
    elif mw_input == 100:
        php_conf = 'plugins/php/info.json'
        if os.path.exists(php_conf):
            cont = mw.readFile(php_conf)
            cont = re.sub("\"53\"", "\"52\",\"53\"", cont)
            cont = re.sub("\"5.3.29\"", "\"5.2.17\",\"5.3.29\"", cont)
            mw.writeFile(php_conf, cont)
            print("|-执行PHP52显示成功!")
    elif mw_input == 101:
        php_conf = 'plugins/php/info.json'
        if os.path.exists(php_conf):
            cont = mw.readFile(php_conf)
            cont = re.sub("\"52\",", "", cont)
            cont = re.sub("\"5.2.17\",", cont)
            mw.writeFile(php_conf, cont)
            print("|-执行PHP52隐藏成功!")
    elif mw_input == 200:
        os.system(INIT_CMD + " mirror")
    elif mw_input == 201:
        os.system('curl -Lso- bench.sh | bash')


def open_ssh_port():
    import firewall_api
    find_ssh_port_cmd = "cat /etc/ssh/sshd_config | grep '^Port \d*' | tail -1"
    cmd_data = mw.execShell(find_ssh_port_cmd)
    ssh_port = cmd_data[0].replace("Port ", '').strip()
    if ssh_port == '':
        ssh_port = '22'

    print("|-SSH端口: "+ str(ssh_port))
    firewall_api.firewall_api().addAcceptPortArgs(ssh_port, 'SSH远程管理服务', 'port')
    return True


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


def show_panel_pwd():
    # 设置面板密码
    import db
    sql = db.Sql()
    password = sql.table('users').where('id=?', (1,)).getField('password')

    file_pwd = ''
    if os.path.exists('data/default.pl'):
        file_pwd = mw.readFile('data/default.pl').strip()

    if mw.md5(file_pwd) == password:
        print('password: ' + file_pwd)
        return
    print("password has been changed!")


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
        "curl --insecure -{} -sS --connect-timeout 5 -m 60 https://v6r.ipip.net/?format=text".format(version))
    print(ip[0])


if __name__ == "__main__":
    method = sys.argv[1]
    if method == 'panel':
        set_panel_pwd(sys.argv[2])
    elif method == 'username':
        if len(sys.argv) > 2:
            set_panel_username(sys.argv[2])
        else:
            set_panel_username()
    elif method == 'password':
        show_panel_pwd()
    elif method == 'getServerIp':
        getServerIp()
    elif method == "cli":
        clinum = 0
        try:
            if len(sys.argv) > 2:
                clinum = int(sys.argv[2]) if sys.argv[2][:6] else sys.argv[2]
        except:
            clinum = sys.argv[2]
        mwcli(clinum)
    else:
        print('ERROR: Parameter error')
