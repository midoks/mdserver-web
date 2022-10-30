# coding: utf-8

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
    __isUfw = False
    __isMac = False

    def __init__(self):
        if os.path.exists('/usr/sbin/firewalld'):
            self.__isFirewalld = True
        if os.path.exists('/usr/sbin/ufw'):
            self.__isUfw = True
        if mw.isAppleSystem():
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
            if self.__isFirewalld:
                cmd = 'firewall-cmd --permanent --add-rich-rule=\'rule family=ipv4 source address="' + \
                    address + '" drop\''
                mw.execShell(cmd)
            else:
                cmd = 'iptables -I INPUT -s ' + address + ' -j DROP'
                mw.execShell(cmd)

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

        data = self.addAcceptPortArgs(port, ps, stype)
        return mw.getJson(data)

    # 添加放行端口
    def addAcceptPortArgs(self, port, ps, stype):
        import re
        import time

        if not self.getFwStatus():
            self.setFw(0)

        rep = "^\d{1,5}(:\d{1,5})?$"
        if not re.search(rep, port):
            return mw.returnData(False, '端口范围不正确!')

        if mw.M('firewall').where("port=?", (port,)).count() > 0:
            return mw.returnData(False, '您要放行的端口已存在，无需重复放行!')

        msg = mw.getInfo('放行端口[{1}]成功', (port,))
        mw.writeLog("防火墙管理", msg)
        addtime = time.strftime('%Y-%m-%d %X', time.localtime())
        mw.M('firewall').add('port,ps,addtime', (port, ps, addtime))

        self.addAcceptPort(port)
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
        else:
            if self.__isFirewalld:
                mw.execShell(
                    'firewall-cmd --permanent --remove-rich-rule=\'rule family=ipv4 source address="' + address + '" drop\'')
            elif self.__isMac:
                pass
            else:
                cmd = 'iptables -D INPUT -s ' + address + ' -j DROP'
                mw.execShell(cmd)

        msg = mw.getInfo('解除IP[{1}]的屏蔽!', (address,))
        mw.writeLog("防火墙管理", msg)
        mw.M('firewall').where("id=?", (sid,)).delete()

        self.firewallReload()
        return mw.returnJson(True, '删除成功!')

    # 删除放行端口
    def delAcceptPortApi(self):
        port = request.form.get('port', '').strip()
        sid = request.form.get('id', '').strip()
        mw_port = mw.readFile('data/port.pl')
        try:
            if(port == mw_port):
                return mw.returnJson(False, '失败，不能删除当前面板端口!')
            if self.__isUfw:
                mw.execShell('ufw delete allow ' + port + '/tcp')
            else:
                if self.__isFirewalld:
                    mw.execShell(
                        'firewall-cmd --permanent --zone=public --remove-port=' + port + '/tcp')
                    mw.execShell(
                        'firewall-cmd --permanent --zone=public --remove-port=' + port + '/udp')
                else:
                    mw.execShell(
                        'iptables -D INPUT -p tcp -m state --state NEW -m tcp --dport ' + port + ' -j ACCEPT')
            msg = mw.getInfo('删除防火墙放行端口[{1}]成功!', (port,))
            mw.writeLog("防火墙管理", msg)
            mw.M('firewall').where("id=?", (sid,)).delete()

            self.firewallReload()
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

    def getLogListApi(self):
        p = request.form.get('p', '1').strip()
        limit = request.form.get('limit', '10').strip()
        search = request.form.get('search', '').strip()
        return self.getLogList(int(p), int(limit), search)

    def getSshInfoApi(self):
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
                conf = mw.readFile(file)
                rep = "#*net\.ipv4\.icmp_echo_ignore_all\s*=\s*([0-9]+)"
                tmp = re.search(rep, conf).groups(0)[0]
                if tmp == '1':
                    isPing = False
        except:
            isPing = True

        import system_api
        panelsys = system_api.system_api()
        version = panelsys.getSystemVersion()
        if os.path.exists('/usr/bin/apt-get'):
            if os.path.exists('/etc/init.d/sshd'):
                cmd = "service sshd status | grep -P '(dead|stop)'|grep -v grep"
                status = mw.execShell(cmd)
            else:
                cmd = "service ssh status | grep -P '(dead|stop)'|grep -v grep"
                status = mw.execShell(cmd)
        else:
            if version.find(' 7.') != -1:
                cmd = "systemctl status sshd.service | grep 'dead'|grep -v grep"
                status = mw.execShell(cmd)
            else:
                cmd = "/etc/init.d/sshd status | grep -e 'stopped' -e '已停'|grep -v grep"
                status = mw.execShell(cmd)
        if len(status[0]) > 3:
            status = False
        else:
            status = True

        data = {}
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

        ports = ['21', '25', '80', '443', '7200', '8080', '888', '8888']
        if port in ports:
            return mw.returnJson(False, '(' + port + ')' + '特殊端口不可设置!')

        file = '/etc/ssh/sshd_config'
        conf = mw.readFile(file)

        rep = "#*Port\s+([0-9]+)\s*\n"
        conf = re.sub(rep, "Port " + port + "\n", conf)
        mw.writeFile(file, conf)

        if self.__isFirewalld:
            mw.execShell('setenforce 0')
            mw.execShell(
                'sed -i "s#SELINUX=enforcing#SELINUX=disabled#" /etc/selinux/config')
            mw.execShell("systemctl restart sshd.service")
        elif self.__isUfw:
            mw.execShell('ufw allow ' + port + '/tcp')
            mw.execShell("service ssh restart")
        else:
            mw.execShell(
                'iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport ' + port + ' -j ACCEPT')
            mw.execShell("/etc/init.d/sshd restart")

        self.firewallReload()
        # mw.M('firewall').where(
        #     "ps=?", ('SSH远程管理服务',)).setField('port', port)
        msg = "改SSH端口为[{}]成功!".format(port)
        mw.writeLog("防火墙管理", msg)
        return mw.returnJson(True, '修改成功!')

    def setSshStatusApi(self):
        if mw.isAppleSystem():
            return mw.returnJson(True, '开发机不能操作!')

        status = request.form.get('status', '1').strip()
        version = mw.readFile('/etc/redhat-release')
        if int(status) == 1:
            msg = 'SSH服务已停用'
            act = 'stop'
        else:
            msg = 'SSH服务已启用'
            act = 'start'

        if not os.path.exists('/etc/redhat-release'):
            mw.execShell('service ssh ' + act)
        elif version.find(' 7.') != -1:
            mw.execShell("systemctl " + act + " sshd.service")
        else:
            mw.execShell("/etc/init.d/sshd " + act)

        mw.writeLog("防火墙管理", msg)
        return mw.returnJson(True, '操作成功!')

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

    def setFw(self, status):
        if status == '1':
            if self.__isUfw:
                mw.execShell('/usr/sbin/ufw disable')
            if self.__isFirewalld:
                mw.execShell('systemctl stop firewalld.service')
                mw.execShell('systemctl disable firewalld.service')
            elif self.__isMac:
                pass
            else:
                mw.execShell('/etc/init.d/iptables save')
                mw.execShell('/etc/init.d/iptables stop')
        else:
            if self.__isUfw:
                mw.execShell("echo 'y'|sudo ufw enable")
            if self.__isFirewalld:
                mw.execShell('systemctl start firewalld.service')
                mw.execShell('systemctl enable firewalld.service')
            elif self.__isMac:
                pass
            else:
                mw.execShell('/etc/init.d/iptables save')
                mw.execShell('/etc/init.d/iptables restart')

        return mw.returnData(True, '设置成功!')

    def delPanelLogsApi(self):
        mw.M('logs').where('id>?', (0,)).delete()
        mw.writeLog('面板设置', '面板操作日志已清空!')
        return mw.returnJson(True, '面板操作日志已清空!')

    ##### ----- start ----- ###

    def getList(self, page, limit):

        start = (page - 1) * limit

        _list = mw.M('firewall').field('id,port,ps,addtime').limit(
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

    def getLogList(self, page, limit, search=''):
        find_search = ''
        if search != '':
            find_search = "type like '%" + search + "%' or log like '%" + \
                search + "%' or addtime like '%" + search + "%'"

        start = (page - 1) * limit

        _list = mw.M('logs').where(find_search, ()).field(
            'id,type,log,addtime').limit(str(start) + ',' + str(limit)).order('id desc').select()
        data = {}
        data['data'] = _list

        count = mw.M('logs').where(find_search, ()).count()
        _page = {}
        _page['count'] = count
        _page['tojs'] = 'getLogs'
        _page['p'] = page

        data['page'] = mw.getPage(_page)
        return mw.getJson(data)

    def addAcceptPort(self, port):
        if self.__isUfw:
            mw.execShell('ufw allow ' + port + '/tcp')
        elif self.__isFirewalld:
            port = port.replace(':', '-')
            cmd = 'firewall-cmd --permanent --zone=public --add-port=' + port + '/tcp'
            mw.execShell(cmd)
        elif self.__isMac:
            pass
        else:
            cmd = 'iptables -I INPUT -p tcp -m state --state NEW -m tcp --dport ' + port + ' -j ACCEPT'
            mw.execShell(cmd)

    def firewallReload(self):
        if self.__isUfw:
            mw.execShell('/usr/sbin/ufw reload')
            return
        if self.__isFirewalld:
            mw.execShell('firewall-cmd --reload')
        elif self.__isMac:
            pass
        else:
            mw.execShell('/etc/init.d/iptables save')
            mw.execShell('/etc/init.d/iptables restart')

    def getFwStatus(self):
        if self.__isUfw:
            cmd = "/usr/sbin/ufw status| grep Status | awk -F ':' '{print $2}'"
            data = mw.execShell(cmd)
            if data[0].strip() == 'inactive':
                return False
            return True
        if self.__isFirewalld:
            cmd = "ps -ef|grep firewalld |grep -v grep | awk '{print $2}'"
            data = mw.execShell(cmd)
            if data[0] == '':
                return False
            return True
        elif self.__isMac:
            return False
        else:
            cmd = "ps -ef|grep iptables |grep -v grep  | awk '{print $2}'"
            data = mw.execShell(cmd)
            if data[0] == '':
                return False
            return True
