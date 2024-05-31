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


class ssh_local(object):

    __debug_file = 'logs/ssh_local.log'
    __log_type = 'SSH终端'

    __ssh = None

    # lock
    _instance_lock = threading.Lock()

    def __init__(self):
        pass

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(ssh_local, "_instance"):
            with ssh_local._instance_lock:
                if not hasattr(ssh_local, "_instance"):
                    ssh_local._instance = ssh_local(*args, **kwargs)
        return ssh_local._instance

    def debug(self, msg):
        msg = "{} - {}:{} => {} \n".format(mw.formatDate(),
                                           self.__host, self.__port, msg)
        if not mw.isDebugMode():
            return
        mw.writeFile(self.__debug_file, msg, 'a+')

    def returnMsg(self, status, msg):
        return {'status': status, 'msg': msg}


    def connectSsh(self):
        import paramiko
        ssh = paramiko.SSHClient()
        mw.createSshInfo()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        port = mw.getSSHPort()
        try:
            ssh.connect('127.0.0.1', port, timeout=5)
        except Exception as e:
            ssh.connect('localhost', port, timeout=5)
        except Exception as e:
            ssh.connect(mw.getHostAddr(), port, timeout=30)
        except Exception as e:
            return False

        shell = ssh.invoke_shell(term='xterm', width=83, height=21)
        shell.setblocking(0)
        return shell

    def send(self):
        pass

    def close(self):
        try:
            if self.__ssh:
                self.__ssh.close()
        except:
            pass

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


    def run(self, info):
        if not self.__ssh:
            self.__ssh = self.connectSsh()

        if self.__ssh.exit_status_ready():
            self.__ssh = self.connectSsh()

        self.__ssh.send(info)
        try:
            time.sleep(0.005)
            recv = self.__ssh.recv(8192)
            return self.wsSend(recv)
        except Exception as ex:
            return self.wsSend('')
