
# +--------------------------------------------------------------------
# |   事件型防篡改
# +--------------------------------------------------------------------
import sys
import os
import pyinotify
import json
import shutil
import time
import psutil
import threading
import datetime

sys.path.append(os.getcwd() + "/class/core")
import mw


class MyEventHandler(pyinotify.ProcessEvent):
    _PLUGIN_PATH = '/www/server/tamper_proof_py'
    _CONFIG = '/config.json'
    _SITES = '/sites.json'
    _SITES_DATA = None
    _CONFIG_DATA = None
    _DONE_FILE = None
    bakcupChirdPath = []

    def __init__(self):
        self._PLUGIN_PATH = self.getServerDir()

    def getPluginName(self):
        return 'tamper_proof_py'

    def getPluginDir(self):
        return mw.getPluginDir() + '/' + self.getPluginName()

    def getServerDir(self):
        return mw.getServerDir() + '/' + self.getPluginName()

    def rmdir(self, filename):
        try:
            shutil.rmtree(filename)
        except:
            pass

    def check_site_logs(self, Stiename, datetime_time):
        ret = []
        cur_month = datetime_time.month
        cur_day = datetime_time.day
        cur_year = datetime_time.year
        cur_hour = datetime_time.hour
        cur_minute = datetime_time.minute
        cur_second = int(datetime_time.second)
        months = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07',
                  'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
        logs_data = self.get_site_logs(Stiename)
        if not logs_data:
            return False
        for i2 in logs_data:
            try:
                i = i2.split()
                # 判断状态码是否为200
                if int(i[8]) not in [200, 500]:
                    continue
                # 判断是否为POST
                day_time = i[3].split('/')[0].split('[')[1]
                if int(cur_day) != int(day_time):
                    continue
                month_time = i[3].split('/')[1]
                if int(months[month_time]) != int(cur_month):
                    continue
                year_time = i[3].split('/')[2].split(':')[0]
                if int(year_time) != int(cur_year):
                    continue
                hour_time = i[3].split('/')[2].split(':')[1]
                if int(hour_time) != int(cur_hour):
                    continue
                minute_time = i[3].split('/')[2].split(':')[2]
                if int(minute_time) != int(cur_minute):
                    continue
                second_time = int(i[3].split('/')[2].split(':')[3])
                if cur_second - second_time > 10:
                    continue
                ret.append(i2)
            except:
                continue
        ret2 = []
        if len(ret) > 20:
            for i2 in logs_data:
                try:
                    i = i2.split()
                    if i[6] != 'POST':
                        continue
                    if int(i[8]) not in [200, 500]:
                        continue
                    # 判断是否为POST
                    day_time = i[3].split('/')[0].split('[')[1]
                    if int(cur_day) != int(day_time):
                        continue
                    month_time = i[3].split('/')[1]
                    if int(months[month_time]) != int(cur_month):
                        continue
                    year_time = i[3].split('/')[2].split(':')[0]
                    if int(year_time) != int(cur_year):
                        continue
                    hour_time = i[3].split('/')[2].split(':')[1]
                    if int(hour_time) != int(cur_hour):
                        continue
                    minute_time = i[3].split('/')[2].split(':')[2]
                    if int(minute_time) != int(cur_minute):
                        continue
                    ret2.append(i2)
                except:
                    continue
        if ret2:
            ret = ret2
        if len(ret) > 20:
            return ret[0:20]
        return ret

    def get_site_logs(self, Stiename):
        try:
            pythonV = sys.version_info[0]
            path = '/www/wwwlogs/' + Stiename + '.log'
            num = 500
            if not os.path.exists(path):
                return []
            p = 1
            start_line = (p - 1) * num
            count = start_line + num
            fp = open(path, 'rb')
            buf = ""
            try:
                fp.seek(-1, 2)
            except:
                return []
            if fp.read(1) == "\n":
                fp.seek(-1, 2)
            data = []
            b = True
            n = 0
            c = 0
            while c < count:
                while True:
                    newline_pos = str.rfind(buf, "\n")
                    pos = fp.tell()
                    if newline_pos != -1:
                        if n >= start_line:
                            line = buf[newline_pos + 1:]
                            if line:
                                try:
                                    data.append(line)
                                except:
                                    c -= 1
                                    n -= 1
                                    pass
                            else:
                                c -= 1
                                n -= 1
                        buf = buf[:newline_pos]
                        n += 1
                        c += 1
                        break
                    else:
                        if pos == 0:
                            b = False
                            break
                        to_read = min(4096, pos)
                        fp.seek(-to_read, 1)
                        t_buf = fp.read(to_read)
                        if pythonV == 3:
                            t_buf = t_buf.decode('utf-8', errors="ignore")
                        buf = t_buf + buf
                        fp.seek(-to_read, 1)
                        if pos - to_read == 0:
                            buf = "\n" + buf
                if not b:
                    break
            fp.close()
        except:
            data = []
        return data

    def process_IN_CREATE(self, event):
        siteInfo = self.get_SITE_CONFIG(event.pathname)
        if not self.check_FILE(event, siteInfo, True):
            return False
        self._DONE_FILE = event.pathname
        if event.dir:
            if os.path.exists(event.pathname):
                self.rmdir(event.pathname)
                self.write_LOG('create', siteInfo[
                               'siteName'], event.pathname, datetime.datetime.now())

        else:
            if os.path.exists(event.pathname):
                try:
                    src_path = os.path.dirname(event.pathname)
                    os.system("chattr -a {}".format(src_path))
                    os.remove(event.pathname)
                    os.system("chattr +a {}".format(src_path))
                    self.write_LOG('create', siteInfo[
                                   'siteName'], event.pathname, datetime.datetime.now())
                except:
                    pass

    def process_IN_MOVED_TO(self, event):
        # 检查是否受保护
        siteInfo = self.get_SITE_CONFIG(event.pathname)
        if not self.check_FILE(event, siteInfo):
            return False

        if not getattr(event, 'src_pathname', None):
            if os.path.isdir(event.pathname):
                self.rmdir(event.pathname)
            else:
                os.remove(event.pathname)
            self.write_LOG('move', siteInfo[
                           'siteName'], '未知 -> ' + event.pathname)
            return True

        # 是否为标记文件
        if event.src_pathname == self._DONE_FILE:
            return False

        if not os.path.exists(event.src_pathname):
            # 标记
            self._DONE_FILE = event.pathname
            # 还原
            os.renames(event.pathname, event.src_pathname)

        # 记录日志
        self.write_LOG('move', siteInfo['siteName'],
                       event.src_pathname + ' -> ' + event.pathname)

    def check_FILE(self, event, siteInfo, create=False):
        if not siteInfo:
            return False
        if self.exclude_PATH(event.pathname):
            return False
        if event.dir and create:
            return True
        if not event.dir:
            if not self.protect_EXT(event.pathname):
                return False
        return True

    def protect_EXT(self, pathname):
        if pathname.find('.') == -1:
            return False
        extName = pathname.split('.')[-1].lower()
        siteData = self.get_SITE_CONFIG(pathname)
        if siteData:
            if extName in siteData['protectExt']:
                return True
        return False

    def exclude_PATH(self, pathname):
        if pathname.find('/') == -1:
            return False
        siteData = self.get_SITE_CONFIG(pathname)
        return self.exclude_PATH_OF_SITE(pathname, siteData['excludePath'])

    def exclude_PATH_OF_SITE(self, pathname, excludePath):
        pathname = pathname.lower()
        dirNames = pathname.split('/')
        if excludePath:
            if pathname in excludePath:
                return True
            if pathname + '/' in excludePath:
                return True
            for ePath in excludePath:
                if ePath in dirNames:
                    return True
                if pathname.find(ePath) == 0:
                    return True
        return False

    def get_SITE_CONFIG(self, pathname):
        if not self._SITES_DATA:
            self._SITES_DATA = json.loads(
                mw.readFile(self._PLUGIN_PATH + self._SITES))
        for site in self._SITES_DATA:
            length = len(site['path'])
            if len(pathname) < length:
                continue
            if site['path'] != pathname[:length]:
                continue
            return site
        return None

    def get_CONFIG(self):
        if self._CONFIG_DATA:
            return self._CONFIG_DATA
        self._CONFIG_DATA = json.loads(
            mw.readFile(self._PLUGIN_PATH + self._CONFIG))

    def list_DIR(self, path, siteInfo):  # path 站点路径
        if not os.path.exists(path):
            return
        lock_files = []
        lock_dirs = []
        explode_a = ['log', 'logs', 'cache', 'templates', 'template', 'upload', 'img',
                     'image', 'images', 'public', 'static', 'js', 'css', 'tmp', 'temp', 'update', 'data']
        for name in os.listdir(path):
            try:
                filename = "{}/{}".format(path, name).replace('//', '/')
                lower_name = name.lower()
                lower_filename = filename.lower()
                if os.path.isdir(filename):  # 是否为目录
                    if lower_name in siteInfo['excludePath']:
                        continue  # 是否为排除的文件名
                    # 是否为排除目录
                    if not self.exclude_PATH_OF_SITE(filename, siteInfo['excludePath']):
                        if not lower_name in explode_a:  # 是否为固定不锁定目录
                            lock_dirs.append('"' + name + '"')
                        self.list_DIR(filename, siteInfo)
                    continue

                # 是否为受保护的文件名或文件全路径
                if not lower_name in siteInfo['protectExt'] and not lower_filename in siteInfo['protectExt']:
                    if not self.get_EXT_NAME(lower_name) in siteInfo['protectExt']:
                        continue  # 是否为受保护文件类型

                if lower_filename in siteInfo['excludePath']:
                    continue  # 是否为排除文件
                if lower_name in siteInfo['excludePath']:
                    continue  # 是否为排除的文件名
                lock_files.append('"' + name + '"')
            except:
                print(mw.getTracebackInfo())
        if lock_files:
            self.thread_exec(lock_files, path, 'i')
        if lock_dirs:
            self.thread_exec(lock_dirs, path, 'a')

    _thread_count = 0
    _thread_max = 2 * psutil.cpu_count()

    def thread_exec(self, file_list, cwd, i='i'):
        while self._thread_count > self._thread_max:
            time.sleep(0.1)

        self._thread_count += 1
        cmd = "cd {} && chattr +{} {} > /dev/null".format(
            cwd, i, ' '.join(file_list))
        p = threading.Thread(target=self.run_thread, args=(cmd,))
        p.start()

    def run_thread(self, cmd):
        os.system(cmd)
        self._thread_count -= 1

    def get_EXT_NAME(self, fileName):
        return fileName.split('.')[-1]

    def write_LOG(self, eventType, siteName, pathname, datetime):
        # 获取网站时间的top100 记录
        site_log = '/www/wwwlogs/%s.log' % siteName
        logs_data = []
        if os.path.exists(site_log):
            logs_data = self.check_site_logs(siteName, datetime)
        dateDay = time.strftime("%Y-%m-%d", time.localtime())
        logPath = self._PLUGIN_PATH + '/sites/' + \
            siteName + '/day/' + dateDay
        if not os.path.exists(logPath):
            os.makedirs(logPath)
        logFile = os.path.join(logPath, 'logs.json')
        logVar = [int(time.time()), eventType, pathname, logs_data]
        fp = open(logFile, 'a+')
        fp.write(json.dumps(logVar) + "\n")
        fp.close()
        logFiles = [
            logPath + '/total.json',
            self._PLUGIN_PATH + '/sites/' + siteName + '/day/total.json',
            self._PLUGIN_PATH + '/sites/total.json'
        ]

        for totalLogFile in logFiles:
            if not os.path.exists(totalLogFile):
                totalData = {"total": 0, "delete": 0,
                             "create": 0, "modify": 0, "move": 0}
            else:
                dataTmp = mw.readFile(totalLogFile)
                if dataTmp:
                    totalData = json.loads(dataTmp)
                else:
                    totalData = {"total": 0, "delete": 0,
                                 "create": 0, "modify": 0, "move": 0}

            totalData['total'] += 1
            totalData[eventType] += 1
            mw.writeFile(totalLogFile, json.dumps(totalData))

    # 设置.user.ini
    def set_user_ini(self, path, up=0):
        os.chdir(path)
        useriniPath = path + '/.user.ini'
        if os.path.exists(useriniPath):
            os.system('chattr +i ' + useriniPath)
        for p1 in os.listdir(path):
            try:
                npath = path + '/' + p1
                if not os.path.isdir(npath):
                    continue
                useriniPath = npath + '/.user.ini'
                if os.path.exists(useriniPath):
                    os.system('chattr +i ' + useriniPath)
                if up < 3:
                    self.set_user_ini(npath, up + 1)
            except:
                continue
        return True

    def unlock(self, path):
        os.system('chattr -R -i {} &> /dev/null'.format(path))
        os.system('chattr -R -a {} &> /dev/null'.format(path))
        self.set_user_ini(path)

    def close(self, reload=False):
        # 解除锁定
        sites = self.get_sites()
        print("")
        print("=" * 60)
        print("【{}】正在关闭防篡改，请稍候...".format(mw.formatDate()))
        print("-" * 60)
        for siteInfo in sites:
            tip = self._PLUGIN_PATH + '/tips/' + siteInfo['siteName'] + '.pl'
            if not siteInfo['open'] and not os.path.exists(tip):
                continue
            if reload and siteInfo['open']:
                continue
            if sys.version_info[0] == 2:
                print(
                    "【{}】|-解锁网站[{}]".format(mw.formatDate(), siteInfo['siteName'])),
            else:
                os.system(
                    "echo -e '【{}】|-解锁网站[{}]\c'".format(mw.formatDate(), siteInfo['siteName']))
                #print("【{}】|-解锁网站[{}]".format(mw.format_date(),siteInfo['siteName']),end=" ")
            self.unlock(siteInfo['path'])
            if os.path.exists(tip):
                os.remove(tip)
            print("\t=> 完成")
        print("-" * 60)
        print('|-防篡改已关闭')
        print("=" * 60)
        print(">>>>>>>>>>END<<<<<<<<<<")

    # 获取网站配置列表
    def get_sites(self):
        siteconf = self._PLUGIN_PATH + '/sites.json'
        d = mw.readFile(siteconf)
        if not os.path.exists(siteconf) or not d:
            mw.writeFile(siteconf, "[]")
        data = json.loads(mw.readFile(siteconf))

        # 处理多余字段开始 >>>>>>>>>>
        is_write = False
        rm_keys = ['lock', 'bak_open']
        for i in data:
            i_keys = i.keys()
            if not 'open' in i_keys:
                i['open'] = False
            for o in rm_keys:
                if o in i_keys:
                    if i[o]:
                        i['open'] = True
                    i.pop(o)
                    is_write = True
        if is_write:
            mw.writeFile(siteconf, json.dumps(data))
        # 处理多余字段结束 <<<<<<<<<<<<<
        return data

    def __enter__(self):
        self.close()

    def __exit__(self, a, b, c):
        self.close()


