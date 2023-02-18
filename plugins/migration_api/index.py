# coding:utf-8

import sys
import io
import os
import time
import re
import hashlib
import json

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


class classApi:
    __MW_KEY = 'app'
    __MW_PANEL = 'http://127.0.0.1:7200'

    _REQUESTS = None

    # 如果希望多台面板，可以在实例化对象时，将面板地址与密钥传入
    def __init__(self, mw_panel=None, mw_key=None):
        if mw_panel:
            self.__MW_PANEL = mw_panel
            self.__MW_KEY = mw_key

        import requests
        if not self._REQUESTS:
            self._REQUESTS = requests.session()

    # 计算MD5
    def __get_md5(self, s):
        m = hashlib.md5()
        m.update(s.encode('utf-8'))
        return m.hexdigest()

    # 构造带有签名的关联数组
    def __get_key_data(self):
        now_time = int(time.time())
        ready_data = {
            'request_token': self.__get_md5(str(now_time) + '' + self.__get_md5(self.__MW_KEY)),
            'request_time': now_time
        }
        return ready_data

    def __http_post_cookie(self, url, p_data, timeout=1800):
        try:
            # print(url)
            res = self._REQUESTS.post(url, p_data, timeout=timeout)
            return res.text
        except Exception as ex:
            ex = str(ex)
            if ex.find('Max retries exceeded with') != -1:
                return mw.returnJson(False, '连接服务器失败!')
            if ex.find('Read timed out') != -1 or ex.find('Connection aborted') != -1:
                return mw.returnJson(False, '连接超时!')
            return mw.returnJson(False, '连接服务器失败!')

    def send(self, url, args, timeout=600):
        url = self.__MW_PANEL + '/api' + url
        post_data = self.__get_key_data()  # 取签名
        post_data.update(args)
        result = self.__http_post_cookie(url, post_data, timeout)
        try:
            return json.loads(result)
        except Exception as e:
            return result

    # 取面板日志
    def getLogs(self):
        # 拼接URL地址
        url = self.__MW_PANEL + '/firewall/get_log_list'

        # 准备POST数据
        post_data = self.__get_key_data()  # 取签名
        post_data['limit'] = 10
        post_data['p'] = '1'

        # 请求面板接口
        result = self.__http_post_cookie(url, post_data)

        # 解析JSON数据
        return json.loads(result)


def getPluginName():
    return 'migration_api'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getConf():
    path = getServerDir() + "/ma.cfg"
    return path


def getCfgData():
    path = getConf()
    if not os.path.exists(path):
        mw.writeFile(path, '{}')

    t = mw.readFile(path)
    return json.loads(t)


def writeConf(data):
    path = getConf()
    mw.writeFile(path, json.dumps(data))
    return True


def getArgs():
    args = sys.argv[2:]
    tmp = {}
    # print(args)
    args_len = len(args)
    if args_len == 1:
        t = args[0].strip('{').strip('}')
        if t.strip() == '':
            tmp = []
        else:
            t = t.split(':', 1)
            tmp[t[0]] = t[1]
        tmp[t[0]] = t[1]
    elif args_len > 1:

        for i in range(len(args)):
            # print(args[i])
            t = args[i].split(':', 1)
            tmp[t[0]] = t[1]
    return tmp


def checkArgs(data, ck=[]):
    for i in range(len(ck)):
        if not ck[i] in data:
            return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, mw.returnJson(True, 'ok'))


def status():
    return 'start'


def initDreplace():
    return 'ok'


def getStepOneData():
    data = getCfgData()
    return mw.returnJson(True, 'ok', data)


def stepOne():
    args = getArgs()
    data = checkArgs(args, ['url', 'token'])
    if not data[0]:
        return data[1]

    url = args['url']
    token = args['token']

    api = classApi(url, token)
    # api = classApi('http://127.0.0.1:7200','HfJNKGP5RPqGvhIOyrwpXG4A2fTjSh9B')
    rdata = api.send('/task/count', {})
    if type(rdata) != int:
        return mw.returnJson(False, rdata['msg'])
    data = getCfgData()

    data['url'] = url
    data['token'] = token
    writeConf(data)

    return mw.returnJson(True, '验证成功')


# 获取本地服务器和环境配置
def get_src_config(args):
    serverInfo = {}
    serverInfo['status'] = True
    sdir = mw.getServerDir()

    serverInfo['webserver'] = '未安装'
    if os.path.exists(sdir + '/openresty/nginx/sbin/nginx'):
        serverInfo['webserver'] = 'OpenResty'
    serverInfo['php'] = []
    phpversions = ['52', '53', '54', '55', '56', '70', '71',
                   '72', '73', '74', '80', '81', '82', '83', '84']
    phpPath = sdir + '/php/'
    for pv in phpversions:
        if not os.path.exists(phpPath + pv + '/bin/php'):
            continue
        serverInfo['php'].append(pv)
    serverInfo['mysql'] = False
    if os.path.exists(sdir + '/mysql/bin/mysql'):
        serverInfo['mysql'] = True
    import psutil
    try:
        diskInfo = psutil.disk_usage('/www')
    except:
        diskInfo = psutil.disk_usage('/')

    serverInfo['disk'] = mw.toSize(diskInfo[2])
    return serverInfo


