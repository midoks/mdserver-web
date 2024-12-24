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
        if self.__isUfw:
            self.aIF_Ufw()


    def aIF_Ufw(self):
        t = mw.execShell("ufw status|awk '{print $1}' | grep -v 'Status'|grep -v 'To'|grep -v '-'")
        if t[1] != '':
            return True

        all_port = t[0].strip()
        ports_list = all_port.split('\n')

        ports_all = []
        for pinfo in ports_list:
            info = pinfo.split('/')

            is_same = False
            for i in range(len(ports_all)):
                if ports_all[i]['port'] == info[0] and ports_all[i]['protocol'] != info[1]:
                    ports_all[i]['protocol'] = ports_all[i]['protocol']+'/'+info[1]
                    is_same = True

            if not is_same:
                t = {}
                t['port'] = info[0].replace('-',':')
                t['protocol'] = info[1]
                ports_all.append(t)
        for add_info in ports_all:
            if thisdb.getFirewallCountByPort(add_info['port']) == 0:
                thisdb.addFirewall(add_info['port'], ps='自动识别',protocol=add_info['protocol'])

    def AIF_Firewalld(self):
        t = mw.execShell("firewall-cmd --list-all | grep '  ports'")
        if t[1] != '':
            return True

        all_port = t[0].strip()
        data = all_port.split(":")
        ports_str = data[1]
        ports_list = ports_str.strip().split(' ')

        ports_all = []
        for pinfo in ports_list:
            info = pinfo.split('/')

            is_same = False
            for i in range(len(ports_all)):
                if ports_all[i]['port'] == info[0] and ports_all[i]['protocol'] != info[1]:
                    ports_all[i]['protocol'] = ports_all[i]['protocol']+'/'+info[1]
                    is_same = True

            if not is_same:
                t = {}
                t['port'] = info[0].replace('-',':')
                t['protocol'] = info[1]
                ports_all.append(t)

        for add_info in ports_all:
            if thisdb.getFirewallCountByPort(add_info['port']) == 0:
                thisdb.addFirewall(add_info['port'], ps='自动识别',protocol=add_info['protocol'])

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

    def reloadSshd(self):
        if self.__isUfw:
            mw.execShell("service ssh restart")
        elif self.__isIptables:
            mw.execShell("/etc/init.d/sshd restart")
        elif self.__isFirewalld:
            mw.execShell("systemctl restart sshd.service")
        else:
            return False
        return True

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

        data['pubkey_prohibit_status'] = False
        data['pass_prohibit_status'] = False
        port = '22'
        sshd_file = '/etc/ssh/sshd_config'
        if  os.path.exists(sshd_file):
            conf = mw.readFile(sshd_file)
            rep = r"#*Port\s+([0-9]+)\s*\n"
            port = re.search(rep, conf).groups(0)[0]

            # 密码登陆配置检查
            pass_rep = r"PasswordAuthentication\s+(\w*)\s*\n"
            pass_status = re.search(pass_rep, conf)
            if pass_status:
                if pass_status and pass_status.groups(0)[0].strip() == 'no':
                    data['pass_prohibit_status'] = True
            else:
                data['pass_prohibit_status'] = True

            # 密钥登陆配置检查
            pass_rep = r"PubkeyAuthentication\s+(\w*)\s*\n"
            pass_status = re.search(pass_rep, conf)
            if pass_status:
                if pass_status and pass_status.groups(0)[0].strip() == 'no':
                    data['pubkey_prohibit_status'] = True
            else:
                data['pubkey_prohibit_status'] = True

        data['port'] = port
        data['status'] = status
        data['ping'] = isPing
        if mw.isAppleSystem():
            data['firewall_status'] = False
        else:
            data['firewall_status'] = self.getFwStatus()
        return data

    def setPing(self, status):
        if mw.isAppleSystem():
            return mw.returnData(True, '开发机不能操作!')

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

    def setSshPort(self, port):
        if int(port) < 22 or int(port) > 65535:
            return mw.returnData(False, '端口范围必需在22-65535之间!')

        ports = ['21', '25', '80', '443', '888']
        if port in ports:
            return mw.returnData(False, '(' + port + ')' + '特殊端口不可设置!')

        file = '/etc/ssh/sshd_config'
        conf = mw.readFile(file)

        rep = r"#*Port\s+([0-9]+)\s*\n"
        conf = re.sub(rep, "Port " + port + "\n", conf)
        mw.writeFile(file, conf)
        
        self.addAcceptPort(port, 'SSH端口修改', 'port')
        self.reload()

        if not self.reloadSshd():
            return mw.returnData(False, '重启sshd失败,尝试手动重启:service ssh restart!')
        return mw.returnData(True, '修改成功!')

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

    def addAcceptPortCmd(self, port, protocol ='tcp'):
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
        protocol='tcp'
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

    def addPanelPort(self, port):
        self.setFw(0)

        protocol = 'tcp'
        ps = 'PANEL端口'

        if thisdb.getFirewallCountByPort(port) > 0:
            return mw.returnData(False, '您要放行的端口已存在，无需重复放行!')

        thisdb.addFirewall(port, ps=ps,protocol=protocol)
        self.addAcceptPortCmd(port, protocol=protocol)
        self.reload()

        msg = mw.getInfo('放行端口[{1}][{2}]成功', (port, protocol,))
        mw.writeLog("防火墙管理", msg)
        return mw.returnData(True, msg)

    def delAcceptPort(self, firewall_id, port,
        protocol='tcp'
    ):
        panel_port = mw.getPanelPort()

        if port.find(':') > 0:
            pass
        elif port.find('-') > 0:
            pass
        else:
            if(int(port) == int(panel_port)):
                return mw.returnData(False, '失败，不能删除当前面板端口!')
        try:
            self.delAcceptPortCmd(port, protocol)
            mw.M('firewall').where("id=?", (firewall_id,)).delete()
            return mw.returnData(True, '删除成功!')
        except Exception as e:
            return mw.returnData(False, '删除失败!:' + str(e))

    def delAcceptPortCmd(self, port,
        protocol ='tcp'
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

    def setSshPassStatus(self, status):
        msg = '禁止密码登陆成功'
        if status == "1":
            msg = '开启密码登陆成功'

        file = '/etc/ssh/sshd_config'
        if not os.path.exists(file):
            return mw.returnJson(False, '无法设置!')

        conf = mw.readFile(file)

        pass_rep = r"PasswordAuthentication\s+(\w*)\s*\n"
        pass_status = re.search(pass_rep, conf)
        if not pass_status:
            rep = r"(#)?PasswordAuthentication\s+(\w*)\s*\n"
            conf = re.sub(rep, "PasswordAuthentication yes\n", conf)

        if status == '1':
            rep = r"PasswordAuthentication\s+(\w*)\s*\n"
            conf = re.sub(rep, "PasswordAuthentication yes\n", conf)
        else:
            rep = r"PasswordAuthentication\s+(\w*)\s*\n"
            conf = re.sub(rep, "PasswordAuthentication no\n", conf)
        mw.writeFile(file, conf)
        mw.execShell("systemctl restart sshd.service")
        mw.writeLog("SSH管理", msg)
        return mw.returnData(True, msg)

    def setSshPubkeyStatus(self, status):
        msg = '禁止密钥登陆成功'
        if status == "1":
            msg = '开启密钥登陆成功'

        file = '/etc/ssh/sshd_config'
        if not os.path.exists(file):
            return mw.returnJson(False, '无法设置!')

        content = mw.readFile(file)

        pubkey_rep = r"PubkeyAuthentication\s+(\w*)\s*\n"
        pubkey_status = re.search(pubkey_rep, content)
        if not pubkey_status:
            rep = r"(#)?PubkeyAuthentication\s+(\w*)\s*\n"
            content = re.sub(rep, "PubkeyAuthentication yes\n", content)

        if status == '1':
            rep = r"PubkeyAuthentication\s+(\w*)\s*\n"
            content = re.sub(rep, "PubkeyAuthentication yes\n", content)
        else:
            rep = r"PubkeyAuthentication\s+(\w*)\s*\n"
            content = re.sub(rep, "PubkeyAuthentication no\n", content)
        mw.writeFile(file, content)
        mw.execShell("systemctl restart sshd.service")
        mw.writeLog("SSH管理", msg)
        return mw.returnData(True, msg)



