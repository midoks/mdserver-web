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
import yaml

def getPluginName():
    return 'mongodb'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getConf():
    path = getServerDir() + "/mongodb.conf"
    return path
    
def getConfigData():
    cfg = getConf()
    config_data = mw.readFile(cfg)
    try:
        config = yaml.safe_load(config_data)
    except:
        config = {
            "systemLog": {
                "destination": "file",
                "logAppend": True,
                "path": mw.getServerDir()+"/mongodb/log/mongodb.log"
            },
            "storage": {
                "dbPath": mw.getServerDir()+"/mongodb/data",
                "directoryPerDB": True,
                "journal": {
                    "enabled": True
                }
            },
            "processManagement": {
                "fork": True,
                "pidFilePath": mw.getServerDir()+"/mongodb/log/mongodb.pid"
            },
            "net": {
                "port": 27017,
                "bindIp": "0.0.0.0"
            },
            "security": {
                "authorization": "enabled",
                "javascriptEnabled": False
            }
        }
    return config


def getConfIp():
    data = getConfigData()
    return data['net']['bindIp']

def getConfPort():
    data = getConfigData()
    return data['net']['port']

def getConfAuth():
    data = getConfigData()
    return data['security']['authorization']

def mongdbClient():
    import pymongo
    port = getConfPort()
    auth = getConfAuth()
    ip = getConfIp()
    mg_root = pSqliteDb('config').where('id=?', (1,)).getField('mg_root')
    # print(ip,port,auth,mg_root)
    if auth == 'disabled':
        client = pymongo.MongoClient(host=ip, port=int(port), directConnection=True)
    else:
        # uri = "mongodb://root:"+mg_root+"@127.0.0.1:"+str(port)
        # client = pymongo.MongoClient(uri)
        client = pymongo.MongoClient(host=ip, port=int(port), directConnection=True, username='root',password=mg_root)
    return client

class backupTools:

    def getDbBackupList(self,dbname=''):
        bkDir = mw.getRootDir() + '/backup/database'
        blist = os.listdir(bkDir)
        r = []

        bname = 'mongodb_' + dbname
        blen = len(bname)
        for x in blist:
            fbstr = x[0:blen]
            if fbstr == bname:
                r.append(x)
        return r

    def backupDatabase(self, name, count):
        db_path = mw.getServerDir() + '/mongodb'
        db_name = 'mongodb'
        name = mw.M('databases').dbPos(db_path, db_name).where('name=?', (name,)).getField('name')

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

        time_now = time.strftime('%Y%m%d_%H%M%S', time.localtime())
        backup_name = "mongodb_" + name + "_" + time_now + ".tar.gz"
        filename = backup_path + "/"+backup_name

    
        cmd = db_path + "/bin/mongodump --port 27017 -d test -o "+backup_path 
        mw.execShell(cmd)
        cmd_gz = "cd "+backup_path+"/"+name+" && tar -zcvf "+filename + " ./"
        mw.execShell(cmd_gz)
        mw.execShell("rm -rf "+ backup_path+"/"+name)
        
        if not os.path.exists(filename):
            endDate = time.strftime('%Y/%m/%d %X', time.localtime())
            log = "数据库[" + name + "]备份失败!"
            print("★[" + endDate + "] " + log)
            print("----------------------------------------------------------------------------")
            return


        endDate = time.strftime('%Y/%m/%d %X', time.localtime())
        outTime = time.time() - startTime

        # print(outTime)
        log = "数据库MongoDB[" + name + "]备份成功,用时[" + str(round(outTime, 2)) + "]秒"
        mw.writeLog('计划任务', log)
        print("★[" + endDate + "] " + log)
        print("|---保留最新的[" + count + "]份备份")
        print("|---文件名:" + filename)

        backups = self.getDbBackupList(name)

        # 清理多余备份
        num = len(backups) - int(count)
        if num > 0:
            for backup in backups:
                mw.execShell("rm -f " + backup_path + "/"+backup)
                num -= 1
                print("|---已清理过期备份文件：" + backup)
                if num < 1:
                    break

    def backupDatabaseAll(self, save):
        db_path = mw.getServerDir() + '/mongodb'
        db_name = 'mongodb'
        databases = mw.M('databases').dbPos(
            db_path, db_name).field('name').select()
        for db in databases:
            self.backupDatabase(db['name'], save)

    def findPathName(self, path, filename):
        f = os.scandir(path)
        l = []
        for ff in f:
            if ff.name.find(filename) > -1:
                l.append(ff.name)
        return l

if __name__ == "__main__":
    backup = backupTools()
    stype = sys.argv[1]
    if stype == 'all':
        backup.backupDatabaseAll(sys.argv[2])
    if stype == 'database':
        backup.backupDatabase(sys.argv[2], sys.argv[3])