def get_dst_config(args):

    data = getCfgData()
    api = classApi(data['url'], data['token'])
    disk = api.send('/system/disk_info', {})
    info = api.send('/system/get_env_info', {})

    result = info['data']

    result['disk'] = disk
    return result


def stepTwo():
    data = {}
    data['local'] = get_src_config(None)
    data['remote'] = get_dst_config(None)
    return mw.returnJson(True, 'ok', data)


def get_src_info(args):
    # 获取本地服务器网站、数据库.
    data = {}
    data['sites'] = mw.M('sites').field(
        "id,name,path,ps,status,addtime").order("id desc").select()

    my_db_pos = mw.getServerDir() + '/mysql'
    conn = mw.M('databases').dbPos(my_db_pos, 'mysql')
    data['databases'] = conn.field('id,name,ps').order("id desc").select()
    return data


def stepThree():
    data = get_src_info(None)
    return mw.returnJson(True, 'ok', data)


def getPid():
    result = mw.execShell(
        "ps aux|grep index.py|grep -v grep|awk '{print $2}'|xargs")[0].strip()
    if not result:
        import psutil
        for pid in psutil.pids():
            if not os.path.exists('/proc/{}'.format(pid)):
                continue  # 检查pid是否还存在
            try:
                p = psutil.Process(pid)
            except:
                return None
            cmd = p.cmdline()
            if len(cmd) < 2:
                continue
            if cmd[1].find('psync_api_main.py') != -1:
                return pid
        return None


def bgProcessRun():
    time.sleep(10)
    return '123123'


def bgProcess():
    log_file = getServerDir() + '/sync.log'
    log_file_error = getServerDir() + '/sync_error.log'

    if os.path.exists(log_file_error):
        os.remove(log_file_error)
    if os.path.exists(log_file):
        os.remove(log_file)

    plugins_dir = mw.getServerDir() + '/mdserver-web'
    exe = "cd {0} && source bin/activate && nohup python3 plugins/migration_api/index.py bg_process &>{1} &".format(
        plugins_dir, log_file_error)

    os.system(exe)
    time.sleep(1)
    # 检查是否执行成功
    if not getPid():
        return mw.returnJson(False, '创建进程失败!<br>{}'.format(mw.readFile(log_file_error)))
    return mw.returnJson(True, "迁移进程创建成功!")


def stepFour():
    args = getArgs()
    data = checkArgs(args, ['sites', 'databases'])
    if not data[0]:
        return data[1]

    sites = args['sites']
    databases = args['databases']

    data = getCfgData()
    ready_data = {
        'sites': sites.strip(',').split(','),
        'databases': databases.strip(',').split(',')
    }
    data['ready'] = ready_data
    writeConf(data)
    return bgProcess()
    # return mw.returnJson(True, 'ok')


def get_speed_data():
    path = getServerDir() + '/config/speed.json'
    data = mw.readFile(path)
    return json.loads(data)


def get_speed(args):
    # 取迁移进度
    if not os.path.exists(self._SPEED_FILE):
        return public.returnMsg(False, '正在准备..')
    try:
        speed_info = json.loads(mw.readFile(self._SPEED_FILE))
    except:
        return False
    sync_info = self.get_sync_info(None)
    speed_info['all_total'] = sync_info['total']
    speed_info['all_speed'] = sync_info['speed']
    speed_info['total_time'] = speed_info['end_time'] - speed_info['time']
    speed_info['total_time'] = str(int(speed_info[
                                   'total_time'] // 60)) + "分" + str(int(speed_info['total_time'] % 60)) + "秒"
    log_file = '/www/server/panel/logs/psync.log'
    speed_info['log'] = public.ExecShell(
        "tail -n 10 {}".format(log_file))[0]
    # if len(speed_info['log']) > 20480 and speed_info['action'] != 'True':
    # return False
    return speed_info

if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print(status())
    elif func == 'start':
        print(start())
    elif func == 'stop':
        print(stop())
    elif func == 'get_conf':
        print(getStepOneData())
    elif func == 'step_one':
        print(stepOne())
    elif func == 'step_two':
        print(stepTwo())
    elif func == 'step_three':
        print(stepThree())
    elif func == 'step_four':
        print(stepFour())
    elif func == 'bg_process':
        print(bgProcessRun())
    else:
        print('error')
