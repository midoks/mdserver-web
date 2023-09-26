# coding: utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------
# 防火墙操作
# ---------------------------------------------------------------------------------


import psutil
import time
import os
import sys
import mw
import re
import json
import pwd

from flask import request


class firewall_api:

    __isFirewalld = False
    __isIptables = False
    __isUfw = False
    __isMac = False

    def __init__(self):
        iptables_file = mw.systemdCfgDir() + '/iptables.service'
        if os.path.exists('/usr/sbin/firewalld'):
            self.__isFirewalld = True
        elif os.path.exists('/usr/sbin/ufw'):
            self.__isUfw = True
        elif os.path.exists(iptables_file):
            self.__isIptables = True
        elif mw.isAppleSystem():
            self.__isMac = True

    ##### ----- start ----- ###
    # 添加屏蔽IP
    def addDropAddressApi(self):
        import re
        port = request.form.get('port', '').strip()
        ps = request.form.get('ps', '').strip()

        rep = "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(\/\d{1,2})?$"
        if not re.search(rep, port):
            return mw.returnJson(False, '您输入的IP地址不合法!')
        address = port
        if mw.M('firewall').where("port=?", (address,)).count() > 0:
            return mw.returnJson(False, '您要放屏蔽的IP已存在屏蔽列表，无需重复处理!')
        if self.__isUfw:
            mw.execShell('ufw deny from ' + address + ' to any')
        else:
            if self.__isIptables:
                cmd = 'iptables -I INPUT -s ' + address + ' -j DROP'
                mw.execShell(cmd)
            elif self.__isFirewalld:
                cmd = 'firewall-cmd --permanent --add-rich-rule=\'rule family=ipv4 source address="' + \
                    address + '" drop\''
                mw.execShell(cmd)
            else:
                pass

        msg = mw.getInfo('屏蔽IP[{1}]成功!', (address,))
        mw.writeLog("防火墙管理", msg)
        addtime = time.strftime('%Y-%m-%d %X', time.localtime())
        mw.M('firewall').add('port,ps,addtime', (address, ps, addtime))
        self.firewallReload()
        return mw.returnJson(True, '添加成功!')

    # 添加放行端口
    def addAcceptPortApi(self):
        if not self.getFwStatus():
            return mw.returnJson(False, '防火墙启动时,才能添加规则!')

        port = request.form.get('port', '').strip()
        ps = request.form.get('ps', '').strip()
        stype = request.form.get('type', '').strip()
        protocol = request.form.get('protocol', '').strip()

        data = self.addAcceptPortArgs(port, ps, stype, protocol)
        return mw.getJson(data)

    # 添加放行端口
    def addAcceptPortArgs(self, port, ps, stype, protocol='tcp'):
        import re
        import time

        if not self.getFwStatus():
            self.setFw(0)

        rep = "^\d{1,5}(:\d{1,5})?$"
        if not re.search(rep, port):
            return mw.returnData(False, '端口范围不正确!')

        if mw.M('firewall').where("port=?", (port,)).count() > 0:
            return mw.returnData(False, '您要放行的端口已存在，无需重复放行!')

        msg = mw.getInfo('放行端口[{1}][{2}]成功', (port, protocol,))
        mw.writeLog("防火墙管理", msg)
        addtime = time.strftime('%Y-%m-%d %X', time.localtime())
        mw.M('firewall').add('port,protocol,ps,addtime',
                             (port, protocol, ps, addtime))

        self.addAcceptPort(port, protocol)
        self.firewallReload()
        return mw.returnData(True, '添加放行(' + port + ')端口成功!')

    # 删除IP屏蔽
    def delDropAddressApi(self):
        if not self.getFwStatus():
            return mw.returnJson(False, '防火墙启动时,才能删除规则!')

        port = request.form.get('port', '').strip()
        ps = request.form.get('ps', '').strip()
        sid = request.form.get('id', '').strip()
        address = port
        if self.__isUfw:
            mw.execShell('ufw delete deny from ' + address + ' to any')
        elif self.__isFirewalld:
            mw.execShell(
                'firewall-cmd --permanent --remove-rich-rule=\'rule family=ipv4 source address="' + address + '" drop\'')
        elif self.__isIptables:
            cmd = 'iptables -D INPUT -s ' + address + ' -j DROP'
            mw.execShell(cmd)
        else:
            pass

        msg = mw.getInfo('解除IP[{1}]的屏蔽!', (address,))
        mw.writeLog("防火墙管理", msg)
        mw.M('firewall').where("id=?", (sid,)).delete()

        self.firewallReload()
        return mw.returnJson(True, '删除成功!')

    def delAcceptPortArgs(self, port, protocol='tcp'):
        if self.__isUfw:
            if protocol == 'tcp':
                mw.execShell('ufw delete allow ' + port + '/tcp')
            if protocol == 'udp':
                mw.execShell('ufw delete allow ' + port + '/udp')
            if protocol == 'tcp/udp':
                mw.execShell('ufw delete allow ' + port + '/tcp')
                mw.execShell('ufw delete allow ' + port + '/udp')
        elif self.__isFirewalld:
            port = port.replace(':', '-')
            if protocol == 'tcp':
                mw.execShell(
                    'firewall-cmd --permanent --zone=public --remove-port=' + port + '/tcp')
            if protocol == 'udp':
                mw.execShell(
                    'firewall-cmd --permanent --zone=public --remove-port=' + port + '/udp')
            if protocol == 'tcp/udp':
                mw.execShell(
                    'firewall-cmd --permanent --zone=public --remove-port=' + port + '/tcp')
                mw.execShell(
                    'firewall-cmd --permanent --zone=public --remove-port=' + port + '/udp')
        elif self.__isIptables:
            if protocol == 'tcp':
                mw.execShell(
                    'iptables -D INPUT -p tcp -m state --state NEW -m tcp --dport ' + port + ' -j ACCEPT')
            if protocol == 'udp':
                mw.execShell(
                    'iptables -D INPUT -p udp -m state --state NEW -m udp --dport ' + port + ' -j ACCEPT')
            if protocol == 'tcp/udp':
                mw.execShell(
                    'iptables -D INPUT -p tcp -m state --state NEW -m tcp --dport ' + port + ' -j ACCEPT')
                mw.execShell(
                    'iptables -D INPUT -p udp -m state --state NEW -m udp --dport ' + port + ' -j ACCEPT')
        else:
            pass

        mw.M('firewall').where("port=?", (port,)).delete()

        msg = mw.getInfo('删除防火墙放行端口[{1}][{2}]成功!', (port, protocol,))
        mw.writeLog("防火墙管理", msg)

        self.firewallReload()
        return True

    # 删除放行端口
    def delAcceptPortApi(self):
        port = request.form.get('port', '').strip()
        protocol = request.form.get('protocol', 'tcp').strip()
        sid = request.form.get('id', '').strip()
        mw_port = mw.readFile('data/port.pl')

        if(port == mw_port):
            return mw.returnJson(False, '失败，不能删除当前面板端口!')
        try:
            self.delAcceptPortArgs(port, protocol)
            mw.M('firewall').where("id=?", (sid,)).delete()

            return mw.returnJson(True, '删除成功!')
        except Exception as e:
            return mw.returnJson(False, '删除失败!:' + str(e))

    def getWwwPathApi(self):
        path = mw.getLogsDir()
        return mw.getJson({'path': path})

    def getListApi(self):
        p = request.form.get('p', '1').strip()
        limit = request.form.get('limit', '10').strip()
        return self.getList(int(p), int(limit))

    def getSshInfoApi(self):
        data = {}

        file = '/etc/ssh/sshd_config'
        conf = mw.readFile(file)
        rep = "#*Port\s+([0-9]+)\s*\n"
        port = re.search(rep, conf).groups(0)[0]

        isPing = True
        try:
            if mw.isAppleSystem():
                isPing = True
            else:
                file = '/etc/sysctl.conf'
                sys_conf = mw.readFile(file)
                rep = "#*net\.ipv4\.icmp_echo_ignore_all\s*=\s*([0-9]+)"
                tmp = re.search(rep, sys_conf).groups(0)[0]
                if tmp == '1':
                    isPing = False
        except:
            isPing = True

        # sshd 检测
        status = True
        cmd = "service sshd status | grep -P '(dead|stop)'|grep -v grep"
        ssh_status = mw.execShell(cmd)
        if ssh_status[0] != '':
            status = False

        cmd = "systemctl status sshd.service | grep 'dead'|grep -v grep"
        ssh_status = mw.execShell(cmd)
        if ssh_status[0] != '':
            status = False

        data['pass_prohibit_status'] = False
        # 密码登陆配置检查
        pass_rep = "PasswordAuthentication\s+(\w*)\s*\n"
        pass_status = re.search(pass_rep, conf)
        if pass_status:
            if pass_status and pass_status.groups(0)[0].strip() == 'no':
                data['pass_prohibit_status'] = True
        else:
            data['pass_prohibit_status'] = True

        data['port'] = port
        data['status'] = status
        data['ping'] = isPing
        if mw.isAppleSystem():
            data['firewall_status'] = False
        else:
            data['firewall_status'] = self.getFwStatus()
        return mw.getJson(data)

    def setSshPortApi(self):
        port = request.form.get('port', '1').strip()
        if int(port) < 22 or int(port) > 65535:
            return mw.returnJson(False, '端口范围必需在22-65535之间!')

        ports = ['21', '25', '80', '443', '888']
        if port in ports:
            return mw.returnJson(False, '(' + port + ')' + '特殊端口不可设置!')

        file = '/etc/ssh/sshd_config'
        conf = mw.readFile(file)

        rep = "#*Port\s+([0-9]+)\s*\n"
        conf = re.sub(rep, "Port " + port + "\n", conf)
        mw.writeFile(file, conf)

        self.addAcceptPortArgs(port, 'SSH端口修改', 'port')
        if self.__isUfw:
            mw.execShell("service ssh restart")
        elif self.__isIptables:
            mw.execShell("/etc/init.d/sshd restart")
        elif self.__isFirewalld:
            mw.execShell("systemctl restart sshd.service")
        else:
            return mw.returnJson(False, '修改失败!')
        return mw.returnJson(True, '修改成功!')

    def setSshStatusApi(self):
        if mw.isAppleSystem():
            return mw.returnJson(True, '开发机不能操作!')

        status = request.form.get('status', '1').strip()
        msg = 'SSH服务已启用'
        act = 'start'
        if status == "1":
            msg = 'SSH服务已停用'
            act = 'stop'

        ssh_service = mw.systemdCfgDir() + '/sshd.service'
        if os.path.exists(ssh_service):
            mw.execShell("systemctl " + act + " sshd.service")
        else:
            mw.execShell('service sshd ' + act)

        if os.path.exists('/etc/init.d/sshd'):
            mw.execShell('/etc/init.d/sshd ' + act)

        mw.writeLog("防火墙管理", msg)
        return mw.returnJson(True, '操作成功!')

    def setSshPassStatusApi(self):
        if mw.isAppleSystem():
            return mw.returnJson(True, '开发机不能操作!')

        status = request.form.get('status', '1').strip()
        msg = '禁止密码登陆成功'
        if status == "1":
            msg = '开启密码登陆成功'

        file = '/etc/ssh/sshd_config'
        if not os.path.exists(file):
            return mw.returnJson(False, '无法设置!')

        conf = mw.readFile(file)

        pass_rep = "PasswordAuthentication\s+(\w*)\s*\n"
        pass_status = re.search(pass_rep, conf)
        if not pass_status:
            rep = "(#)?PasswordAuthentication\s+(\w*)\s*\n"
            conf = re.sub(rep, "PasswordAuthentication yes\n", conf)

        if status == '1':
            rep = "PasswordAuthentication\s+(\w*)\s*\n"
            conf = re.sub(rep, "PasswordAuthentication yes\n", conf)
        else:
            rep = "PasswordAuthentication\s+(\w*)\s*\n"
            conf = re.sub(rep, "PasswordAuthentication no\n", conf)
        mw.writeFile(file, conf)
        mw.execShell("systemctl restart sshd.service")
        mw.writeLog("SSH管理", msg)
        return mw.returnJson(True, msg)

    def setPingApi(self):
        if mw.isAppleSystem():
            return mw.returnJson(True, '开发机不能操作!')

        status = request.form.get('status')
        filename = '/etc/sysctl.conf'
        conf = mw.readFile(filename)
        if conf.find('net.ipv4.icmp_echo') != -1:
            rep = u"net\.ipv4\.icmp_echo.*"
            conf = re.sub(rep, 'net.ipv4.icmp_echo_ignore_all=' + status, conf)
        else:
            conf += "\nnet.ipv4.icmp_echo_ignore_all=" + status

        mw.writeFile(filename, conf)
        mw.execShell('sysctl -p')
        return mw.returnJson(True, '设置成功!')

    def setFwApi(self):
        if mw.isAppleSystem():
            return mw.returnJson(True, '开发机不能设置!')

        status = request.form.get('status', '1')
        return mw.getJson(self.setFw(status))

    def setFwIptables(self, status):
        # iptables特殊处理
        if status == '1':
            mw.execShell('service iptables save')
            mw.execShell('service iptables stop')
        else:
            # 重新导入数据
            _list = mw.M('firewall').field('id,port,ps,addtime').limit(
                '0,1000').order('id desc').select()

            mw.execShell('iptables -P INPUT DROP')
            mw.execShell('iptables -P OUTPUT ACCEPT')
            for x in _list:
                port = x['port']
                if mw.isIpAddr(port):
                    cmd = 'iptables -I INPUT -s ' + port + ' -j DROP'
                    mw.execShell(cmd)
                else:
                    self.addAcceptPort(port)

            mw.execShell('service iptables save')
            mw.execShell('service iptables start')

    def setFw(self, status):

        if self.__isIptables:
            self.setFwIptables(status)
            return mw.returnData(True, '设置成功!')

        if status == '1':
            if self.__isUfw:
                mw.execShell('/usr/sbin/ufw disable')

            elif self.__isFirewalld:
                mw.execShell('systemctl stop firewalld.service')
                mw.execShell('systemctl disable firewalld.service')
            else:
                pass
        else:
            if self.__isUfw:
                mw.execShell("echo 'y'| ufw enable")
            elif self.__isFirewalld:
                mw.execShell('systemctl start firewalld.service')
                mw.execShell('systemctl enable firewalld.service')
            else:
                pass

        return mw.returnData(True, '设置成功!')

    ##### ----- start ----- ###

    def getList(self, page, limit):

        start = (page - 1) * limit

        _list = mw.M('firewall').field('id,port,protocol,ps,addtime').limit(
            str(start) + ',' + str(limit)).order('id desc').select()
        data = {}
        data['data'] = _list

        count = mw.M('firewall').count()
        _page = {}
        _page['count'] = count
        _page['tojs'] = 'showAccept'
        _page['p'] = page

        data['page'] = mw.getPage(_page)
        return mw.getJson(data)

    def addAcceptPort(self, port, protocol='tcp'):
        if self.__isUfw:
            if protocol == 'tcp':
                mw.execShell('ufw allow ' + port + '/tcp')
            if protocol == 'udp':
                mw.execShell('ufw allow ' + port + '/udp')
            if protocol == 'tcp/udp':
                mw.execShell('ufw allow ' + port + '/tcp')
                mw.execShell('ufw allow ' + port + '/udp')
        elif self.__isFirewalld:
            port = port.replace(':', '-')
            if protocol == 'tcp':
                cmd = 'firewall-cmd --permanent --zone=public --add-port=' + port + '/tcp'
                mw.execShell(cmd)
            if protocol == 'udp':
                cmd = 'firewall-cmd --permanent --zone=public --add-port=' + port + '/udp'
                mw.execShell(cmd)
            if protocol == 'tcp/udp':
                cmd = 'firewall-cmd --permanent --zone=public --add-port=' + port + '/tcp'
                mw.execShell(cmd)
                cmd = 'firewall-cmd --permanent --zone=public --add-port=' + port + '/udp'
                mw.execShell(cmd)
        elif self.__isIptables:
            if protocol == 'tcp':
                cmd = 'iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport ' + port + ' -j ACCEPT'
                mw.execShell(cmd)
            if protocol == 'udp':
                cmd = 'iptables -I INPUT -p udp -m state --state NEW -m udp --dport ' + port + ' -j ACCEPT'
                mw.execShell(cmd)
            if protocol == 'tcp/udp':
                cmd = 'iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport ' + port + ' -j ACCEPT'
                mw.execShell(cmd)
                cmd = 'iptables -I INPUT -p udp -m state --state NEW -m udp --dport ' + port + ' -j ACCEPT'
                mw.execShell(cmd)
        else:
            pass
        return True

    def firewallReload(self):
        if self.__isUfw:
            mw.execShell('/usr/sbin/ufw reload')
            return
        elif self.__isIptables:
            mw.execShell('service iptables save')
            mw.execShell('service iptables restart')
        elif self.__isFirewalld:
            mw.execShell('firewall-cmd --reload')
        else:
            pass

    def getFwStatus(self):
        if self.__isUfw:
            cmd = "/usr/sbin/ufw status| grep Status | awk -F ':' '{print $2}'"
            data = mw.execShell(cmd)
            if data[0].strip() == 'inactive':
                return False
            return True
        elif self.__isIptables:
            cmd = "systemctl status iptables | grep 'inactive'"
            data = mw.execShell(cmd)
            if data[0] != '':
                return False
            return True
        elif self.__isFirewalld:
            cmd = "ps -ef|grep firewalld |grep -v grep | awk '{print $2}'"
            data = mw.execShell(cmd)
            if data[0] == '':
                return False
            return True
        else:
            return False
