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


class crontab_api:

    field = 'id,name,type,where1,where_hour,where_minute,echo,addtime,status,save,backup_to,stype,sname,sbody,urladdress'

    def __init__(self):
        pass

    ##### ----- start ----- ###
    def listApi(self):
        _list = public.M('crontab').where('', ()).field(self.field).limit(
            '0,5').order('id desc').select()

        data = []
        for i in range(len(_list)):
            tmp = _list[i]
            if _list[i]['type'] == "day":
                tmp['type'] = '每天'
                tmp['cycle'] = public.getInfo('每天, {1}点{2}分 执行', (str(
                    _list[i]['where_hour']), str(_list[i]['where_minute'])))
            elif _list[i]['type'] == "day-n":
                tmp['type'] = public.getInfo(
                    '每{1}天', (str(_list[i]['where1']),))
                tmp['cycle'] = public.getInfo('每隔{1}天, {2}点{3}分 执行',  (str(
                    _list[i]['where1']), str(_list[i]['where_hour']), str(_list[i]['where_minute'])))
            elif _list[i]['type'] == "hour":
                tmp['type'] = '每小时'
                tmp['cycle'] = public.getInfo(
                    '每小时, 第{1}分钟 执行', (str(_list[i]['where_minute']),))
            elif _list[i]['type'] == "hour-n":
                tmp['type'] = public.getInfo(
                    '每{1}小时', (str(_list[i]['where1']),))
                tmp['cycle'] = public.getInfo('每{1}小时, 第{2}分钟 执行', (str(
                    _list[i]['where1']), str(_list[i]['where_minute'])))
            elif _list[i]['type'] == "minute-n":
                tmp['type'] = public.getInfo(
                    '每{1}分钟', (str(_list[i]['where1']),))
                tmp['cycle'] = public.getInfo(
                    '每隔{1}分钟执行', (str(_list[i]['where1']),))
            elif _list[i]['type'] == "week":
                tmp['type'] = '每周'
                if not _list[i]['where1']:
                    _list[i]['where1'] = '0'
                tmp['cycle'] = public.getInfo('每周{1}, {2}点{3}分执行', (self.toWeek(int(
                    _list[i]['where1'])), str(_list[i]['where_hour']), str(_list[i]['where_minute'])))
            elif _list[i]['type'] == "month":
                tmp['type'] = '每月'
                tmp['cycle'] = public.getInfo('每月, {1}日 {2}点{3}分执行', (str(_list[i]['where1']), str(
                    _list[i]['where_hour']), str(_list[i]['where_minute'])))
            data.append(tmp)

        _ret = {}
        _ret['data'] = data

        count = public.M('crontab').where('', ()).count()
        _page = {}
        _page['count'] = count
        _page['tojs'] = 'remind'

        _ret['page'] = public.getPage(_page)
        return public.getJson(_ret)

    # 获取指定任务数据
    def getCrondFindApi(self):
        sid = request.form.get('id', '')
        data = public.M('crontab').where(
            'id=?', (sid,)).field(self.field).find()
        return public.getJson(data)

    def modifyCrondApi(self):
        sid = request.form.get('id', '')
        iname = request.form.get('name', '')
        field_type = request.form.get('type', '')
        week = request.form.get('week', '')
        where1 = request.form.get('where1', '')
        hour = request.form.get('hour', '')
        minute = request.form.get('minute', '')
        save = request.form.get('save', '')
        backup_to = request.form.get('backup_to', '')
        stype = request.form.get('stype', '')
        sname = request.form.get('sname', '')
        sbody = request.form.get('sbody', '')
        urladdress = request.form.get('urladdress', '')

        if len(iname) < 1:
            return public.returnJson(False, '任务名称不能为空!')

        params = {
            'name': iname,
            'type': field_type,
            'week': week,
            'where1': where1,
            'hour': hour,
            'minute': minute,
            'save': save,
            'backup_to': backup_to,
            'stype': stype,
            'sname': sname,
            'sbody': sbody,
            'urladdress': urladdress,
        }
        cuonConfig, get, name = self.getCrondCycle(params)
        cronInfo = public.M('crontab').where(
            'id=?', (sid,)).field(self.field).find()
        del(cronInfo['id'])
        del(cronInfo['addtime'])
        cronInfo['name'] = get['name']
        cronInfo['type'] = get['type']
        cronInfo['where1'] = get['where1']
        cronInfo['where_hour'] = get['hour']
        cronInfo['where_minute'] = get['minute']
        cronInfo['save'] = get['save']
        cronInfo['backup_to'] = get['backup_to']
        cronInfo['sbody'] = get['sbody']
        cronInfo['urladdress'] = get['urladdress']

        addData = public.M('crontab').where('id=?', (sid,)).save('name,type,where1,where_hour,where_minute,save,backup_to,sbody,urladdress', (get[
            'name'], field_type, get['where1'], get['hour'], get['minute'], get['save'], get['backup_to'], get['sbody'], get['urladdress']))

        self.removeForCrond(cronInfo['echo'])
        self.syncToCrond(cronInfo)
        public.writeLog('计划任务', '修改计划任务[' + cronInfo['name'] + ']成功')
        return public.returnJson(True, '修改成功')

    def logsApi(self):
        sid = request.form.get('id', '')
        echo = public.M('crontab').where("id=?", (sid,)).field('echo').find()
        logFile = public.getServerDir() + '/cron/' + echo['echo'] + '.log'
        if not os.path.exists(logFile):
            return public.returnJson(False, '当前日志为空!')
        log = public.getNumLines(logFile, 2000)
        return public.returnJson(True, log)

    def addApi(self):
        iname = request.form.get('name', '')
        field_type = request.form.get('type', '')
        week = request.form.get('week', '')
        where1 = request.form.get('where1', '')
        hour = request.form.get('hour', '')
        minute = request.form.get('minute', '')
        save = request.form.get('save', '')
        backup_to = request.form.get('backupTo', '')
        stype = request.form.get('sType', '')
        sname = request.form.get('sName', '')
        sbody = request.form.get('sBody', '')
        urladdress = request.form.get('urladdress', '')

        if len(iname) < 1:
            return public.returnJson(False, '任务名称不能为空!')

        params = {
            'name': iname,
            'type': field_type,
            'week': week,
            'where1': where1,
            'hour': hour,
            'minute': minute,
            'save': save,
            'backup_to': backup_to,
            'stype': stype,
            'sname': sname,
            'sbody': sbody,
            'urladdress': urladdress,
        }

        # print params
        cuonConfig, get, name = self.getCrondCycle(params)
        cronPath = public.getServerDir() + '/cron'

        cronName = self.getShell(params)
        # print cuonConfig, _params, name
        # print cronPath, cronName
        # print stype

        if type(cronName) == dict:
            return cronName

        cuonConfig += ' ' + cronPath + '/' + cronName + \
            ' >> ' + cronPath + '/' + cronName + '.log 2>&1'
        wRes = self.writeShell(cuonConfig)

        if type(wRes) != bool:
            return wRes

        self.crondReload()
        addData = public.M('crontab').add('name,type,where1,where_hour,where_minute,echo,addtime,status,save,backup_to,stype,sname,sbody,urladdress', (iname, field_type, where1, hour, minute, cronName, time.strftime(
            '%Y-%m-%d %X', time.localtime()), 1, save, backup_to, stype, sname, sbody, urladdress))

        if addData > 0:
            return public.returnJson(True, '添加成功')
        return public.returnJson(False, '添加失败')

    def startTaskApi(self):
        sid = request.form.get('id', '')
        echo = public.M('crontab').where('id=?', (sid,)).getField('echo')
        execstr = public.getServerDir() + '/cron/' + echo
        os.system('chmod +x ' + execstr)
        os.system('nohup ' + execstr + ' >> ' + execstr + '.log 2>&1 &')
        return public.returnJson(True, '任务已执行!')

    def delApi(self):
        sid = request.form.get('id', '')
        try:
            find = public.M('crontab').where(
                "id=?", (sid,)).field('name,echo').find()
            if not self.removeForCrond(find['echo']):
                return public.returnJson(False, '无法写入文件，请检查是否开启了系统加固功能!')

            cronPath = public.getServerDir() + '/cron'
            sfile = cronPath + '/' + find['echo']

            if os.path.exists(sfile):
                os.remove(sfile)
            sfile = cronPath + '/' + find['echo'] + '.log'
            if os.path.exists(sfile):
                os.remove(sfile)

            public.M('crontab').where("id=?", (sid,)).delete()
            public.writeLog('计划任务', public.getInfo(
                '删除计划任务[{1}]成功!', (find['name'],)))
            return public.returnJson(True, '删除成功')
        except Exception as e:
            return public.returnJson(False, '删除失败:' + str(e))

    def delLogsApi(self):
        sid = request.form.get('id', '')
        try:
            echo = public.M('crontab').where("id=?", (sid,)).getField('echo')
            logFile = public.getServerDir() + '/cron/' + echo + '.log'
            os.remove(logFile)
            return public.returnJson(True, '任务日志已清空!')
        except:
            return public.returnJson(False, '任务日志清空失败!')
    ##### ----- start ----- ###

    # 转换大写星期
    def toWeek(self, num):
        wheres = {
            0:   '日',
            1:   '一',
            2:   '二',
            3:   '三',
            4:   '四',
            5:   '五',
            6:   '六'
        }
        try:
            return wheres[num]
        except:
            return ''

    def getCrondCycle(self, params):
        cuonConfig = ''
        name = ''
        if params['type'] == "day":
            cuonConfig = self.getDay(params)
            name = '每天'
        elif params['type'] == "day-n":
            cuonConfig = self.getDay_N(params)
            name = public.getInfo('每{1}天', (params['where1'],))
        elif params['type'] == "hour":
            cuonConfig = self.getHour(params)
            name = '每小时'
        elif params['type'] == "hour-n":
            cuonConfig = self.getHour_N(params)
            name = '每小时'
        elif params['type'] == "minute-n":
            cuonConfig = self.minute_N(params)
        elif params['type'] == "week":
            params['where1'] = params['week']
            cuonConfig = self.week(params)
        elif params['type'] == "month":
            cuonConfig = self.month(params)
        return cuonConfig, params, name

    # 取任务构造Day
    def getDay(self, param):
        cuonConfig = "{0} {1} * * * ".format(param['minute'], param['hour'])
        return cuonConfig
    # 取任务构造Day_n

    def getDay_N(self, param):
        cuonConfig = "{0} {1} */{2} * * ".format(
            param['minute'], param['hour'], param['where1'])
        return cuonConfig

    # 取任务构造Hour
    def getHour(self, param):
        cuonConfig = "{0} * * * * ".format(param['minute'])
        return cuonConfig

    # 取任务构造Hour-N
    def getHour_N(self, param):
        cuonConfig = "{0} */{1} * * * ".format(
            param['minute'], param['where1'])
        return cuonConfig

    # 取任务构造Minute-N
    def minute_N(self, param):
        cuonConfig = "*/{0} * * * * ".format(param['where1'])
        return cuonConfig

    # 取任务构造week
    def week(self, param):
        cuonConfig = "{0} {1} * * {2}".format(
            param['minute'], param['hour'], param['week'])
        return cuonConfig

    # 取任务构造Month
    def month(self, param):
        cuonConfig = "{0} {1} {2} * * ".format(
            param['minute'], param['hour'], param['where1'])
        return cuonConfig

    # 取执行脚本
    def getShell(self, param):
        # try:
        stype = param['stype']
        if stype == 'toFile':
            shell = param.sFile
        else:
            head = "#!/bin/bash\nPATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin\nexport PATH\n"
            log = '.log'

            wheres = {
                'path': head + "python " + public.getServerDir() + "/panel/script/backup.py path " + param['sname'] + " " + str(param['save']),
                'site':   head + "python " + public.getServerDir() + "/panel/script/backup.py site " + param['sname'] + " " + str(param['save']),
                'database': head + "python " + public.getServerDir() + "/panel/script/backup.py database " + param['sname'] + " " + str(param['save']),
                'logs':   head + "python " + public.getServerDir() + "/panel/script/logsBackup " + param['sname'] + log + " " + str(param['save']),
                'rememory': head + "/bin/bash " + public.getServerDir() + '/panel/script/rememory.sh'
            }
            if param['backup_to'] != 'localhost':
                cfile = public.getServerDir() + "/panel/plugin/" + param[
                    'backup_to'] + "/" + param['backup_to'] + "_main.py"
                if not os.path.exists(cfile):
                    cfile = public.getServerDir() + "/panel/script/backup_" + \
                        param['backup_to'] + ".py"
                wheres = {
                    'path': head + "python " + cfile + " path " + param['sname'] + " " + str(param['save']),
                    'site':   head + "python " + cfile + " site " + param['sname'] + " " + str(param['save']),
                    'database': head + "python " + cfile + " database " + param['sname'] + " " + str(param['save']),
                    'logs':   head + "python " + public.getServerDir() + "/panel/script/logsBackup " + param['sname'] + log + " " + str(param['save']),
                    'rememory': head + "/bin/bash " + public.getServerDir() + '/panel/script/rememory.sh'
                }

            try:
                shell = wheres[stype]
            except:
                if stype == 'toUrl':
                    shell = head + "curl -sS --connect-timeout 10 -m 60 '" + \
                        param['urladdress'] + "'"
                else:
                    shell = head + param['sbody'].replace("\r\n", "\n")

                shell += '''
echo "----------------------------------------------------------------------------"
endDate=`date +"%Y-%m-%d %H:%M:%S"`
echo "★[$endDate] Successful"
echo "----------------------------------------------------------------------------"
'''
        cronPath = public.getServerDir() + '/cron'
        if not os.path.exists(cronPath):
            public.execShell('mkdir -p ' + cronPath)
        if not 'echo' in param:
            cronName = public.md5(public.md5(str(time.time()) + '_mw'))
        else:
            cronName = param['echo']
        file = cronPath + '/' + cronName
        public.writeFile(file, self.checkScript(shell))
        public.execShell('chmod 750 ' + file)
        return cronName

    # 检查脚本
    def checkScript(self, shell):
        keys = ['shutdown', 'init 0', 'mkfs', 'passwd',
                'chpasswd', '--stdin', 'mkfs.ext', 'mke2fs']
        for key in keys:
            shell = shell.replace(key, '[***]')
        return shell

    # 将Shell脚本写到文件
    def writeShell(self, config):
        u_file = '/var/spool/cron/crontabs/root'
        if not os.path.exists(u_file):
            file = '/var/spool/cron/root'
            if public.isAppleSystem():
                file = '/etc/crontab'
        else:
            file = u_file

        if not os.path.exists(file):
            public.writeFile(file, '')
        conf = public.readFile(file)
        conf += config + "\n"
        if public.writeFile(file, conf):
            if not os.path.exists(u_file):
                public.execShell("chmod 600 '" + file +
                                 "' && chown root.root " + file)
            else:
                public.execShell("chmod 600 '" + file +
                                 "' && chown root.crontab " + file)
            return True
        return public.returnJson(False, '文件写入失败,请检查是否开启系统加固功能!')

    # 重载配置
    def crondReload(self):
        if public.isAppleSystem():
            if os.path.exists('/etc/crontab'):
                pass
                # public.execShell('/usr/sbin/cron restart')
        else:
            if os.path.exists('/etc/init.d/crond'):
                public.execShell('/etc/init.d/crond reload')
            elif os.path.exists('/etc/init.d/cron'):
                public.execShell('service cron restart')
            else:
                public.execShell("systemctl reload crond")

    # 从crond删除
    def removeForCrond(self, echo):
        u_file = '/var/spool/cron/crontabs/root'
        if not os.path.exists(u_file):
            file = '/var/spool/cron/root'
            if public.isAppleSystem():
                file = '/etc/crontab'
        else:
            file = u_file
        conf = public.readFile(file)
        rep = ".+" + str(echo) + ".+\n"
        conf = re.sub(rep, "", conf)
        if not public.writeFile(file, conf):
            return False
        self.crondReload()
        return True

    def syncToCrond(self, cronInfo):
        if 'status' in cronInfo:
            if cronInfo['status'] == 0:
                return False
        if 'where_hour' in cronInfo:
            cronInfo['hour'] = cronInfo['where_hour']
            cronInfo['minute'] = cronInfo['where_minute']
            cronInfo['week'] = cronInfo['where1']
        cuonConfig, cronInfo, name = self.getCrondCycle(cronInfo)
        cronPath = public.getServerDir() + '/cron'
        cronName = self.getShell(cronInfo)
        if type(cronName) == dict:
            return cronName
        cuonConfig += ' ' + cronPath + '/' + cronName + \
            ' >> ' + cronPath + '/' + cronName + '.log 2>&1'
        wRes = self.writeShell(cuonConfig)
        if type(wRes) != bool:
            return False
        self.crondReload()
