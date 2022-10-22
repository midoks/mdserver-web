# coding: utf-8

import sys
import os
import json
import time

sys.path.append(os.getcwd() + "/class/core")
import mw
import db

# cmd = 'ls /usr/local/lib/ | grep python  | cut -d \\  -f 1 | awk \'END {print}\''
# info = mw.execShell(cmd)
# p = "/usr/local/lib/" + info[0].strip() + "/site-packages"
# sys.path.append(p)

INIT_DIR = "/etc/init.d"
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
        print("(1) 重启面板服务")
        print("(2) 停止面板服务")
        print("(3) 启动面板服务")
        print("(4) 重载面板服务")
        print("(5) 修改面板端口")
        print("(10) 查看面板默认信息")
        print("(11) 修改面板密码")
        print("(12) 修改面板用户名")
        print("(13) 显示面板错误日志")
        print("(0) 取消")
        print(raw_tip)
        try:
            mw_input = input("请输入命令编号：")
            if sys.version_info[0] == 3:
                mw_input = int(mw_input)
        except:
            mw_input = 0

    nums = [1, 2, 3, 4, 5, 10, 11, 12, 13]
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
        input_user = mw_input_cmd("请输入新的面板用户名(>3位)：")
        set_panel_username(input_user.strip())
    elif mw_input == 13:
        os.system('tail -100 ' + mw.getRunDir() + '/logs/error.log')


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
    method = sys.argv[1]
    if method == 'panel':
        set_panel_pwd(sys.argv[2])
    elif method == 'username':
        if len(sys.argv) > 2:
            set_panel_username(sys.argv[2])
        else:
            set_panel_username()
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
