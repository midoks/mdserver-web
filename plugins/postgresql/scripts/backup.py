# coding: utf-8
#-----------------------------
# 数据库备份工具
#-----------------------------

import sys
import os
import time
import re

if sys.platform != 'darwin':
    # 按脚本位置定位项目根目录:plugins/postgresql/scripts -> 项目根
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))

web_dir = os.getcwd() + "/web"
if os.path.exists(web_dir):
    sys.path.append(web_dir)
    os.chdir(web_dir)

import core.mw as mw
import core.db as db

'''
DEBUG:
python3 /www/server/mdserver-web/plugins/postgresql/scripts/backup.py database admin 3
'''
class backupTools:

    def getServerDir(self):
        return mw.getServerDir() + '/postgresql'

    def getPgPort(self):
        conf = self.getServerDir() + '/data/postgresql.conf'
        content = mw.readFile(conf)
        if not content:
            return '5432'
        tmp = re.search(r'port\s*=\s*(.*)', content)
        if not tmp:
            return '5432'
        return tmp.groups()[0].strip()

    def getPgDump(self):
        pg_dump = self.getServerDir() + '/bin/pg_dump'
        if os.path.exists(pg_dump):
            return pg_dump
        return 'pg_dump'

    def getDbBackupList(self,dbname=''):
        bkDir = mw.getFatherDir() + '/backup/database/postgresql'
        if not os.path.isdir(bkDir):
            return []
        blist = os.listdir(bkDir)
        r = []

        bname = 'db_' + dbname
        blen = len(bname)
        for x in blist:
            fbstr = x[0:blen]
            if fbstr == bname:
                r.append(x)
        # 文件名按时间戳命名,排序后即为时间顺序(旧->新)
        r.sort()
        return r
    
    def backupDatabase(self, params, count):
        params_args = params.split("@")
        name = params_args[0]
        table_name = ''
        if len(params_args) > 1:
            table_name = params_args[1]

        backup_name = name
        if table_name != '':
            backup_name = name+'@'+table_name

        db_path = self.getServerDir()
        db_name = 'pgsql'
        find_name = mw.M('databases').dbPos(db_path, db_name).where(
            'name=?', (name,)).getField('name')
        startTime = time.time()
        if not find_name:
            endDate = time.strftime('%Y/%m/%d %X', time.localtime())
            log = "数据库[" + name + "]不存在!"
            print("★[" + endDate + "] " + log)
            print("----------------------------------------------------------------------------")
            return

        backup_path = mw.getBackupDir() + '/database/postgresql'
        if not os.path.exists(backup_path):
            mw.execShell("mkdir -p " + backup_path)

        filename = backup_path + "/db_" + backup_name + "_" + \
            time.strftime('%Y%m%d_%H%M%S', time.localtime()) + ".sql.gz"

        port = self.getPgPort()
        pg_dump = self.getPgDump()

        dump_args = '-c ' + name
        if table_name != '':
            dump_args = '-c -t ' + table_name + ' ' + name

        # postgresql 安装目录属主是 postgres,Linux 下需以 postgres 用户执行
        if mw.isAppleSystem():
            cmd = pg_dump + ' ' + dump_args + ' -p ' + port + ' | gzip > ' + filename
        else:
            cmd = 'su - postgres -c "' + pg_dump + ' ' + \
                dump_args + ' -p ' + port + '" | gzip > ' + filename
        mw.execShell(cmd)

        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            if os.path.exists(filename):
                mw.execShell("rm -f " + filename)
            endDate = time.strftime('%Y/%m/%d %X', time.localtime())
            log = "数据库[" + name + "]备份失败!"
            print("★[" + endDate + "] " + log)
            print("----------------------------------------------------------------------------")
            return

        endDate = time.strftime('%Y/%m/%d %X', time.localtime())
        outTime = time.time() - startTime
        pid = mw.M('databases').dbPos(db_path, db_name).where(
            'name=?', (name,)).getField('id')


        log = "数据库[" + backup_name + "]备份成功,用时[" + str(round(outTime, 2)) + "]秒"
        mw.writeLog('计划任务', log)
        print("★[" + endDate + "] " + log)
        print("|---保留最新的[" + count + "]份备份")
        print("|---文件名:" + filename)

        backups = self.getDbBackupList(backup_name)
        # 清理多余备份
        num = len(backups) - int(count)
        if num > 0:
            for backup in backups:
                mw.execShell("rm -f " + backup_path + "/"+backup)
                num -= 1
                print("|---已清理过期文件：" + backup)
                if num < 1:
                    break

    def backupDatabaseAll(self, save):
        db_path = self.getServerDir()
        db_name = 'pgsql'
        databases = mw.M('databases').dbPos(db_path, db_name).field('name').select()
        for database in databases:
            self.backupDatabase(database['name'], save)


if __name__ == "__main__":
    backup = backupTools()
    type = sys.argv[1]
    if type == 'database':
        if sys.argv[2] == 'ALL':
            backup.backupDatabaseAll(sys.argv[3])
        else:
            backup.backupDatabase(sys.argv[2], sys.argv[3])