def run():
    # 初始化inotify对像
    event = MyEventHandler()
    watchManager = pyinotify.WatchManager()
    starttime = time.time()
    mode = pyinotify.IN_CREATE | pyinotify.IN_MOVED_TO

    # 处理网站属性
    sites = event.get_sites()
    print("=" * 60)
    print("【{}】正在启动防篡改，请稍候...".format(mw.formatDate()))
    print("-" * 60)
    tip_path = event._PLUGIN_PATH + '/tips/'
    if not os.path.exists(tip_path):
        os.makedirs(tip_path)
    speed_file = event._PLUGIN_PATH + '/speed.pl'
    for siteInfo in sites:
        s = time.time()
        tip = tip_path + siteInfo['siteName'] + '.pl'
        if not siteInfo['open']:
            continue
        if sys.version_info[0] == 2:
            print("【{}】|-网站[{}]".format(mw.formatDate(),
                                        siteInfo['siteName'])),
        else:
            os.system(
                "echo -e '【{}】|-网站[{}]\c'".format(mw.formatDate(), siteInfo['siteName']))
            # print("【{}】|-网站[{}]".format(public.format_date(),siteInfo['siteName']),end=" ")
        mw.writeFile(speed_file, "正在处理网站[{}]，请稍候...".format(
            siteInfo['siteName']))
        if not os.path.exists(tip):
            event.list_DIR(siteInfo['path'], siteInfo)
        try:
            watchManager.add_watch(
                siteInfo['path'], mode, auto_add=True, rec=True)
        except:
            print(mw.getTracebackInfo())
        tout = round(time.time() - s, 2)
        mw.writeFile(tip, '1')
        print("\t\t=> 完成，耗时 {} 秒".format(tout))

    # 启动服务
    endtime = round(time.time() - starttime, 2)
    mw.writeLog('防篡改程序', "网站防篡改服务已成功启动,耗时[%s]秒" % endtime)
    notifier = pyinotify.Notifier(watchManager, event)
    print("-" * 60)
    print('|-防篡改服务已启动')
    print("=" * 60)
    end_tips = ">>>>>>>>>>END<<<<<<<<<<"
    print(end_tips)
    mw.writeFile(speed_file, end_tips)
    notifier.loop()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if 'stop' in sys.argv:
            event = MyEventHandler()
            event.close()
        elif 'start' in sys.argv:
            run()
        elif 'unlock' in sys.argv:
            event = MyEventHandler()
            event.unlock(sys.argv[2])
        elif 'reload' in sys.argv:
            event = MyEventHandler()
            event.close(True)
        else:
            print('error')
    else:
        run()
