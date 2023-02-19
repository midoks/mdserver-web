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
    _SPEED_FILE = None

    # 如果希望多台面板，可以在实例化对象时，将面板地址与密钥传入
    def __init__(self, mw_panel=None, mw_key=None):
        if mw_panel:
            self.__MW_PANEL = mw_panel
            self.__MW_KEY = mw_key

        import requests
        if not self._REQUESTS:
            self._REQUESTS = requests.session()

        self._SPEED_FILE = getServerDir() + '/config/speed.json'

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

    def write_speed(self, key, value):
        # 写进度
        if os.path.exists(self._SPEED_FILE):
            speed_info = json.loads(mw.readFile(self._SPEED_FILE))
        else:
            speed_info = {"time": int(time.time()), "size": 0, "used": 0, "total_size": 0,
                          "speed": 0, "action": "等待中", "done": "等待中", "end_time": int(time.time())}
        if not key in speed_info:
            speed_info[key] = 0
        if key == 'total_size':
            speed_info[key] += value
        else:
            speed_info[key] = value
        mw.writeFile(self._SPEED_FILE, json.dumps(speed_info))

    # 设置文件权限
    def set_mode(self, filename, mode):
        if not os.path.exists(filename):
            return False
        mode = int(str(mode), 8)
        os.chmod(filename, mode)
        return True

    def send(self, url, args, timeout=600):
        url = self.__MW_PANEL + '/api' + url
        post_data = self.__get_key_data()  # 取签名
        post_data.update(args)
        result = self.__http_post_cookie(url, post_data, timeout)
        try:
            return json.loads(result)
        except Exception as e:
            return result

    def get_mode_and_user(self, path):
        '''取文件或目录权限信息'''
        data = {}
        if not os.path.exists(path):
            return None
        stat = os.stat(path)
        data['mode'] = str(oct(stat.st_mode)[-3:])
        try:
            data['user'] = pwd.getpwuid(stat.st_uid).pw_name
        except:
            data['user'] = str(stat.st_uid)
        return data

    def upload_file(self, sfile, dfile, chmod=None):
        # 上传文件
        if not os.path.exists(sfile):
            write_log("|-指定目录不存在{}".format(sfile))
            return False
        pdata = self.__get_key_data()
        pdata['f_name'] = os.path.basename(dfile)
        pdata['f_path'] = os.path.dirname(dfile)
        pdata['f_size'] = os.path.getsize(sfile)
        pdata['f_start'] = 0
        if chmod:
            mode_user = self.get_mode_and_user(os.path.dirname(sfile))
            pdata['dir_mode'] = mode_user['mode'] + ',' + mode_user['user']
            mode_user = self.get_mode_and_user(sfile)
            pdata['file_mode'] = mode_user['mode'] + ',' + mode_user['user']
        f = open(sfile, 'rb')
        return self.send_file(pdata, f)

    def send_file(self, f):
        pass

    def save(self):
        # 保存迁移配置
        mw.writeFile(self._INFO_FILE, json.dumps(self._SYNC_INFO))

    def state(self, stype, index, state, error=''):
        # 设置状态
        self._SYNC_INFO[stype][index]['state'] = state
        self._SYNC_INFO[stype][index]['error'] = error
        if self._SYNC_INFO[stype][index]['state'] != 1:
            self._SYNC_INFO['speed'] += 1
        self.save()

    def format_domain(self, domain):
        # 格式化域名
        domains = []
        for d in domain:
            domains.append("{}:{}".format(d['name'], d['port']))
        return domains

    def create_site(self, siteInfo, index):
        pdata = {}
        domains = self.format_domain(siteInfo['domain'])

        pdata['webinfo'] = json.dumps(
            {"domain": siteInfo['name'], "domainlist": domains, "count": len(domains)})
        pdata['ps'] = siteInfo['ps']
        pdata['path'] = siteInfo['path']
        pdata['type'] = 'PHP'
        pdata['version'] = '00'
        pdata['type_id'] = '0'
        pdata['port'] = siteInfo['port']
        if not pdata['port']:
            pdata['port'] = 80

        result = self.send('/site/add', pdata)
        if not result['status']:
            err_msg = '站点[{}]创建失败, {}'.format(siteInfo['name'], result['msg'])
            # self.state('sites', index, -1, err_msg)
            # self.error(err_msg)
            return False
        return True

    def send_site(self, siteInfo, index):
        if not os.path.exists(siteInfo['path']):
            err_msg = "网站根目录[{}]不存在,跳过!".format(siteInfo['path'])
            self.state('sites', index, -1, err_msg)
            self.error(err_msg)
            return False
        if not self.create_site(siteInfo, index):
            return False

    def sync_site(self):
        data = getCfgData()
        sites = data['ready']['sites']
        for i in range(len(sites)):
            siteInfo = mw.M('sites').where('name=?', (sites[i],)).field(
                'id,name,path,ps,status,edate,addtime').find()

            if not siteInfo:
                err_msg = "指定站点[{}]不存在!".format(sites[i])
                # self.state('sites', i, -1, err_msg)
                # self.error(err_msg)
                continue
            pid = siteInfo['id']

            siteInfo['port'] = mw.M('domain').where(
                'pid=? and name=?', (pid, sites[i],)).getField('port')

            siteInfo['domain'] = mw.M('domain').where(
                'pid=? and name!=?', (pid, sites[i])).field('name,port').select()

            print(sites[i])
            print("dd:", mw.M('domain').where(
                'pid=? and name!=?', (pid, sites[i])).field('name,port').select())

            if self.send_site(siteInfo, i):
                self.state('sites', i, 2)
            write_log("=" * 50)
        print(sites)

    def run(self):
        # 开始迁移
        # mw.CheckMyCnf()
        # self.sync_other()
        self.sync_site()
        # self.sync_database()
        # self.sync_ftp()
        # self.sync_path()
        # self.write_speed('action', 'True')
        write_log('|-所有项目迁移完成!')


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
    # api =
    # classApi('http://127.0.0.1:7200','HfJNKGP5RPqGvhIOyrwpXG4A2fTjSh9B')
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
        "ps aux|grep plugins/migration_api/index.py|grep -v grep|awk '{print $2}'|xargs")[0].strip()
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
            if cmd[1].find('plugins/migration_api/index.py') != -1:
                return pid
        return None


def write_log(log_str):
    log_file = getServerDir() + '/sync.log'
    f = open(log_file, 'ab+')
    log_str += "\n"
    f.write(log_str.encode('utf-8'))
    f.close()
    return True


def bgProcessRun():
    data = getCfgData()
    api = classApi(data['url'], data['token'])
    api.run()
    return ''


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


def getSpeed():
    # 取迁移进度
    path = getServerDir() + '/config/speed.json'
    if not os.path.exists(path):
        return mw.returnJson(False, '正在准备..')
    try:
        speed_info = json.loads(mw.readFile(path))
    except:
        return mw.returnJson(False, '正在准备..')
    sync_info = self.get_sync_info(None)
    speed_info['all_total'] = sync_info['total']
    speed_info['all_speed'] = sync_info['speed']
    speed_info['total_time'] = speed_info['end_time'] - speed_info['time']
    speed_info['total_time'] = str(int(speed_info[
        'total_time'] // 60)) + "分" + str(int(speed_info['total_time'] % 60)) + "秒"
    log_file = getServerDir() + '/migration_api/sync.log'
    speed_info['log'] = mw.execShell("tail -n 10 {}".format(log_file))[0]
    return mw.returnJson(True, 'ok', speed_info)

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
    elif func == 'get_speed':
        print(getSpeed())
    else:
        print('error')
