# coding: utf-8
#-----------------------------
# 网站备份工具
#-----------------------------

import sys
import os
import re

if sys.platform != 'darwin':
    os.chdir('/www/server/mdserver-web')


chdir = os.getcwd()
sys.path.append(chdir + '/class/core')

# reload(sys)
# sys.setdefaultencoding('utf-8')


import mw
import db
import time


class backupTools:

    def backupSite(self, name, count):
        sql = db.Sql()
        path = sql.table('sites').where('name=?', (name,)).getField('path')
        startTime = time.time()
        if not path:
            endDate = time.strftime('%Y/%m/%d %X', time.localtime())
            log = "网站[" + name + "]不存在!"
            print("★[" + endDate + "] " + log)
            print(
                "----------------------------------------------------------------------------")
            return

        backup_path = mw.getBackupDir() + '/site'
        if not os.path.exists(backup_path):
            mw.execShell("mkdir -p " + backup_path)

        filename = backup_path + "/web_" + name + "_" + \
            time.strftime('%Y%m%d_%H%M%S', time.localtime()) + '.tar.gz'

        cmd = "cd " + os.path.dirname(path) + " && tar zcvf '" + \
            filename + "' '" + os.path.basename(path) + "' > /dev/null"

        # print(cmd)
        mw.execShell(cmd)

        endDate = time.strftime('%Y/%m/%d %X', time.localtime())
        print(filename)
        if not os.path.exists(filename):
            log = "网站[" + name + "]备份失败!"
            print("★[" + endDate + "] " + log)
            print(
                "----------------------------------------------------------------------------")
            return

        outTime = time.time() - startTime
        pid = sql.table('sites').where('name=?', (name,)).getField('id')
        sql.table('backup').add('type,name,pid,filename,addtime,size', ('0', os.path.basename(
            filename), pid, filename, endDate, os.path.getsize(filename)))
        log = "网站[" + name + "]备份成功,用时[" + str(round(outTime, 2)) + "]秒"
        mw.writeLog('计划任务', log)
        print("★[" + endDate + "] " + log)
        print("|---保留最新的[" + count + "]份备份")
        print("|---文件名:" + filename)

        # 清理多余备份
        backups = sql.table('backup').where(
            'type=? and pid=?', ('0', pid)).field('id,filename').select()

        num = len(backups) - int(count)
        if num > 0:
            for backup in backups:
                mw.execShell("rm -f " + backup['filename'])
                sql.table('backup').where('id=?', (backup['id'],)).delete()
                num -= 1
                print("|---已清理过期备份文件：" + backup['filename'])
                if num < 1:
                    break

    def getConf(self, mtype='mysql'):
        path = mw.getServerDir() + '/' + mtype + '/etc/my.cnf'
        return path

     # 数据库密码处理
    def mypass(self, act, root):
        conf_file = self.getConf('mysql')
        mw.execShell("sed -i '/user=root/d' {}".format(conf_file))
        mw.execShell("sed -i '/password=/d' {}".format(conf_file))
        if act:
            mycnf = mw.readFile(conf_file)
            src_dump = "[mysqldump]\n"
            sub_dump = src_dump + "user=root\npassword=\"{}\"\n".format(root)
            if not mycnf:
                return False
            mycnf = mycnf.replace(src_dump, sub_dump)
            if len(mycnf) > 100:
                mw.writeFile(conf_file, mycnf)
            return True
        return True

    def backupDatabase(self, name, count):
        db_path = mw.getServerDir() + '/mysql'
        db_name = 'mysql'
        name = mw.M('databases').dbPos(db_path, 'mysql').where(
            'name=?', (name,)).getField('name')
        startTime = time.time()
        if not name:
            endDate = time.strftime('%Y/%m/%d %X', time.localtime())
            log = "数据库[" + name + "]不存在!"
            print("★[" + endDate + "] " + log)
            print(
                "----------------------------------------------------------------------------")
            return

        backup_path = mw.getBackupDir() + '/database'
        if not os.path.exists(backup_path):
            mw.execShell("mkdir -p " + backup_path)

        filename = backup_path + "/db_" + name + "_" + \
            time.strftime('%Y%m%d_%H%M%S', time.localtime()) + ".sql.gz"

        mysql_root = mw.M('config').dbPos(db_path, db_name).where(
            "id=?", (1,)).getField('mysql_root')

        my_cnf = self.getConf('mysql')
        self.mypass(True, mysql_root)

        # mw.execShell(db_path + "/bin/mysqldump --opt --default-character-set=utf8 " +
        #              name + " | gzip > " + filename)

        # mw.execShell(db_path + "/bin/mysqldump --skip-lock-tables --default-character-set=utf8 " +
        #              name + " | gzip > " + filename)

        # mw.execShell(db_path + "/bin/mysqldump  --single-transaction --quick --default-character-set=utf8 " +
        #              name + " | gzip > " + filename)

        cmd = db_path + "/bin/mysqldump --defaults-file=" + my_cnf + "  --force --opt --default-character-set=utf8 " + \
            name + " | gzip > " + filename
        # print(cmd)
        mw.execShell(cmd)

        if not os.path.exists(filename):
            endDate = time.strftime('%Y/%m/%d %X', time.localtime())
            log = "数据库[" + name + "]备份失败!"
            print("★[" + endDate + "] " + log)
            print(
                "----------------------------------------------------------------------------")
            return

        self.mypass(False, mysql_root)

        endDate = time.strftime('%Y/%m/%d %X', time.localtime())
        outTime = time.time() - startTime
        pid = mw.M('databases').dbPos(db_path, db_name).where(
            'name=?', (name,)).getField('id')

        mw.M('backup').add('type,name,pid,filename,addtime,size', (1, os.path.basename(
            filename), pid, filename, endDate, os.path.getsize(filename)))
        log = "数据库[" + name + "]备份成功,用时[" + str(round(outTime, 2)) + "]秒"
        mw.writeLog('计划任务', log)
        print("★[" + endDate + "] " + log)
        print("|---保留最新的[" + count + "]份备份")
        print("|---文件名:" + filename)

        # 清理多余备份
        backups = mw.M('backup').where(
            'type=? and pid=?', ('1', pid)).field('id,filename').select()

        num = len(backups) - int(count)
        if num > 0:
            for backup in backups:
                mw.execShell("rm -f " + backup['filename'])
                mw.M('backup').where('id=?', (backup['id'],)).delete()
                num -= 1
                print("|---已清理过期备份文件：" + backup['filename'])
                if num < 1:
                    break

    def backupSiteAll(self, save):
        sites = mw.M('sites').field('name').select()
        for site in sites:
            self.backupSite(site['name'], save)

    def backupDatabaseAll(self, save):
        db_path = mw.getServerDir() + '/mysql'
        db_name = 'mysql'
        databases = mw.M('databases').dbPos(
            db_path, db_name).field('name').select()
        for database in databases:
            self.backupDatabase(database['name'], save)

    def findPathName(self, path, filename):
        f = os.scandir(path)
        l = []
        for ff in f:
            if ff.name.find(filename) > -1:
                l.append(ff.name)
        return l

    def backupPath(self, path, count):

        mw.echoStart('备份')

        backup_path = mw.getBackupDir() + '/path'
        if not os.path.exists(backup_path):
            mw.execShell("mkdir -p " + backup_path)

        dirname = os.path.basename(path)
        fname = 'path_{}_{}.tar.gz'.format(
            dirname, mw.formatDate("%Y%m%d_%H%M%S"))
        dfile = os.path.join(backup_path, fname)

        p_size = mw.getPathSize(path)
        stime = time.time()

        cmd = "cd " + os.path.dirname(path) + " && tar zcvf '" + dfile + "' '" + dirname + "' 2>{err_log} 1> /dev/null".format(
            err_log='/tmp/backup_err.log')
        mw.execShell(cmd)

        tar_size = os.path.getsize(dfile)

        mw.echoInfo('备份目录：' + path)
        mw.echoInfo('目录已备份到：' + dfile)
        mw.echoInfo("目录大小：{}".format(mw.toSize(p_size)))
        mw.echoInfo("开始压缩文件：{}".format(mw.formatDate(times=stime)))
        mw.echoInfo("文件压缩完成，耗时{:.2f}秒，压缩包大小：{}".format(
            time.time() - stime, mw.toSize(tar_size)))
        mw.echoInfo('保留最新的备份数：' + count + '份')

        backups = self.findPathName(backup_path, 'path_{}'.format(dirname))
        num = len(backups) - int(count)
        backups.sort()
        if num > 0:
            for backup in backups:
                abspath_bk = backup_path + "/" + backup
                mw.execShell("rm -f " + abspath_bk)
                mw.echoInfo("|---已清理过期备份文件：" + abspath_bk)
                num -= 1
                if num < 1:
                    break

        mw.echoEnd('备份')

if __name__ == "__main__":
    backup = backupTools()
    stype = sys.argv[1]
    if stype == 'site':
        if sys.argv[2] == 'ALL':
            backup.backupSiteAll(sys.argv[3])
        else:
            backup.backupSite(sys.argv[2], sys.argv[3])
    elif stype == 'database':
        if sys.argv[2] == 'ALL':
            backup.backupDatabaseAll(sys.argv[3])
        else:
            backup.backupDatabase(sys.argv[2], sys.argv[3])
    elif stype == 'path':
        backup.backupPath(sys.argv[2], sys.argv[3])
