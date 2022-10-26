# coding: utf-8
#-----------------------------
# 网站备份工具
#-----------------------------

import sys
import os

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

        backup_path = mw.getRootDir() + '/backup/site'
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

        backup_path = mw.getRootDir() + '/backup/database'
        if not os.path.exists(backup_path):
            mw.execShell("mkdir -p " + backup_path)

        filename = backup_path + "/db_" + name + "_" + \
            time.strftime('%Y%m%d_%H%M%S', time.localtime()) + ".sql.gz"

        import re
        mysql_root = mw.M('config').dbPos(db_path, db_name).where(
            "id=?", (1,)).getField('mysql_root')

        mycnf = mw.readFile(db_path + '/etc/my.cnf')
        rep = "\[mysqldump\]\nuser=root"
        sea = "[mysqldump]\n"
        subStr = sea + "user=root\npassword=" + mysql_root + "\n"
        mycnf = mycnf.replace(sea, subStr)
        if len(mycnf) > 100:
            mw.writeFile(db_path + '/etc/my.cnf', mycnf)

        # mw.execShell(db_path + "/bin/mysqldump --opt --default-character-set=utf8 " +
        #              name + " | gzip > " + filename)

        # mw.execShell(db_path + "/bin/mysqldump --skip-lock-tables --default-character-set=utf8 " +
        #              name + " | gzip > " + filename)

        mw.execShell(db_path + "/bin/mysqldump  --single-transaction --quick --default-character-set=utf8 " +
                     name + " | gzip > " + filename)

        if not os.path.exists(filename):
            endDate = time.strftime('%Y/%m/%d %X', time.localtime())
            log = "数据库[" + name + "]备份失败!"
            print("★[" + endDate + "] " + log)
            print(
                "----------------------------------------------------------------------------")
            return

        mycnf = mw.readFile(db_path + '/etc/my.cnf')
        mycnf = mycnf.replace(subStr, sea)
        if len(mycnf) > 100:
            mw.writeFile(db_path + '/etc/my.cnf', mycnf)

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


if __name__ == "__main__":
    backup = backupTools()
    type = sys.argv[1]
    if type == 'site':
        if sys.argv[2] == 'ALL':
            backup.backupSiteAll(sys.argv[3])
        else:
            backup.backupSite(sys.argv[2], sys.argv[3])
    elif type == 'database':
        if sys.argv[2] == 'ALL':
            backup.backupDatabaseAll(sys.argv[3])
        else:
            backup.backupDatabase(sys.argv[2], sys.argv[3])
