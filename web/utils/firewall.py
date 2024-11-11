# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os
import re
import threading
import re
import time


import core.mw as mw
import thisdb

class Firewall(object):

    __isFirewalld = False
    __isIptables = False
    __isUfw = False
    __isMac = False

    # lock
    _instance_lock = threading.Lock()

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(Firewall, "_instance"):
            with Firewall._instance_lock:
                if not hasattr(Firewall, "_instance"):
                    Firewall._instance = Firewall(*args, **kwargs)
        return Firewall._instance

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

    # 自动识别防火墙配置 | Automatically identify firewall
    def aIF(self):
        if self.__isFirewalld:
            self.AIF_Firewalld()

    def AIF_Firewalld(self):
        # firewall-cmd --list-all | grep '  ports'
        data = mw.execShell("firewall-cmd --list-all | grep '  ports'")
        print(data)

    def getList(self, page=1,size=10):
        info = thisdb.getFirewallList(page=page, size=size)

        rdata = {}
        rdata['data'] = info['list']
        rdata['page'] = mw.getPage({'count':info['count'],'tojs':'showAccept','p':page,'row':size})
        return rdata

    def reload(self):
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


    def getSshInfo(self):
        data = {}

        file = '/etc/ssh/sshd_config'
        conf = mw.readFile(file)
        rep = r"#*Port\s+([0-9]+)\s*\n"
        port = re.search(rep, conf).groups(0)[0]

        isPing = True
        try:
            if mw.isAppleSystem():
                isPing = True
            else:
                file = '/etc/sysctl.conf'
                sys_conf = mw.readFile(file)
                rep = r"#*net\.ipv4\.icmp_echo_ignore_all\s*=\s*([0-9]+)"
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
        pass_rep = r"PasswordAuthentication\s+(\w*)\s*\n"
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

    def setPing(self):
        if mw.isAppleSystem():
            return mw.returnData(True, '开发机不能操作!')

        status = request.form.get('status')
        filename = '/etc/sysctl.conf'
        conf = mw.readFile(filename)
        if conf.find('net.ipv4.icmp_echo') != -1:
            rep = r"net\.ipv4\.icmp_echo.*"
            conf = re.sub(rep, 'net.ipv4.icmp_echo_ignore_all=' + status, conf)
        else:
            conf += "\nnet.ipv4.icmp_echo_ignore_all=" + status

        mw.writeFile(filename, conf)
        mw.execShell('sysctl -p')
        return mw.returnData(True, '设置成功!')

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

    def addAcceptPortCmd(self, port,
        protocol:str  | None ='tcp'
    ):
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

    # 添加放行端口
    def addAcceptPort(self, port, ps, stype,
        protocol: str  | None ='tcp'
    ):
        if not self.getFwStatus():
            self.setFw(0)
            return mw.returnData(False, '防火墙启动时,才能添加规则!')

        rep = r"^\d{1,5}(:\d{1,5})?$"
        if not re.search(rep, port):
            return mw.returnData(False, '端口范围不正确!')

        if thisdb.getFirewallCountByPort(port) > 0:
            return mw.returnData(False, '您要放行的端口已存在，无需重复放行!')

        thisdb.addFirewall(port, ps=ps,protocol=protocol)
        self.addAcceptPortCmd(port, protocol=protocol)
        self.reload()
        
        msg = mw.getInfo('放行端口[{1}][{2}]成功', (port, protocol,))
        mw.writeLog("防火墙管理", msg)
        return mw.returnData(True, msg)

    def delAcceptPort(self, firewall_id, port,
        protocol: str  | None ='tcp'
    ):
        panel_port = mw.getPanelPort()

        if(int(port) == int(panel_port)):
            return mw.returnData(False, '失败，不能删除当前面板端口!')
        try:
            self.delAcceptPortCmd(port, protocol)
            mw.M('firewall').where("id=?", (firewall_id,)).delete()
            return mw.returnData(True, '删除成功!')
        except Exception as e:
            return mw.returnData(False, '删除失败!:' + str(e))

    def delAcceptPortCmd(self, port,
        protocol: str  | None ='tcp'
    ):
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
        self.reload()
        return True



