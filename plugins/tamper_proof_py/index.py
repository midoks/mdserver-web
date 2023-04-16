# coding:utf-8

import sys
import io
import os
import time
import json
import re
import psutil
from datetime import datetime

sys.dont_write_bytecode = True
sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


class App:

    __total = 'total.json'
    __sites = []

    def __init__(self):
        pass

    def getPluginName(self):
        return 'tamper_proof_py'

    def getPluginDir(self):
        return mw.getPluginDir() + '/' + self.getPluginName()

    def getServerDir(self):
        return mw.getServerDir() + '/' + self.getPluginName()

    def getInitDFile(self):
        if app_debug:
            return '/tmp/' + self.getPluginName()
        return '/etc/init.d/' + self.getPluginName()

    def getInitDTpl(self):
        path = self.getPluginDir() + "/init.d/" + self.getPluginName() + ".tpl"
        return path

    def getArgs(self):
        args = sys.argv[2:]
        tmp = {}
        args_len = len(args)

        if args_len == 1:
            t = args[0].strip('{').strip('}')
            if t.strip() == '':
                tmp = []
            else:
                t = t.split(':')
                tmp[t[0]] = t[1]
        elif args_len > 1:
            for i in range(len(args)):
                t = args[i].split(':')
                tmp[t[0]] = t[1]
        return tmp

    def checkArgs(self, data, ck=[]):
        for i in range(len(ck)):
            if not ck[i] in data:
                return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
        return (True, mw.returnJson(True, 'ok'))

    def getTotal(self, siteName=None, day=None):
        defaultTotal = {"total": 0, "delete": 0,
                        "create": 0, "modify": 0, "move": 0}
        if siteName:
            total = {}
            total_path = self.getServerDir() + '/sites/' + siteName + '/' + self.__total
            if not os.path.exists(total_path):
                total['site'] = defaultTotal
            else:
                total_data = mw.readFile(total_path)
                if total_data['site']:
                    total['site'] = json.loads(total_data['site'])
                else:
                    total['site'] = defaultTotal

            if not day:
                day = time.strftime("%Y-%m-%d", time.localtime())
            total_day_path = self.getServerDir() + '/sites/' + siteName + '/day/total.json'
            if not os.path.exists(total_day_path):
                total['day'] = defaultTotal
            else:
                total['day'] = mw.readFile(total_day_path)
                if total['day']:
                    total['day'] = json.loads(total['day'])
                else:
                    total['day'] = defaultTotal
        else:
            filename = self.getServerDir() + '/sites/' + self.__total
            if os.path.exists(filename):
                total = json.loads(mw.readFile(filename))
            else:
                total = defaultTotal
        return total

    def getSites(self):
        sites_path = self.getServerDir() + '/sites.json'
        t = mw.readFile(sites_path)
        if not os.path.exists(sites_path) or not t:
            mw.writeFile(sites_path, '[]')
        data = json.loads(mw.readFile(sites_path))

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
            mw.writeFile(sites_path, json.dumps(data))

        self.__sites = data
        return data

    def writeSites(self, data):
        mw.writeFile(self.getServerDir() + '/sites.json', json.dumps(data))
        # mw.ExecShell('/etc/init.d/bt_tamper_proof reload')

    def __getFind(self, siteName):
        data = self.getSites()
        for siteInfo in data:
            if siteName == siteInfo['siteName']:
                return siteInfo
        return None

    def writeLog(self, log):
        mw.writeLog('防篡改程序', log)

    def saveSiteConfig(self, siteInfo):
        data = self.getSites()
        for i in range(len(data)):
            if data[i]['siteName'] != siteInfo['siteName']:
                continue
            data[i] = siteInfo
            break
        self.writeSites(data)

    def syncSites(self):
        data = self.getSites()
        sites = mw.M('sites').field('name,path').select()

        config_path = self.getPluginDir() + '/conf/config.json'
        config = json.loads(mw.readFile(config_path))
        names = []
        n = 0

        # print(config)
        for siteTmp in sites:
            names.append(siteTmp['name'])
            siteInfo = self.__getFind(siteTmp['name'])
            if siteInfo:
                if siteInfo['path'] != siteTmp['path']:
                    siteInfo['path'] = siteTmp['path']
                    self.saveSiteConfig(siteInfo)
                    data = self.getSites()
                continue
            siteInfo = {}
            siteInfo['siteName'] = siteTmp['name']
            siteInfo['path'] = siteTmp['path']
            siteInfo['open'] = False
            siteInfo['excludePath'] = config['excludePath']
            siteInfo['protectExt'] = config['protectExt']
            data.append(siteInfo)
            n += 1

        newData = []
        for siteInfoTmp in data:
            if siteInfoTmp['siteName'] in names:
                newData.append(siteInfoTmp)
            else:
                mw.execShell("rm -rf " + self.getServerDir() +
                             '/sites/' + siteInfoTmp['siteName'])
                n += 1
        if n > 0:
            self.writeSites(newData)
        self.__sites = None

    def initDreplace(self):
        file_tpl = self.getInitDTpl()
        service_path = self.getServerDir()

        initD_path = service_path + '/init.d'
        if not os.path.exists(initD_path):
            os.mkdir(initD_path)

        # init.d
        file_bin = initD_path + '/' + self.getPluginName()
        if not os.path.exists(file_bin):
            # initd replace
            content = mw.readFile(file_tpl)
            content = content.replace('{$SERVER_PATH}', service_path)
            mw.writeFile(file_bin, content)
            mw.execShell('chmod +x ' + file_bin)

        # systemd
        # /usr/lib/systemd/system
        systemDir = mw.systemdCfgDir()
        systemService = systemDir + '/tamper_proof_py.service'
        systemServiceTpl = self.getPluginDir() + '/init.d/tamper_proof_py.service.tpl'
        if os.path.exists(systemDir) and not os.path.exists(systemService):
            se_content = mw.readFile(systemServiceTpl)
            se_content = se_content.replace('{$SERVER_PATH}', service_path)
            mw.writeFile(systemService, se_content)
            mw.execShell('systemctl daemon-reload')

        return file_bin

    def getDays(self, path):
        days = []
        if not os.path.exists(path):
            os.makedirs(path)
        for dirname in os.listdir(path):
            if dirname == '..' or dirname == '.' or dirname == 'total.json':
                continue
            if not os.path.isdir(path + '/' + dirname):
                continue
            days.append(dirname)
        days = sorted(days, reverse=True)
        return days

    def status(self):
        '''
        状态
        '''
        initd_file = self.getServerDir() + '/init.d/' + self.getPluginName()
        if not os.path.exists(initd_file):
            return 'stop'
        cmd = initd_file + ' status|grep already'
        data = mw.execShell(cmd)
        if data[0] != '':
            return 'start'
        return 'stop'

    def tpOp(self, method):
        file = self.initDreplace()
        if not mw.isAppleSystem():
            cmd = 'systemctl ' + method + ' ' + self.getPluginName()
            data = mw.execShell(cmd)
            if data[1] == '':
                return mw.returnJson(True, '操作成功')
            return mw.returnJson(False, '操作失败')

        cmd = file + ' ' + method
        data = mw.execShell(cmd)
        if data[1] == '':
            return mw.returnJson(True, '操作成功')
        return mw.returnJson(False, '操作失败')

    def start(self):
        return self.tpOp('start')

    def restart(self):
        return self.tpOp('restart')

    def service_admin(self):
        if mw.isAppleSystem():
            return mw.returnJson(False, '仅支持Linux!')

        args = self.getArgs()
        check = self.checkArgs(args, ['serviceStatus'])
        if not check[0]:
            return check[1]

        method = args['serviceStatus']
        return self.tpOp(method)

    def initd_status(self):
        if mw.isAppleSystem():
            return "Apple Computer does not support"
        shell_cmd = 'systemctl status %s | grep loaded | grep "enabled;"' % (
            self.getPluginName())
        data = mw.execShell(shell_cmd)
        if data[0] == '':
            return 'fail'
        return 'ok'

    def initd_install(self):
        if mw.isAppleSystem():
            return "Apple Computer does not support"

        mw.execShell('systemctl enable ' + self.getPluginName())
        return 'ok'

    def initd_uninstall(self):
        if mw.isAppleSystem():
            return "Apple Computer does not support"

        mw.execShell('systemctl disable ' + self.getPluginName())
        return 'ok'

    def set_site_status(self):
        args = self.getArgs()
        check = self.checkArgs(args, ['siteName'])
        if not check[0]:
            return check[1]

        siteName = args['siteName']
        siteInfo = self.__getFind(siteName)
        if not siteInfo:
            return mw.returnJson(False, '指定站点不存在!')
        try:
            siteInfo['open'] = not siteInfo['open']
        except:
            siteInfo['open'] = not siteInfo['open']

        m_logs = {True: '开启', False: '关闭'}
        self.writeLog('%s站点[%s]防篡改保护' %
                      (m_logs[siteInfo['open']], siteInfo['siteName']))
        self.siteReload(siteInfo)
        self.saveSiteConfig(siteInfo)
        self.restart()
        return mw.returnJson(True, '设置成功!')

    def get_run_logs(self):
        log_file = self.getServerDir() + '/service.log'
        return mw.returnJson(True, mw.getLastLine(log_file, 200))

    # 取文件指定尾行数
    def getNumLines(self, path, num, p=1):
        pyVersion = sys.version_info[0]
        try:
            import cgi
            if not os.path.exists(path):
                return ""
            start_line = (p - 1) * num
            count = start_line + num
            fp = open(path, 'rb')
            buf = ""
            fp.seek(-1, 2)
            if fp.read(1) == "\n":
                fp.seek(-1, 2)
            data = []
            b = True
            n = 0
            for i in range(count):
                while True:
                    newline_pos = str.rfind(str(buf), "\n")
                    pos = fp.tell()
                    if newline_pos != -1:
                        if n >= start_line:
                            line = buf[newline_pos + 1:]
                            try:
                                data.append(json.loads(cgi.escape(line)))
                            except:
                                pass
                        buf = buf[:newline_pos]
                        n += 1
                        break
                    else:
                        if pos == 0:
                            b = False
                            break
                        to_read = min(4096, pos)
                        fp.seek(-to_read, 1)
                        t_buf = fp.read(to_read)
                        if pyVersion == 3:
                            if type(t_buf) == bytes:
                                t_buf = t_buf.decode('utf-8')
                        buf = t_buf + buf
                        fp.seek(-to_read, 1)
                        if pos - to_read == 0:
                            buf = "\n" + buf
                if not b:
                    break
            fp.close()
        except:
            return []
        if len(data) >= 2000:
            arr = []
            for d in data:
                arr.insert(0, json.dumps(d))
            mw.writeFile(path, "\n".join(arr))
        return data

    def get_safe_logs(self):

        args = self.getArgs()
        check = self.checkArgs(args, ['siteName'])
        if not check[0]:
            return check[1]

        siteName = args['siteName']

        data = {}
        path = self.getPluginDir() + '/sites/' + siteName + '/day'
        data['days'] = self.getDays(path)

        if not data['days']:
            data['logs'] = []
        else:
            p = 1
            if hasattr(args, 'p'):
                p = args['p']

            day = data['days'][0]
            if hasattr(args, 'day'):
                day = args['day']
            data['get_day'] = day
            logs_path = path + '/' + day + '/logs.json'
            data['logs'] = self.getNumLines(logs_path, 2000, int(p))
        return mw.returnJson(True, 'ok', data)

    def get_site_find(self):
        args = self.getArgs()
        check = self.checkArgs(args, ['siteName'])
        if not check[0]:
            return check[1]

        siteName = args['siteName']
        data = self.__getFind(siteName)
        return mw.returnJson(True, 'ok', data)

    def siteReload(self, siteInfo):
        cmd = "python3 {} {}".format(
            mw.getPluginDir() + '/tamper_proof_service.py unlock', siteInfo['path'])
        mw.execShell(cmd)
        tip_file = mw.getServerDir() + '/tips/' + siteInfo['siteName'] + '.pl'
        if os.path.exists(tip_file):
            os.remove(tip_file)

    def remove_protect_ext(self):
        args = self.getArgs()
        check = self.checkArgs(args, ['siteName', 'protectExt'])
        if not check[0]:
            return check[1]

        siteName = args['siteName']
        protectExt = args['protectExt'].strip()

        siteInfo = self.__getFind(siteName)

        if not siteInfo:
            return mw.returnJson(False, '指定站点不存在!')
        if not protectExt:
            return mw.returnJson(False, '被删除的保护列表不能为空')

        for protectExt in protectExt.split(','):
            if not protectExt in siteInfo['protectExt']:
                continue
            siteInfo['protectExt'].remove(protectExt)
            self.writeLog('站点[%s]从受保护列表中删除[.%s]' %
                          (siteInfo['siteName'], protectExt))
        self.siteReload(siteInfo)
        self.saveSiteConfig(siteInfo)
        return mw.returnJson(True, '删除成功!')

    def add_protect_ext(self):
        args = self.getArgs()
        check = self.checkArgs(args, ['siteName', 'protectExt'])
        if not check[0]:
            return check[1]

        siteName = args['siteName']
        protectExt = args['protectExt'].strip()

        siteInfo = self.__getFind(siteName)
        if not siteInfo:
            return mw.returnJson(False, '指定站点不存在!')
        protectExt = protectExt.lower()
        for protectExt in protectExt.split("\n"):
            if protectExt[0] == '/':
                if os.path.isdir(protectExt):
                    continue
            if protectExt in siteInfo['protectExt']:
                continue
            siteInfo['protectExt'].insert(0, protectExt)
            self.writeLog('站点[%s]添加文件类型或文件名[.%s]到受保护列表' %
                          (siteInfo['siteName'], protectExt))
        self.siteReload(siteInfo)
        self.saveSiteConfig(siteInfo)
        return mw.returnJson(True, '添加成功!')

    def add_excloud(self):
        args = self.getArgs()
        check = self.checkArgs(args, ['siteName', 'excludePath'])
        if not check[0]:
            return check[1]

        siteName = args['siteName']
        excludePath = args['excludePath'].strip()
        siteInfo = self.__getFind(siteName)
        if not siteInfo:
            return mw.returnJson(False, '指定站点不存在!')

        if not excludePath:
            return mw.returnJson(False, '排除内容不能为空')

        for excludePath in excludePath.split('\n'):
            if not excludePath:
                continue
            if excludePath.find('/') != -1:
                if not os.path.exists(excludePath):
                    continue
            excludePath = excludePath.lower()
            if excludePath[-1] == '/':
                excludePath = excludePath[:-1]
            if excludePath in siteInfo['excludePath']:
                continue
            siteInfo['excludePath'].insert(0, excludePath)
            self.writeLog('站点[%s]添加排除目录名[%s]到排除列表' %
                          (siteInfo['siteName'], excludePath))

        self.siteReload(siteInfo)
        self.saveSiteConfig(siteInfo)
        return mw.returnJson(True, '添加成功!')

    def remove_excloud(self):
        args = self.getArgs()
        check = self.checkArgs(args, ['siteName', 'excludePath'])
        if not check[0]:
            return check[1]

        siteName = args['siteName']
        siteInfo = self.__getFind(siteName)
        excludePath = args['excludePath'].strip()
        if excludePath == '':
            return mw.returnJson(False, '排除文件或目录不能为空')
        if not siteInfo:
            return mw.returnJson(False, '指定站点不存在!')

        for excludePath in excludePath.split(','):
            if not excludePath:
                continue
            if not excludePath in siteInfo['excludePath']:
                continue
            siteInfo['excludePath'].remove(excludePath)
            self.writeLog('站点[%s]从排除列表中删除目录名[%s]' %
                          (siteInfo['siteName'], excludePath))
        self.siteReload(siteInfo)
        self.saveSiteConfig(siteInfo)
        return mw.returnJson(True, '删除成功!')

    def sim_test(self):
        args = self.getArgs()
        check = self.checkArgs(args, ['path'])
        if not check[0]:
            return check[1]

        path = args['path'].strip()
        if not os.path.exists(path):
            return mw.returnJson(False, "此目录不存在")

        # 判断是否安装php
        import site_api
        php_version = site_api.site_api().getPhpVersion()
        if not php_version:
            return mw.returnJson(False, "未安装PHP测试失败")

        php_path = '/www/server/php/' + php_version[1]['version'] + '/bin/php'
        php_name = path + "/" + str(int(time.time())) + ".php"
        if os.path.exists(php_name):
            mw.execShell("rm -rf %s" % php_name)
        # 写入
        cmd = php_path + \
            " -r \"file_put_contents('{}','{}');\"".format(php_name, php_name)
        mw.execShell(cmd)
        time.sleep(0.5)
        if os.path.exists(php_name):
            if os.path.exists(php_name):
                mw.execShell("rm -rf %s" % php_name)
            return mw.returnJson(False, "拦截失败,可能未开启防篡改")
        return mw.returnJson(True, "拦截成功")

    def set_site_status_all(self):
        args = self.getArgs()
        check = self.checkArgs(args, ['siteNames', 'siteState'])
        if not check[0]:
            return check[1]

        sites = self.getSites()
        siteState = True if args['siteState'] == '1' else False
        siteNames = json.loads(args['siteNames'])
        m_logs = {True: '开启', False: '关闭'}
        for i in range(len(sites)):
            if sites[i]['siteName'] in siteNames:
                sites[i]['open'] = siteState
                self.writeLog('%s站点[%s]防篡改保护' %
                              (m_logs[siteState], sites[i]['siteName']))
        self.writeSites(sites)
        return mw.returnJson(True, '批量设置成功')

    def get_index(self):
        self.syncSites()
        args = self.getArgs()
        day = None
        if 'day' in args:
            day = args['day']

        ser_status = self.status()
        ser_status_bool = False
        if ser_status == 'start':
            ser_status_bool = True
        data = {}
        data['open'] = ser_status_bool
        data['total'] = self.getTotal()
        data['sites'] = self.getSites()
        for i in range(len(data['sites'])):
            data['sites'][i]['total'] = self.getTotal(
                data['sites'][i]['siteName'], day)
        return mw.returnJson(True, 'ok', data)

    def get_speed(self):
        print("12")


if __name__ == "__main__":
    func = sys.argv[1]
    classApp = App()
    try:
        data = eval("classApp." + func + "()")
        print(data)
    except Exception as e:
        print(mw.getTracebackInfo())
