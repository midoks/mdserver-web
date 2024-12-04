# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os
import sys
import re
import time
import json
import threading
import multiprocessing

import core.mw as mw
import thisdb


class crontab(object):
        # lock
    _instance_lock = threading.Lock()

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(crontab, "_instance"):
            with crontab._instance_lock:
                if not hasattr(crontab, "_instance"):
                    crontab._instance = crontab(*args, **kwargs)
        return crontab._instance

    def modifyCrond(self,cron_id,data):
        if len(data['name']) < 1:
            return mw.returnData(False, '任务名称不能为空!')

        is_check_pass, msg = self.cronCheck(data)
        if not is_check_pass:
            return mw.returnData(is_check_pass, msg)

        info = thisdb.getCrond(cron_id)

        dbdata = {}
        dbdata['name'] = data['name']
        dbdata['type'] = data['type']
        dbdata['where1'] = data['where1']
        dbdata['where_hour'] = data['hour']
        dbdata['where_minute'] = data['minute']
        dbdata['save'] = data['save']
        dbdata['backup_to'] = data['backup_to']
        dbdata['sname'] = data['sname']
        dbdata['sbody'] = data['sbody']
        dbdata['stype'] = data['stype']
        dbdata['url_address'] = data['url_address']

        if not self.removeForCrond(info['echo']):
            return mw.returnData(False, '无法写入文件，是否开启了系统加固功能!')

        thisdb.setCrontabData(cron_id, dbdata)
        self.syncToCrond(cron_id)
        msg = '修改计划任务[' + data['name'] + ']成功'
        mw.writeLog('计划任务', msg)
        return mw.returnData(True, msg)

    # 取数据列表
    def getDataList(self,stype=''):
    
        bak_data = []
        if stype == 'site' or stype == 'sites' or stype == 'database' or stype.find('database_') > -1 or stype == 'path':
            bak_data = thisdb.getOptionByJson('hook_backup',type='hook', default=[])

        if stype == 'database' or stype.find('database_') > -1:
            sqlite3_name = 'mysql'
            path = mw.getServerDir() + '/mysql'
            if stype != 'database':
                soft_name = stype.replace('database_', '')
                path = mw.getServerDir() + '/' + soft_name

                if soft_name == 'postgresql':
                    sqlite3_name = 'pgsql'

                if soft_name == 'mongodb':
                    sqlite3_name = 'mongodb'

            db_list = {}
            db_list['orderOpt'] = bak_data

            if not os.path.exists(path + '/' + sqlite3_name + '.db'):
                db_list['data'] = []
            else:
                db_list['data'] = mw.M('databases').dbPos(path, sqlite3_name).field('name,ps').select()
            return db_list

        if stype == 'path':
            db_list = {}
            db_list['data'] = [{"name": mw.getWwwDir(), "ps": "www"}]
            db_list['orderOpt'] = bak_data
            return db_list

        data = {}
        data['orderOpt'] = bak_data

        default_db = 'sites'
        data['data'] = mw.M(default_db).field('name,ps').select()
        return data

    def setCronStatus(self,cron_id):
        data = thisdb.getCrond(cron_id)

        status = 1
        status_msg = '开启'
        if data['status'] == status:
            status = 0
            status_msg = '关闭'
            self.removeForCrond(data['echo'])
        else:
            data['status'] = 1
            self.syncToCrond(cron_id)

        thisdb.setCrontabStatus(cron_id, status)

        msg = '修改计划任务[' + data['name'] + ']状态为[' + str(status_msg) + ']'
        mw.writeLog('计划任务', msg)
        return mw.returnJson(True, msg)


    def cronLog(self, cron_id):
        data = thisdb.getCrond(cron_id)
        log_file = mw.getServerDir() + '/cron/' + data['echo'] + '.log'
        if not os.path.exists(log_file):
            return mw.returnData(False, '当前日志为空!')
        content = mw.getLastLine(log_file, 500)
        return mw.returnData(True, content)

    def startTask(self, cron_id):
        data = thisdb.getCrond(cron_id)
        cmd_file = mw.getServerDir() + '/cron/' + data['echo']
        os.system('chmod +x ' + cmd_file)
        os.system('nohup ' + cmd_file + ' >> ' + cmd_file + '.log 2>&1 &')
        return mw.returnData(True, '计划任务【%s】已执行!' % data['name'])


    # 获取指定任务数据
    def getCrondFind(self, cron_id):
        return thisdb.getCrond(cron_id)

    def add(self, data):
        if len(data['name']) < 1:
            # 任务名称不能为空
            return -1

        is_check_pass, msg = self.cronCheck(data)
        if not is_check_pass:
            return mw.returnData(is_check_pass, msg)

        cmd, title = self.getCrondCycle(data)
        cron_path = mw.getServerDir() + '/cron'
        cron_name = self.getShell(data)

        cmd += ' ' + cron_path + '/' + cron_name + ' >> ' + cron_path + '/' + cron_name + '.log 2>&1'

        if not mw.isAppleSystem():
            sh_data = self.writeShell(cmd)
            if not sh_data['status']:
                return sh_data
            self.crondReload()

        add_dbdata = {}
        add_dbdata['name'] = data['name']
        add_dbdata['type'] = data['type']
        add_dbdata['where1'] = data['where1']
        add_dbdata['where_hour'] = data['hour']
        add_dbdata['where_minute'] = data['minute']
        add_dbdata['save'] = data['save']
        add_dbdata['backup_to'] = data['backup_to']
        add_dbdata['sname'] = data['sname']
        add_dbdata['sbody'] = data['sbody']
        add_dbdata['stype'] = data['stype']
        add_dbdata['echo'] = cron_name
        add_dbdata['url_address'] = data['url_address']

        tid = thisdb.addCrontab(add_dbdata)
        return tid

    def delete(self, tid):
        data = thisdb.getCrond(tid)
        if not self.removeForCrond(data['echo']):
            return mw.returnData(False, '无法写入文件，是否开启了系统加固功能!')

        cron_path = mw.getServerDir() + '/cron'
        cron_file = cron_path + '/' + data['echo']

        if os.path.exists(cron_file):
            os.remove(cron_file)
        cron_file = cron_path + '/' + data['echo'] + '.log'
        if os.path.exists(cron_file):
            os.remove(cron_file)

        thisdb.deleteCronById(tid)
        msg = mw.getInfo('删除计划任务[{1}]成功!', (data['name'],))
        mw.writeLog('计划任务', msg)
        return mw.returnData(True, msg)


    def delLogs(self,cron_id):
        try:
            data = thisdb.getCrond(cron_id)
            log_file = mw.getServerDir() + '/cron/' + data['echo'] + '.log'
            if os.path.exists(log_file):
                os.remove(log_file)
            return mw.returnData(True, '任务日志已清空!')
        except:
            return mw.returnData(False, '任务日志清空失败!')

    def getCrontabHuman(self, data):
        rdata = []
        for i in range(len(data)):
            t = data[i]
            if t['type'] == "day":
                t['type'] = '每天'
                t['cycle'] = mw.getInfo('每天, {1}点{2}分 执行', (str(t['where_hour']), str(t['where_minute'])))
            elif t['type'] == "day-n":
                t['type'] = mw.getInfo('每{1}天', (str(t['where1']),))
                t['cycle'] = mw.getInfo('每隔{1}天, {2}点{3}分 执行',  (str(t['where1']), str(t['where_hour']), str(t['where_minute'])))
            elif t['type'] == "hour":
                t['type'] = '每小时'
                t['cycle'] = mw.getInfo('每小时, 第{1}分钟 执行', (str(t['where_minute']),))
            elif t['type'] == "hour-n":
                t['type'] = mw.getInfo('每{1}小时', (str(t['where1']),))
                t['cycle'] = mw.getInfo('每{1}小时, 第{2}分钟 执行', (str(t['where1']), str(t['where_minute'])))
            elif t['type'] == "minute-n":
                t['type'] = mw.getInfo('每{1}分钟', (str(t['where1']),))
                t['cycle'] = mw.getInfo('每隔{1}分钟执行', (str(t['where1']),))
            elif t['type'] == "week":
                t['type'] = '每周'
                if not t['where1']:
                    t['where1'] = '0'
                t['cycle'] = mw.getInfo('每周{1}, {2}点{3}分执行', (self.toWeek(int(t['where1'])), str(t['where_hour']), str(t['where_minute'])))
            elif t['type'] == "month":
                t['type'] = '每月'
                t['cycle'] = mw.getInfo('每月, {1}日 {2}点{3}分执行', (str(t['where1']), str(t['where_hour']), str(t['where_minute'])))
            rdata.append(t)
        return rdata

    # 从crond删除
    def removeForCrond(self, echo):
        if mw.isAppleSystem():
            return True

        cron_file = [
            '/var/spool/cron/crontabs/root',
            '/var/spool/cron/root',
        ]

        file = ''
        for i in cron_file:
            if os.path.exists(i):
                file = i


        if file == '':
            return False

        content = mw.readFile(file)
        rep = ".+" + str(echo) + ".+\n"
        content = re.sub(rep, "", content)
        if not mw.writeFile(file, content):
            return False
        self.crondReload()
        return True

    def getCrontabList(self,
        page = 1,
        size = 10
    ):
        info = thisdb.getCrontabList(page=int(page),size=int(size))

        rdata = {}
        rdata['data'] = self.getCrontabHuman(info['list'])
        rdata['page'] = mw.getPage({'count':info['count'],'tojs':'getCronData','p':page,'row':size})


        # backup hook
        rdata['backup_hook'] = thisdb.getOptionByJson('hook_backup', type='hook', default=[])
        return rdata

    def getCrondCycle(self, params):
        cron_cmd = ''
        title = ''
        if params['type'] == "day":
            cron_cmd = self.getDay(params)
            title = '每天'
        elif params['type'] == "day-n":
            cron_cmd = self.getDay_N(params)
            title = mw.getInfo('每{1}天', (params['where1'],))
        elif params['type'] == "hour":
            cron_cmd = self.getHour(params)
            title = '每小时'
        elif params['type'] == "hour-n":
            cron_cmd = self.getHour_N(params)
            title = '每小时'
        elif params['type'] == "minute-n":
            cron_cmd = self.minute_N(params)
        elif params['type'] == "week":
            params['where1'] = params['week']
            cron_cmd = self.week(params)
        elif params['type'] == "month":
            cron_cmd = self.month(params)
        return cron_cmd, title

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

    # 取任务构造Day
    def getDay(self, param):
        cmd = "{0} {1} * * * ".format(param['minute'], param['hour'])
        return cmd

    # 取任务构造Day_n
    def getDay_N(self, param):
        cmd = "{0} {1} */{2} * * ".format(param['minute'], param['hour'], param['where1'])
        return cmd

    # 取任务构造Hour
    def getHour(self, param):
        cmd = "{0} * * * * ".format(param['minute'])
        return cmd

    # 取任务构造Hour-N
    def getHour_N(self, param):
        cmd = "{0} */{1} * * * ".format(param['minute'], param['where1'])
        return cmd

    # 取任务构造Minute-N
    def minute_N(self, param):
        cmd = "*/{0} * * * * ".format(param['where1'])
        return cmd

    # 取任务构造week
    def week(self, param):
        cmd = "{0} {1} * * {2}".format(param['minute'], param['hour'], param['week'])
        return cmd

    # 取任务构造Month
    def month(self, param):
        cmd = "{0} {1} {2} * * ".format(param['minute'], param['hour'], param['where1'])
        return cmd

    # 参数校验
    def cronCheck(self, params):
        if params['stype'] == 'site' or params['stype'] == 'database' or params['stype'].find('database_') > -1 or params['stype'] == 'logs' or params['stype'] == 'path':
            if params['save'] == '':
                return False, '保留份数不能为空!'

        if params['type'] == 'day':
            if params['hour'] == '':
                return False, '小时不能为空!'
            if params['minute'] == '':
                return False, '分钟不能为空!'

        if params['type'] == 'day-n':
            if params['where1'] == '':
                return False, '天不能为空!'
            if params['hour'] == '':
                return False, '小时不能为空!'
            if params['minute'] == '':
                return False, '分钟不能为空!'
        if params['type'] == 'hour':
            if params['minute'] == '':
                return False, '分钟不能为空!'

        if params['type'] == 'hour-n':
            if params['where1'] == '':
                return False, '小时不能为空!'
            if params['minute'] == '':
                return False, '分钟不能为空!'

        if params['type'] == 'minute-n':
            if params['where1'] == '':
                return False, '分钟不能为空!'

        if params['type'] == 'week':
            if params['hour'] == '':
                return False, '小时不能为空!'
            if params['minute'] == '':
                return False, '分钟不能为空!'

        if params['type'] == 'month':
            if params['where1'] == '':
                return False, '日不能为空!'
            if params['hour'] == '':
                return False, '小时不能为空!'
            if params['minute'] == '':
                return False, '分钟不能为空!'
        return True, 'OK'


    # 取执行脚本
    def getShell(self, param):
        # try:
        stype = param['stype']
        if stype == 'toFile':
            shell = param.sFile
        else:
            head = "#!/bin/bash\nPATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin\nexport PATH\n"
            start_head = '''
SCRIPT_RUN_TIME="0s"
MW_ToSeconds()
{
    SEC=$1
    if [ $SEC -lt 60 ]; then
       SCRIPT_RUN_TIME="${SEC}s"
    elif [ $SEC -ge 60 ] && [ $SEC -lt 3600 ];then
       SCRIPT_RUN_TIME="$(( SEC / 60 ))m$(( SEC % 60 ))s"
    elif [ $SEC -ge 3600 ]; then
       SCRIPT_RUN_TIME="$(( SEC / 3600 ))h$(( (SEC % 3600) / 60 ))m$(( (SEC % 3600) % 60 ))s"
    fi
}
START_MW_SHELL_TIME=`date +%s`
'''

            source_bin_activate = '''
export LANG=en_US.UTF-8
MW_PATH=%s/bin/activate
if [ -f $MW_PATH ];then
    source $MW_PATH
fi''' % (mw.getPanelDir(),)

            head = head + start_head + source_bin_activate + "\n"
            log = '.log'

            #所有
            if param['sname'] == 'ALL':
                log = ''

            script_dir = mw.getPanelDir() + "/scripts"
            source_stype = 'database'
            if stype.find('database_') > -1:
                plugin_name = stype.replace('database_', '')
                script_dir = mw.getPanelDir() + "/plugins/" + plugin_name + "/scripts"

                source_stype = stype
                stype = 'database'

            wheres = {
                'path': head + "python3 " + script_dir + "/backup.py path " + param['sname'] + " " + str(param['save']),
                'site':   head + "python3 " + script_dir + "/backup.py site " + param['sname'] + " " + str(param['save']),
                'database': head + "python3 " + script_dir + "/backup.py database " + param['sname'] + " " + str(param['save']),
                'logs':   head + "python3 " + script_dir + "/logs_backup.py " + param['sname'] + log + " " + str(param['save']),
                'rememory': head + "/bin/bash " + script_dir + '/rememory.sh'
            }
            if param['backup_to'] != 'localhost':
                cfile = mw.getPluginDir() + "/" + param['backup_to'] + "/index.py"

                wheres['path'] = head + "python3 " + cfile + " path " + param['sname'] + " " + str(param['save'])
                wheres['site'] = head + "python3 " + cfile + " site " + param['sname'] + " " + str(param['save'])
                wheres['database'] = head + "python3 " + cfile + " " + source_stype + " " + param['sname'] + " " + str(param['save'])
            try:
                shell = wheres[stype]
            except:
                if stype == 'toUrl':
                    shell = head + "curl -sS --connect-timeout 10 -m 60 '" + param['urladdress'] + "'"
                else:
                    shell = head + param['sbody'].replace("\r\n", "\n")

            shell += '''
echo "----------------------------------------------------------------------------"
endDate=`date +"%Y-%m-%d %H:%M:%S"`
END_MW_SHELL_TIME=`date +"%s"`
((SHELL_COS_TIME=($END_MW_SHELL_TIME-$START_MW_SHELL_TIME)))
MW_ToSeconds $SHELL_COS_TIME
echo "★[$endDate] Successful | Script Run [$SCRIPT_RUN_TIME] "
echo "----------------------------------------------------------------------------"
'''
        cron_path = mw.getServerDir() + '/cron'
        if not os.path.exists(cron_path):
            mw.execShell('mkdir -p ' + cron_path)

        if not 'echo' in param:
            cron_name = mw.md5(mw.md5(str(time.time()) + '_mw'))
        else:
            cron_name = param['echo']
        file = cron_path + '/' + cron_name
        mw.writeFile(file, self.checkScript(shell))
        mw.execShell('chmod 750 ' + file)
        return cron_name

    # 检查脚本
    def checkScript(self, shell):
        keys = ['shutdown', 'init 0', 'mkfs', 'passwd',
                'chpasswd', '--stdin', 'mkfs.ext', 'mke2fs']
        for k in keys:
            shell = shell.replace(k, '[***]')
        return shell

    # 将Shell脚本写到文件
    def writeShell(self, bash_script):
        if mw.isAppleSystem():
            return mw.returnData(True, 'ok')
        file = '/var/spool/cron/crontabs/root'
        sys_os = mw.getOs()
        if sys_os == 'darwin':
            file = '/etc/crontab'
        elif sys_os.startswith("freebsd"):
            file = '/var/cron/tabs/root'

        if not os.path.exists(file):
            file = '/var/spool/cron/root'

        if not os.path.exists(file):
            mw.writeFile(file, '')

        content = mw.readFile(file)
        content += str(bash_script) + "\n"
        if mw.writeFile(file, content):
            if not os.path.exists(file):
                mw.execShell("chmod 600 '" + file +"' && chown root.root " + file)
            else:
                mw.execShell("chmod 600 '" + file +"' && chown root.crontab " + file)
            return mw.returnData(True, 'ok')
        return mw.returnData(False, '文件写入失败,是否开启系统加固功能!')

    # 重载配置
    def crondReload(self):
        if mw.isAppleSystem():
            if os.path.exists('/etc/crontab'):
                pass
        else:
            if os.path.exists('/etc/init.d/crond'):
                mw.execShell('/etc/init.d/crond reload')
            elif os.path.exists('/etc/init.d/cron'):
                mw.execShell('service cron restart')
            else:
                mw.execShell("systemctl reload crond")

    def syncToCrond(self, cron_id):
        info = thisdb.getCrond(cron_id)
        if 'status' in info:
            if info['status'] == 0:
                return False

        if 'where_hour' in info:
            info['hour'] = info['where_hour']
            info['minute'] = info['where_minute']
            info['week'] = info['where1']

        cmd, _ = self.getCrondCycle(info)
        cron_path = mw.getServerDir() + '/cron'
        cron_name = self.getShell(info)
        cmd += ' ' + cron_path + '/' + cron_name + ' >> ' + cron_path + '/' + cron_name + '.log 2>&1'
        self.writeShell(cmd)
        self.crondReload()
        return True

