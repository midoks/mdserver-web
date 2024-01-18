# coding: utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------
# 日志类操作
# ---------------------------------------------------------------------------------

import psutil
import time
import os
import sys
import mw
import re
import json
import pwd

from datetime import datetime
from flask import request


class logs_api:

    __months = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                'Jul': '07', 'Aug': '08', 'Sep': '09', 'Sept': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}

    def __init__(self):
        pass

    def delPanelLogsApi(self):
        mw.M('logs').where('id>?', (0,)).delete()
        mw.writeLog('面板设置', '面板操作日志已清空!')
        return mw.returnJson(True, '面板操作日志已清空!')

    def getLogListApi(self):
        p = request.form.get('p', '1').strip()
        limit = request.form.get('limit', '10').strip()
        search = request.form.get('search', '').strip()
        return self.getLogList(int(p), int(limit), search)

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

    def getLogsTitle(self, log_name):
        log_name = log_name.replace('.1', '')
        if log_name in ['mw-update.log']:
            return '面板更新日志'
        if log_name in ['mw-install.log']:
            return '面板安装日志'
        if log_name in ['auth.log', 'secure'] or log_name.find('auth.') == 0:
            return '授权日志'
        if log_name in ['dmesg'] or log_name.find('dmesg') == 0:
            return '内核缓冲区日志'
        if log_name in ['syslog'] or log_name.find('syslog') == 0:
            return '系统日志'
        if log_name in ['rsyncd.log']:
            return '远程同步日志'
        if log_name in ['btmp']:
            return '失败的登录记录'
        if log_name in ['utmp', 'wtmp']:
            return '登录和重启记录'
        if log_name in ['lastlog']:
            return '用户最后登录'
        if log_name in ['yum.log']:
            return 'yum包管理器日志'
        if log_name in ['anaconda.log']:
            return 'Anaconda日志'
        if log_name in ['dpkg.log']:
            return 'dpkg日志'
        if log_name in ['daemon.log']:
            return '系统后台守护进程日志'
        if log_name in ['boot.log']:
            return '启动日志'
        if log_name in ['kern.log']:
            return '内核日志'
        if log_name in ['maillog', 'mail.log']:
            return '邮件日志'
        if log_name.find('Xorg') == 0:
            return 'Xorg日志'
        if log_name in ['cron.log']:
            return '定时任务日志'
        if log_name in ['alternatives.log']:
            return '更新替代信息'
        if log_name in ['debug']:
            return '调试信息'
        if log_name.find('apt') == 0:
            return 'apt-get相关日志'
        if log_name.find('installer') == 0:
            return '系统安装相关日志'
        if log_name in ['messages']:
            return '综合日志'
        return '{}日志'.format(log_name.split('.')[0])

    def getAuditLogsFilesApi(self):
        log_dir = '/var/log'
        log_files = []
        for log_file in os.listdir(log_dir):
            log_suffix = log_file.split('.')[-1:]
            if log_suffix[0] in ['gz', 'xz', 'bz2', 'asl']:
                continue

            if log_file in ['.', '..', 'faillog', 'fontconfig.log', 'unattended-upgrades', 'tallylog']:
                continue

            filename = os.path.join(log_dir, log_file)
            if os.path.isfile(filename):
                file_size = os.path.getsize(filename)
                if not file_size:
                    continue

                tmp = {
                    'name': log_file,
                    'size': file_size,
                    'log_file': filename,
                    'title': self.getLogsTitle(log_file),
                    'uptime': os.path.getmtime(filename)
                }

                log_files.append(tmp)
            else:
                for next_name in os.listdir(filename):
                    if next_name[-3:] in ['.gz', '.xz']:
                        continue
                    next_file = os.path.join(filename, next_name)
                    if not os.path.isfile(next_file):
                        continue
                    file_size = os.path.getsize(next_file)
                    if not file_size:
                        continue
                    log_name = '{}/{}'.format(log_file, next_name)
                    tmp = {
                        'name': log_name,
                        'size': file_size,
                        'log_file': next_file,
                        'title': self.getLogsTitle(log_name),
                        'uptime': os.path.getmtime(next_file)
                    }
                    log_files.append(tmp)
        log_files = sorted(log_files, key=lambda x: x['name'], reverse=True)
        return mw.getJson(log_files)

    def getAuditFileApi(self):
        log_name = request.form.get('log_name', '').strip()
        return self.getAuditLogsName(log_name)

    def __to_date2(self, date_str):
        tmp = date_str.split()
        s_date = str(tmp[-1]) + '-' + self.__months.get(tmp[1],
                                                        tmp[1]) + '-' + tmp[2] + ' ' + tmp[3]
        return s_date

    def __to_date3(self, date_str):
        tmp = date_str.split()
        s_date = str(datetime.now().year) + '-' + \
            self.__months.get(tmp[1], tmp[1]) + '-' + tmp[2] + ' ' + tmp[3]
        return s_date

    def __to_date4(self, date_str):
        tmp = date_str.split()
        s_date = str(datetime.now().year) + '-' + \
            self.__months.get(tmp[0], tmp[0]) + '-' + tmp[1] + ' ' + tmp[2]
        return s_date

    def getAuditLast(self, log_name):
        # 获取日志
        cmd = '''LANG=en_US.UTF-8 last -n 200 -x -f {} |grep -v 127.0.0.1|grep -v " begins"'''.format(
            '/var/log/' + log_name)
        result = mw.execShell(cmd)
        lastlog_list = []
        for _line in result[0].split("\n"):
            if not _line:
                continue
            tmp = {}
            sp_arr = _line.split()
            tmp['用户'] = sp_arr[0]
            if sp_arr[0] == 'runlevel':
                tmp['来源'] = sp_arr[4]
                tmp['端口'] = ' '.join(sp_arr[1:4])
                tmp['时间'] = self.__to_date3(
                    ' '.join(sp_arr[5:])) + ' ' + ' '.join(sp_arr[-2:])
            elif sp_arr[0] in ['reboot', 'shutdown']:
                tmp['来源'] = sp_arr[3]
                tmp['端口'] = ' '.join(sp_arr[1:3])
                if sp_arr[-3] == '-':
                    tmp['时间'] = self.__to_date3(
                        ' '.join(sp_arr[4:])) + ' ' + ' '.join(sp_arr[-3:])
                else:
                    tmp['时间'] = self.__to_date3(
                        ' '.join(sp_arr[4:])) + ' ' + ' '.join(sp_arr[-2:])
            elif sp_arr[1] in ['tty1', 'tty', 'tty2', 'tty3', 'hvc0', 'hvc1', 'hvc2'] or len(sp_arr) == 9:
                tmp['来源'] = ''
                tmp['端口'] = sp_arr[1]
                tmp['时间'] = self.__to_date3(
                    ' '.join(sp_arr[2:])) + ' ' + ' '.join(sp_arr[-3:])
            else:
                tmp['来源'] = sp_arr[2]
                tmp['端口'] = sp_arr[1]
                tmp['时间'] = self.__to_date3(
                    ' '.join(sp_arr[3:])) + ' ' + ' '.join(sp_arr[-3:])

            # tmp['_line'] = _line
            lastlog_list.append(tmp)
        # lastlog_list = sorted(lastlog_list,key=lambda x:x['时间'],reverse=True)
        return mw.returnData(True, 'ok!', lastlog_list)

    def getAuditLastLog(self):
        cmd = '''LANG=en_US.UTF-8 lastlog|grep -v Username'''
        result = mw.execShell(cmd)
        lastlog_list = []
        for _line in result[0].split("\n"):
            if not _line:
                continue
            tmp = {}
            sp_arr = _line.split()
            tmp['用户'] = sp_arr[0]
            # tmp['_line'] = _line
            if _line.find('Never logged in') != -1:
                tmp['最后登录时间'] = '0'
                tmp['最后登录来源'] = '-'
                tmp['最后登录端口'] = '-'
                lastlog_list.append(tmp)
                continue
            tmp['最后登录来源'] = sp_arr[2]
            tmp['最后登录端口'] = sp_arr[1]
            tmp['最后登录时间'] = self.__to_date2(' '.join(sp_arr[3:]))

            lastlog_list.append(tmp)
        lastlog_list = sorted(lastlog_list, key=lambda x: x[
                              '最后登录时间'], reverse=True)
        for i in range(len(lastlog_list)):
            if lastlog_list[i]['最后登录时间'] == '0':
                lastlog_list[i]['最后登录时间'] = '从未登录过'
        return mw.returnData(True, 'ok!', lastlog_list)

    def parseAuditFile(self, log_name, result):
        log_list = []
        is_string = True
        for _line in result.split("\n"):
            if not _line.strip():
                continue
            if log_name.find('sa/sa') == -1:
                if _line[:3] in self.__months:
                    _msg = _line[16:]
                    _tmp = _msg.split(": ")
                    _act = ''
                    if len(_tmp) > 1:
                        _act = _tmp[0]
                        _msg = _tmp[1]
                    else:
                        _msg = _tmp[0]
                    _line = {
                        "时间": self.__to_date4(_line[:16].strip()),
                        "角色": _act,
                        "事件": _msg
                    }
                    is_string = False
                elif _line[:2] in ['19', '20', '21', '22', '23', '24']:
                    _msg = _line[19:]
                    _tmp = _msg.split(" ")
                    _act = _tmp[1]
                    _msg = ' '.join(_tmp[2:])
                    _line = {
                        "时间": _line[:19].strip(),
                        "角色": _act,
                        "事件": _msg
                    }
                    is_string = False
                elif log_name.find('alternatives') == 0:
                    _tmp = _line.split(": ")
                    _last = _tmp[0].split(" ")
                    _act = _last[0]
                    _msg = ' '.join(_tmp[1:])
                    _line = {
                        "时间": ' '.join(_last[1:]).strip(),
                        "角色": _act,
                        "事件": _msg
                    }
                    is_string = False
                else:
                    if not is_string:
                        if type(_line) != dict:
                            continue

            log_list.append(_line)

        return log_list

    def getAuditLogsName(self, log_name):
        # print(log_name)
        if log_name in ['wtmp', 'btmp', 'utmp'] or log_name.find('wtmp') == 0 or log_name.find('btmp') == 0 or log_name.find('utmp') == 0:
            return self.getAuditLast(log_name)

        if log_name.find('lastlog') == 0:
            return self.getAuditLastLog()

        if log_name.find('sa/sa') == 0:
            if log_name.find('sa/sar') == -1:
                return mw.execShell("sar -f /var/log/{}".format(log_name))[0]
        log_dir = '/var/log'
        log_file = log_dir + '/' + log_name
        if not os.path.exists(log_file):
            return mw.returnData(False, '日志文件不存在!')
        result = mw.getLastLine(log_file, 100)
        try:
            log_list = self.parseAuditFile(log_name, result)
            _string = []
            _dict = []
            _list = []
            for _line in log_list:
                if isinstance(_line, str):
                    _string.append(_line.strip())
                elif isinstance(_line, dict):
                    _dict.append(_line)
                elif isinstance(_line, list):
                    _list.append(_line)
                else:
                    continue
            _str_len = len(_string)
            _dict_len = len(_dict)
            _list_len = len(_list)
            if _str_len > _dict_len + _list_len:
                return "\n".join(_string)
            elif _dict_len > _str_len + _list_len:
                return mw.returnData(True, 'ok!', _dict)
            else:
                return mw.returnData(True, 'ok!', _list)

        except:
            return mw.returnData(True, 'ok!', result)
