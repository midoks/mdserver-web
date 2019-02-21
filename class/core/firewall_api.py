# coding: utf-8

import psutil
import time
import os
import sys
import public
import re
import json
import pwd

from flask import request


class firewall_api:

    __isFirewalld = False
    __isUfw = False
    __isMac = False

    def __init__(self):
        if os.path.exists('/usr/sbin/firewalld'):
            self.__isFirewalld = True
        if os.path.exists('/usr/sbin/ufw'):
            self.__isUfw = True
        if public.isAppleSystem():
            self.__isMac = True

    ##### ----- start ----- ###
    # 添加屏蔽IP
    def addDropAddressApi(self):
        import re
        port = request.form.get('port', '').strip()
        ps = request.form.get('ps', '').strip()

        rep = "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(\/\d{1,2})?$"
        if not re.search(rep, port):
            return public.returnJson(False, '您输入的IP地址不合法!')
        address = port
        if public.M('firewall').where("port=?", (address,)).count() > 0:
            return public.returnJson(False, '您要放屏蔽的IP已存在屏蔽列表，无需重复处理!')
        if self.__isUfw:
            public.execShell('ufw deny from ' + address + ' to any')
        else:
            if self.__isFirewalld:
                cmd = 'firewall-cmd --permanent --add-rich-rule=\'rule family=ipv4 source address="' + \
                    address + '" drop\''
                public.execShell(cmd)
            else:
                cmd = 'iptables -I INPUT -s ' + address + ' -j DROP'
                public.execShell(cmd)

        msg = public.getInfo('屏蔽IP[{1}]成功!', (address,))
        public.writeLog("防火墙管理", msg)
        addtime = time.strftime('%Y-%m-%d %X', time.localtime())
        public.M('firewall').add('port,ps,addtime', (address, ps, addtime))
        self.firewallReload()
        return public.returnJson(True, '添加成功!')

    # 添加放行端口
    def addAcceptPortApi(self):
        import re
        import time
        port = request.form.get('port', '').strip()
        ps = request.form.get('ps', '').strip()
        stype = request.form.get('type', '').strip()

        rep = "^\d{1,5}(:\d{1,5})?$"
        if not re.search(rep, port):
            return public.returnJson(False, '端口范围不正确!')

        if public.M('firewall').where("port=?", (port,)).count() > 0:
            return public.returnJson(False, '您要放行的端口已存在，无需重复放行!')

        msg = public.getInfo('放行端口[{1}]成功', (port,))
        public.writeLog("防火墙管理", msg)
        addtime = time.strftime('%Y-%m-%d %X', time.localtime())
        public.M('firewall').add('port,ps,addtime', (port, ps, addtime))

        self.addAcceptPort(port)
        self.firewallReload()
        return public.returnJson(True, '添加放行(' + port + ')端口成功!')

    # 删除IP屏蔽
    def delDropAddressApi(self):
        port = request.form.get('port', '').strip()
        ps = request.form.get('ps', '').strip()
        sid = request.form.get('id', '').strip()
        address = port
        if self.__isUfw:
            public.execShell('ufw delete deny from ' + address + ' to any')
        else:
            if self.__isFirewalld:
                public.execShell(
                    'firewall-cmd --permanent --remove-rich-rule=\'rule family=ipv4 source address="' + address + '" drop\'')
            elif self.__isMac:
                pass
            else:
                cmd = 'iptables -D INPUT -s ' + address + ' -j DROP'
                public.execShell(cmd)

        msg = public.getInfo('解除IP[{1}]的屏蔽!', (address,))
        public.writeLog("防火墙管理", msg)
        public.M('firewall').where("id=?", (sid,)).delete()

        self.firewallReload()
        return public.returnJson(True, '删除成功!')

    # 删除放行端口
    def delAcceptPortApi(self):
        port = request.form.get('port', '').strip()
        sid = request.form.get('id', '').strip()
        mw_port = public.readFile('data/port.pl')
        try:
            if(port == mw_port):
                return public.returnJson(False, '失败，不能删除当前面板端口!')
            if self.__isUfw:
                public.execShell('ufw delete allow ' + port + '/tcp')
            else:
                if self.__isFirewalld:
                    public.execShell(
                        'firewall-cmd --permanent --zone=public --remove-port=' + port + '/tcp')
                    public.execShell(
                        'firewall-cmd --permanent --zone=public --remove-port=' + port + '/udp')
                else:
                    public.execShell(
                        'iptables -D INPUT -p tcp -m state --state NEW -m tcp --dport ' + port + ' -j ACCEPT')
            msg = public.getInfo('删除防火墙放行端口[{1}]成功!', (port,))
            public.writeLog("防火墙管理", msg)
            public.M('firewall').where("id=?", (sid,)).delete()

            self.firewallReload()
            return public.returnJson(True, '删除成功!')
        except Exception as e:
            return public.returnJson(False, '删除失败!:' + str(e))

    def getWwwPathApi(self):
        path = public.getLogsDir()
        return public.getJson({'path': path})

    def getListApi(self):
        p = request.form.get('p', '1').strip()
        limit = request.form.get('limit', '10').strip()
        return self.getList(int(p), int(limit))

    def getLogListApi(self):
        p = request.form.get('p', '1').strip()
        limit = request.form.get('limit', '10').strip()
        search = request.form.get('search', '').strip()
        return self.getLogList(int(p), int(limit), search)

    def getSshInfoApi(self):
        file = '/etc/ssh/sshd_config'
        conf = public.readFile(file)
        rep = "#*Port\s+([0-9]+)\s*\n"
        port = re.search(rep, conf).groups(0)[0]

        isPing = True
        try:
            if public.isAppleSystem():
                isPing = True
            else:
                file = '/etc/sysctl.conf'
                conf = public.readFile(file)
                rep = "#*net\.ipv4\.icmp_echo_ignore_all\s*=\s*([0-9]+)"
                tmp = re.search(rep, conf).groups(0)[0]
                if tmp == '1':
                    isPing = False
        except:
            isPing = True

        data = {}
        data['port'] = port
        data['status'] = True
        data['ping'] = isPing
        if public.isAppleSystem():
            data['firewall_status'] = False
        else:
            data['firewall_status'] = self.getFwStatus()
        return public.getJson(data)

    def setSshPortApi(self):
        port = request.form.get('port', '1').strip()
        if int(port) < 22 or int(port) > 65535:
            return public.returnJson(False, '端口范围必需在22-65535之间!')

        ports = ['21', '25', '80', '443', '7200', '8080', '888', '8888']
        if port in ports:
            return public.returnJson(False, '(' + port + ')' + '特殊端口不可设置!')

        file = '/etc/ssh/sshd_config'
        conf = public.readFile(file)

        rep = "#*Port\s+([0-9]+)\s*\n"
        conf = re.sub(rep, "Port " + port + "\n", conf)
        public.writeFile(file, conf)

        if self.__isFirewalld:
            public.execShell('setenforce 0')
            public.execShell(
                'sed -i "s#SELINUX=enforcing#SELINUX=disabled#" /etc/selinux/config')
            public.execShell("systemctl restart sshd.service")
        elif self.__isUfw:
            public.execShell('ufw allow ' + port + '/tcp')
            public.execShell("service ssh restart")
        else:
            public.execShell(
                'iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport ' + port + ' -j ACCEPT')
            public.execShell("/etc/init.d/sshd restart")

        self.firewallReload()
        # public.M('firewall').where(
        #     "ps=?", ('SSH远程管理服务',)).setField('port', port)
        msg = public.getInfo('改SSH端口为[{1}]成功!', port)
        public.writeLog("防火墙管理", msg)
        return public.returnJson(True, '修改成功!')

    def setPingApi(self):
        if public.isAppleSystem():
            return public.returnJson(True, '开发机不能设置!')

        status = request.form.get('status')
        filename = '/etc/sysctl.conf'
        conf = public.readFile(filename)
        if conf.find('net.ipv4.icmp_echo') != -1:
            rep = u"net\.ipv4\.icmp_echo.*"
            conf = re.sub(rep, 'net.ipv4.icmp_echo_ignore_all=' + status, conf)
        else:
            conf += "\nnet.ipv4.icmp_echo_ignore_all=" + status

        public.writeFile(filename, conf)
        public.execShell('sysctl -p')
        return public.returnJson(True, '设置成功!')

    def setFwApi(self):
        if public.isAppleSystem():
            return public.returnJson(True, '开发机不能设置!')

        status = request.form.get('status', '1')
        if status == '1':
            if self.__isUfw:
                public.execShell('/usr/sbin/ufw stop')
                return
            if self.__isFirewalld:
                public.execShell('systemctl stop firewalld.service')
            elif self.__isMac:
                pass
            else:
                public.execShell('/etc/init.d/iptables save')
                public.execShell('/etc/init.d/iptables stop')
        else:
            if self.__isUfw:
                public.execShell('/usr/sbin/ufw start')
                return
            if self.__isFirewalld:
                public.execShell('systemctl start firewalld.service')
            elif self.__isMac:
                pass
            else:
                public.execShell('/etc/init.d/iptables save')
                public.execShell('/etc/init.d/iptables restart')

        return public.returnJson(True, '设置成功!')

    def delPanelLogsApi(self):
        public.M('logs').where('id>?', (0,)).delete()
        public.writeLog('面板设置', '面板操作日志已清空!')
        return public.returnJson(True, '面板操作日志已清空!')

    ##### ----- start ----- ###

    def getList(self, page, limit):

        start = (page - 1) * limit

        _list = public.M('firewall').field('id,port,ps,addtime').limit(
            str(start) + ',' + str(limit)).order('id desc').select()
        data = {}
        data['data'] = _list

        count = public.M('firewall').count()
        _page = {}
        _page['count'] = count
        _page['tojs'] = 'showAccept'
        _page['p'] = page

        data['page'] = public.getPage(_page)
        return public.getJson(data)

    def getLogList(self, page, limit, search=''):
        find_search = ''
        if search != '':
            find_search = "type like '%" + search + "%' or log like '%" + \
                search + "%' or addtime like '%" + search + "%'"

        start = (page - 1) * limit

        _list = public.M('logs').where(find_search, ()).field(
            'id,type,log,addtime').limit(str(start) + ',' + str(limit)).order('id desc').select()
        data = {}
        data['data'] = _list

        count = public.M('logs').where(find_search, ()).count()
        _page = {}
        _page['count'] = count
        _page['tojs'] = 'getLogs'
        _page['p'] = page

        data['page'] = public.getPage(_page)
        return public.getJson(data)

    def addAcceptPort(self, port):
        if self.__isUfw:
            public.execShell('ufw allow ' + port + '/tcp')
        else:
            if self.__isFirewalld:
                port = port.replace(':', '-')
                cmd = 'firewall-cmd --permanent --zone=public --add-port=' + port + '/tcp'
                public.execShell(cmd)
            elif self.__isMac:
                pass
            else:
                cmd = 'iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport ' + port + ' -j ACCEPT'
                public.execShell(cmd)

    def firewallReload(self):
        if self.__isUfw:
            public.execShell('/usr/sbin/ufw reload')
            return
        if self.__isFirewalld:
            public.execShell('firewall-cmd --reload')
        elif self.__isMac:
            pass
        else:
            public.execShell('/etc/init.d/iptables save')
            public.execShell('/etc/init.d/iptables restart')

    def getFwStatus(self):
        if self.__isUfw:
            cmd = "ps -ef|grep ufw |grep -v grep | awk '{print $2}'"
            data = public.execShell(cmd)
            if data[0] == '':
                return False
            return True
        if self.__isFirewalld:
            cmd = "ps -ef|grep firewalld |grep -v grep | awk '{print $2}'"
            data = public.execShell(cmd)
            if data[0] == '':
                return False
            return True
        elif self.__isMac:
            return False
        else:
            cmd = "ps -ef|grep iptables |grep -v grep  | awk '{print $2}'"
            data = public.execShell(cmd)
            if data[0] == '':
                return False
            return True
