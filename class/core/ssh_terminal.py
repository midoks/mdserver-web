# coding: utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------
# SSH终端操作
# ---------------------------------------------------------------------------------

import json
import time
import os
import sys
import socket
import threading
import re

from io import BytesIO, StringIO

import mw
import paramiko

from flask_socketio import SocketIO, emit, send


class ssh_terminal:

    __debug_file = 'logs/terminal.log'
    __log_type = 'SSH终端'

    # websocketio 唯一标识
    __sid = ''

    __host = None
    __type = '0'
    __port = 22
    __user = None
    __pass = None
    __pkey = None
    __key_passwd = None

    __rep_ssh_config = False
    __rep_ssh_service = False
    __sshd_config_backup = None

    __ssh = None
    __tp = None
    __ps = None

    __ssh_list = {}
    __ssh_last_request_time = {}

    def __init__(self):
        ht = threading.Thread(target=self.heartbeat)
        ht.start()

    def debug(self, msg):
        msg = "{} - {}:{} => {} \n".format(mw.formatDate(),
                                           self.__host, self.__port, msg)
        if not mw.isDebugMode():
            return
        mw.writeFile(self.__debug_file, msg, 'a+')

    def returnMsg(self, status, msg):
        return {'status': status, 'msg': msg}

    def restartSsh(self, act='reload'):
        '''
        重启ssh 无参数传递
        '''
        version = mw.readFile('/etc/redhat-release')
        if not os.path.exists('/etc/redhat-release'):
            mw.execShell('service ssh ' + act)
        elif version.find(' 7.') != -1 or version.find(' 8.') != -1:
            mw.execShell("systemctl " + act + " sshd.service")
        else:
            mw.execShell("/etc/init.d/sshd " + act)

    def isRunning(self, rep=False):
        try:
            if rep and self.__rep_ssh_service:
                self.restartSsh('stop')
                return True

            status = self.getSshStatus()
            if not status:
                self.restartSsh('start')
                self.__rep_ssh_service = True
                return True
            return False
        except:
            return False

    def setSshdConfig(self, rep=False):
        self.isRunning(rep)
        if rep and not self.__rep_ssh_config:
            return False

        try:
            sshd_config_file = '/etc/ssh/sshd_config'
            if not os.path.exists(sshd_config_file):
                return False

            sshd_config = mw.readFile(sshd_config_file)
            if not sshd_config:
                return False

            if rep:
                if self.__sshd_config_backup:
                    mw.writeFile(sshd_config_file, self.__sshd_config_backup)
                    self.restartSsh()
                return True

            pin = r'^\s*PubkeyAuthentication\s+(yes|no)'
            pubkey_status = re.findall(pin, sshd_config, re.I)
            if pubkey_status:
                if pubkey_status[0] == 'yes':
                    pubkey_status = True
                else:
                    pubkey_status = False

            pin = r'^\s*RSAAuthentication\s+(yes|no)'
            rsa_status = re.findall(pin, sshd_config, re.I)
            if rsa_status:
                if rsa_status[0] == 'yes':
                    rsa_status = True
                else:
                    rsa_status = False

            self._sshd_config_backup = sshd_config
            is_write = False
            if not pubkey_status:
                sshd_config = re.sub(
                    r'\n#?PubkeyAuthentication\s\w+', '\nPubkeyAuthentication yes', sshd_config)
                is_write = True
            if not rsa_status:
                sshd_config = re.sub(
                    r'\n#?RSAAuthentication\s\w+', '\nRSAAuthentication yes', sshd_config)
                is_write = True

            if is_write:
                mw.writeFile(sshd_config_file, sshd_config)
                self.__rep_ssh_config = True
                self.restartSsh()
            else:
                self.__sshd_config_backup = None
            return True
        except:
            return False

    def setSid(self, sid):
        self.__sid = sid

    def connect(self, sid):
        # self.connectBySocket()
        if self.__host in ['127.0.0.1', 'localhost']:
            return self.connectLocalSsh(sid)
        else:
            return self.connectBySocket(sid)

    def connectLocalSsh(self, sid):
        mw.createSshInfo()
        self.__ps = paramiko.SSHClient()
        self.__ps.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.__port = mw.getSSHPort()
        try:
            self.__ps.connect(self.__host, self.__port, timeout=60)
        except Exception as e:
            self.__ps.connect('127.0.0.1', self.__port)
        except Exception as e:
            self.__ps.connect('localhost', self.__port)
        except Exception as e:
            self.setSshdConfig(True)
            self.__ps.close()
            e = str(e)
            if e.find('websocket error!') != -1:
                return self.returnMsg(True, '连接成功')
            if e.find('Authentication timeout') != -1:
                self.debug("认证超时{}".format(e))
                return self.returnMsg(False, '认证超时,请按回车重试!{}'.format(e))
            if e.find('Connection reset by peer') != -1:
                self.debug('目标服务器主动拒绝连接')
                return self.returnMsg(False, '目标服务器主动拒绝连接')
            if e.find('Error reading SSH protocol banner') != -1:
                self.debug('协议头响应超时')
                return self.returnMsg(False, '协议头响应超时，与目标服务器之间的网络质量太糟糕：' + e)
            if not e:
                self.debug('SSH协议握手超时')
                return self.returnMsg(False, "SSH协议握手超时，与目标服务器之间的网络质量太糟糕")
            err = mw.getTracebackInfo()
            self.debug(err)
            return self.returnMsg(False, "未知错误: {}".format(err))

        self.debug('local-ssh:认证成功，正在构建会话通道')
        ssh = self.__ps.invoke_shell(
            term='xterm', width=83, height=21)
        ssh.setblocking(0)
        self.__ssh_list[sid] = ssh
        mw.writeLog(self.__log_type, '成功登录到SSH服务器 [{}:{}]'.format(
            self.__host, self.__port))
        self.debug('local-ssh:通道已构建')
        return self.returnMsg(True, '连接成功!')

    def connectBySocket(self, sid):
        if not self.__host:
            return self.returnMsg(False, '错误的连接地址')
        if not self.__user:
            self.__user = 'root'
        if not self.__port:
            self.__port = 22

        self.setSshdConfig(True)
        num = 0
        while num < 5:
            num += 1
            try:
                self.debug('正在尝试第{}次连接'.format(num))
                if self.__rep_ssh_config:
                    time.sleep(0.1)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2 + num)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 8192)
                sock.connect((self.__host, self.__port))
                break
            except Exception as e:
                if num == 5:
                    self.setSshdConfig(True)
                    self.debug('重试连接失败,{}'.format(e))
                    return self.returnMsg(False, '连接目标服务器失败, {}:{}'.format(self.__host, self.__port))
                else:
                    time.sleep(0.2)

        # print(self.__host, sock)
        self.__tp = paramiko.Transport(sock)
        try:
            self.__tp.start_client()
            self.__tp.banner_timeout = 60
            if not self.__pass and not self.__pkey:
                return self.returnMsg(False, '密码或私钥不能都为空: {}:{}'.format(self.__host, self.__port))

            if self.__pkey != '' and self.__type != '0':
                self.debug('正在认证私钥')
                p_file = StringIO(str(self.__pkey.replace('\\n', '\n')))
                # p_file = "/tmp/t_ssh_pkey.txt"
                # mw.writeFile(p_file, self.__pkey.replace('\\n', '\n'))
                # mw.execShell('chmod 600 ' + p_file)
                try:
                    p_file.seek(0)
                    pkey = paramiko.RSAKey.from_private_key(p_file)
                except:
                    try:
                        p_file.seek(0)  # 重置游标
                        pkey = paramiko.Ed25519Key.from_private_key(
                            p_file)
                    except:
                        try:
                            p_file.seek(0)
                            pkey = paramiko.ECDSAKey.from_private_key(p_file)
                        except:
                            p_file.seek(0)
                            pkey = paramiko.DSSKey.from_private_key(p_file)

                self.__tp.auth_publickey(username=self.__user, key=pkey)
            else:
                try:
                    self.__tp.auth_none(self.__user)
                except Exception as e:
                    e = str(e)
                    if e.find('keyboard-interactive') >= 0:
                        self._auth_interactive()
                    else:
                        self.debug('正在认证密码')
                        self.__tp.auth_password(
                            username=self.__user, password=self.__pass)
        except Exception as e:
            self.setSshdConfig(True)
            self.__tp.close()
            e = str(e)
            # print(e)
            if e.find('Authentication timeout') != -1:
                self.debug("认证超时{}".format(e))
                return self.returnMsg(False, '认证超时,请按回车重试!{}'.format(e))
            if e.find('Authentication failed') != -1:
                self.debug('认证失败{}'.format(e))
                return self.returnMsg(False, '帐号或密码错误: {}'.format(e + "," + self.__user + "@" + self.__host + ":" + str(self.__port)))
            if e.find('Bad authentication type; allowed types') != -1:
                self.debug('认证失败{}'.format(e))
                if self.__host in ['127.0.0.1', 'localhost'] and self.__pass == 'none':
                    return self.returnMsg(False, '帐号或密码错误: {}'.format("Authentication failed ," + self.__user + "@" + self.__host + ":" + str(self.__port)))
                return self.returnMsg(False, '不支持的身份验证类型: {}'.format(e))
            if e.find('Connection reset by peer') != -1:
                self.debug('目标服务器主动拒绝连接')
                return self.returnMsg(False, '目标服务器主动拒绝连接')
            if e.find('Error reading SSH protocol banner') != -1:
                self.debug('协议头响应超时')
                return self.returnMsg(False, '协议头响应超时，与目标服务器之间的网络质量太糟糕：' + e)
            if not e:
                self.debug('SSH协议握手超时')
                return self.returnMsg(False, "SSH协议握手超时，与目标服务器之间的网络质量太糟糕")
            err = mw.getTracebackInfo()
            self.debug(err)
            return self.returnMsg(False, "未知错误: {}".format(err))

        self.debug('认证成功，正在构建会话通道')

        ssh = self.__tp.open_session()
        ssh.get_pty(term='xterm', width=100, height=34)
        ssh.invoke_shell()
        self.__ssh_list[sid] = ssh
        mw.writeLog(self.__log_type, '成功登录到SSH服务器 [{}:{}]'.format(
            self.__host, self.__port))
        self.debug('通道已构建')
        return self.returnMsg(True, '连接成功.')

    def getSshInfo(self, file):
        rdata = mw.readFile(file)
        destr = mw.enDoubleCrypt('mdserver-web', rdata)
        return json.loads(destr)

    def setAttr(self, sid, info):
        self.__host = info['host'].strip()

        # 外部连接获取
        if not self.__host in ['127.0.0.1', 'localhost']:
            dst_info = mw.getServerDir() + '/webssh/host/' + self.__host + '/info.json'
            if os.path.exists(dst_info):
                info = self.getSshInfo(dst_info)

        if 'type' in info:
            self.__type = info['type']

        if 'port' in info:
            self.__port = int(info['port'])
        if 'username' in info:
            self.__user = info['username']
        if 'pkey' in info:
            self.__pkey = info['pkey']
        if 'password' in info:
            self.__pass = info['password']
        if 'pkey_passwd' in info:
            self.__key_passwd = info['pkey_passwd']

        # print(self.__host, self.__pass, self.__key_passwd)
        try:
            result = self.connect(sid)
            # print(result)
        except Exception as ex:
            if str(ex).find("NoneType") == -1:
                raise ex
        return result

    def send(self):
        pass

    def close(self):
        try:
            if self.__ssh:
                self.__ssh.close()
            if self.__tp:  # 关闭宿主服务
                self.__tp.close()
            if self.__ps:
                self.__ps.close()
        except:
            pass

    def resize(self, sid, data):
        try:
            self.__ssh_list[sid].resize_pty(
                width=data['cols'], height=data['rows'])
            return True
        except:
            return False

    def wsSend(self, recv):
        try:
            t = recv.decode("utf-8")
            return emit('server_response', {'data': t})
        except Exception as e:
            return emit('server_response', {'data': recv})

    def wsSendConnect(self):
        return emit('connect', {'data': 'ok'})

    def wsSendReConnect(self):
        return emit('reconnect', {'data': 'ok'})

    def heartbeat(self):
        # limit_cos = 10
        while True:
            time.sleep(3)
            cur_time = time.time()
            for x in list(self.__ssh_list.keys()):
                ssh_last_time = self.__ssh_last_request_time[x]
                sid_off_cos = cur_time - ssh_last_time

                # print("heartbeat off cos :", x, sid_off_cos)
                if sid_off_cos > 3:
                    cur_ssh = self.__ssh_list[x]
                    if not cur_ssh:
                        del(self.__ssh_list[x])
                        del(self.__ssh_last_request_time[x])
                        continue

                    if cur_ssh.exit_status_ready():
                        del(self.__ssh_list[x])
                        del(self.__ssh_last_request_time[x])
                        continue

                    cur_ssh.send("exit\r\n")
                    del(self.__ssh_list[x])
                    del(self.__ssh_last_request_time[x])

    def run(self, sid, info):
        self.__sid = sid
        if not self.__sid:
            return self.wsSend('WebSocketIO无效')

        self.__ssh_last_request_time[sid] = time.time()
        if not sid in self.__ssh_list:
            if type(info) == dict and 'host' in info:
                result = self.setAttr(sid, info)
                if result['status']:
                    return self.wsSendConnect()
                else:
                    return self.wsSend(result['msg'])
            else:
                return self.wsSendReConnect()

        result = self.returnMsg(False, '')
        if sid in self.__ssh_list:
            if 'resize' in info:
                self.resize(sid, info)
            result = self.returnMsg(True, '已连接')
            if result['status']:
                if type(info) == str:
                    time.sleep(0.1)
                    cur_ssh = self.__ssh_list[sid]
                    if cur_ssh.exit_status_ready():
                        self.wsSend("logout\r\n")
                        del(self.__ssh_list[sid])
                        return
                    cur_ssh.send(info)
                    try:
                        time.sleep(0.005)
                        recv = cur_ssh.recv(8192)
                        return self.wsSend(recv)
                    except Exception as ex:
                        return self.wsSend('')
            else:
                return self.wsSend(result['msg'])
