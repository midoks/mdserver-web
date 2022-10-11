#!/usr/bin/python
# coding: utf-8
#-----------------------------
# 网站日志切割脚本
#-----------------------------
import sys
import os
import shutil
import time
import glob

if sys.platform != 'darwin':
    os.chdir('/www/server/mdserver-web')


chdir = os.getcwd()
sys.path.append(chdir + '/class/core')

# importlib.reload(sys)
# sys.setdefaultencoding('utf-8')

import mw
print('==================================================================')
print('★[' + time.strftime("%Y/%m/%d %H:%M:%S") + ']，切割日志')
print('==================================================================')
print('|--当前保留最新的[' + sys.argv[2] + ']份')
logsPath = mw.getLogsDir()
px = '.log'


def split_logs(oldFileName, num):
    global logsPath
    if not os.path.exists(oldFileName):
        print('|---' + oldFileName + '文件不存在!')
        return

    logs = sorted(glob.glob(oldFileName + "_*"))
    count = len(logs)
    num = count - num

    for i in range(count):
        if i > num:
            break
        os.remove(logs[i])
        print('|---多余日志[' + logs[i] + ']已删除!')

    newFileName = oldFileName + '_' + time.strftime("%Y-%m-%d_%H%M%S") + '.log'
    shutil.move(oldFileName, newFileName)
    print('|---已切割日志到:' + newFileName)


def split_all(save):
    sites = mw.M('sites').field('name').select()
    for site in sites:
        oldFileName = logsPath + site['name'] + px
        split_logs(oldFileName, save)

if __name__ == '__main__':
    num = int(sys.argv[2])
    if sys.argv[1].find('ALL') == 0:
        split_all(num)
    else:
        siteName = sys.argv[1]
        if siteName[-4:] == '.log':
            siteName = siteName[:-4]
        else:
            siteName = siteName.replace("-access_log", '')
        oldFileName = logsPath + '/' + sys.argv[1]
        errOldFileName = logsPath + '/' + \
            sys.argv[1].strip(".log") + ".error.log"
        split_logs(oldFileName, num)
        if os.path.exists(errOldFileName):
            split_logs(errOldFileName, num)
    path = mw.getServerDir()
    os.system("kill -USR1 `cat " + path + "/openresty/nginx/logs/nginx.pid`")
