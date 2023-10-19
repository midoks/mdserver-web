# coding:utf-8

import sys
import io
import os
import time
import re
import hashlib
import json
import subprocess

sys.path.append(os.getcwd() + "/class/core")
import mw

app_debug = False
if mw.isAppleSystem():
    app_debug = True


class classApi:
    __MW_KEY = 'app'
    __MW_PANEL = 'http://127.0.0.1:7200'
    __VHOST_PATH = ''

    _buff_size = 1024 * 1024 * 2

    _REQUESTS = None
    _SPEED_FILE = None
    _INFO_FILE = None
    _SYNC_INFO = None

    # 如果希望多台面板，可以在实例化对象时，将面板地址与密钥传入
    def __init__(self, mw_panel=None, mw_key=None):
        if mw_panel:
            self.__MW_PANEL = mw_panel
            self.__MW_KEY = mw_key

        import requests
        if not self._REQUESTS:
            self._REQUESTS = requests.session()

        self._SPEED_FILE = getServerDir() + '/config/speed.json'
        self._INFO_FILE = getServerDir() + '/config/sync_info.json'
        self._SYNC_INFO = self.get_sync_info(None)
        self.__VHOST_PATH = mw.getServerDir() + '/web_conf'

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

    def makeSyncInfo(self, args):
        data = {}
        sites = []
        for i in args['sites']:
            # print('ss', i)
            if i == '':
                continue
            t = {'name': i}
            sites.append(t)
        data['sites'] = sites

        databases = []
        for i in args['databases']:
            # print('db:', i)
            if i == '':
                continue
            t = {'name': i}
            databases.append(t)
        data['databases'] = databases
        return data

    def fock_process(self, args):
        log_file = getServerDir() + '/sync.log'
        log_file_error = getServerDir() + '/sync_error.log'

        if os.path.exists(log_file_error):
            os.remove(log_file_error)
        if os.path.exists(log_file):
            os.remove(log_file)

        plugins_dir = mw.getServerDir() + '/mdserver-web'
        exe = "cd {0} && source bin/activate && python3 plugins/migration_api/index.py bg_process &>{1} &".format(
            plugins_dir, log_file_error)
        # mw.execShell(exe)
        # os.system(exe)
        subprocess.Popen(exe, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        time.sleep(1)
        # 检查是否执行成功
        if not getPid():
            return mw.returnJson(False, '创建进程失败!<br>{}'.format(mw.readFile(log_file_error)))
        return mw.returnJson(True, "迁移进程创建成功!")

    def set_sync_info(self, args):
        # 设置要被迁移的网站、数据库
        sync_info = self.makeSyncInfo(args)
        sync_info['total'] = 0
        sync_info['speed'] = 0
        for i in range(len(sync_info['sites'])):
            sync_info['sites'][i]['error'] = ''
            sync_info['sites'][i]['state'] = 0
            sync_info['total'] += 1
        for i in range(len(sync_info['databases'])):
            sync_info['databases'][i]['error'] = ''
            sync_info['databases'][i]['state'] = 0
            sync_info['total'] += 1
        mw.writeFile(self._INFO_FILE, json.dumps(sync_info))
        self.fock_process(None)
        return mw.returnJson(True, '设置成功!')

    def get_sync_info(self, args):
        # 获取要被迁移的网站、数据库
        if not os.path.exists(self._INFO_FILE):
            return mw.returnJson(False, '迁移信息不存在!')
        sync_info = json.loads(mw.readFile(self._INFO_FILE))
        if not args:
            return sync_info
        result = []
        for i in sync_info['sites']:
            i['type'] = "网站"
            result.append(i)
        for i in sync_info['databases']:
            i['type'] = "数据库"
            result.append(i)
        return result

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

    def sendPlugins(self, name, func, args, timeout=36000):
        url = '/plugins/run'

        data = {}
        data['name'] = name
        data['func'] = func
        data['args'] = json.dumps(args).replace(": ", ":").replace(", ", ",")
        r = self.send(url, data, timeout)
        if r['status']:
            return json.loads(r['data'])
        return r

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

    def error(self, error_msg, is_exit=False):
        # 发生错误
        write_log("=" * 50)
        write_log("|-发生时间: {}".format(mw.formatDate()))
        write_log("|-错误信息: {}".format(error_msg))
        if is_exit:
            write_log("|-处理结果: 终止迁移任务")
            sys.exit(0)
        write_log("|-处理结果: 忽略错误, 继续执行")

    def upload_file(self, sfile, dfile, chmod=None):
        # 上传文件
        if not os.path.exists(sfile):
            write_log("|-指定目录不存在{}".format(sfile))
            return False
        pdata = self.__get_key_data()
        pdata['name'] = os.path.basename(dfile)
        pdata['path'] = os.path.dirname(dfile)
        pdata['size'] = os.path.getsize(sfile)
        pdata['start'] = 0
        if chmod:
            mode_user = self.get_mode_and_user(os.path.dirname(sfile))
            pdata['dir_mode'] = mode_user['mode'] + ',' + mode_user['user']
            mode_user = self.get_mode_and_user(sfile)
            pdata['file_mode'] = mode_user['mode'] + ',' + mode_user['user']
        f = open(sfile, 'rb')

        return self.send_file(pdata, f)

    def close_sync(self, args):
        # 取消迁移
        mw.execShell("kill -9 {}".format(self.get_pid()))
        mw.execShell(
            "kill -9 $(ps aux|grep index.py|grep -v grep|awk '{print $2}')")
        # 删除迁移配置
        time.sleep(1)
        if os.path.exists(self._INFO_FILE):
            os.remove(self._INFO_FILE)
        if os.path.exists(self._SPEED_FILE):
            os.remove(self._SPEED_FILE)
        return mw.returnJson(True, '已取消迁移任务!')

    def send_file(self, pdata, f):
        success_num = 0  # 连续发送成功次数
        max_buff_size = int(1024 * 1024 * 2)  # 最大分片大小
        min_buff_size = int(1024 * 32)  # 最小分片大小
        err_num = 0  # 连接错误计数
        max_err_num = 10  # 最大连接错误重试次数
        up_buff_num = 5  # 调整分片的触发次数
        timeout = 60  # 每次发送分片的超时时间
        split_num = 0
        split_done = 0
        total_time = 0
        self.write_speed('done', "正在传输文件")
        self.write_speed('size', pdata['size'])
        self.write_speed('used', 0)
        self.write_speed('speed', 0)
        write_log("|-上传文件[{}], 总大小：{}, 当前分片大小为：{}".format(pdata['name'],
                                                          toSize(pdata['size']), toSize(self._buff_size)))
        while True:
            buff_size = self._buff_size
            max_buff = int(pdata['size'] - pdata['start'])
            if max_buff < buff_size:
                buff_size = max_buff
            files = {"blob": f.read(buff_size)}
            start_time = time.time()

            try:
                url = self.__MW_PANEL + '/api/files/upload_segment'
                res = self._REQUESTS.post(
                    url, data=pdata, files=files, timeout=30000)

                success_num += 1
                err_num = 0
                # 连续5次分片发送成功的情况下尝试调整分片大小, 以提升上传效率
                if success_num > up_buff_num and self._buff_size < max_buff_size:
                    self._buff_size = int(self._buff_size * 2)
                    success_num = up_buff_num - 3  # 如再顺利发送3次则继续提升分片大小
                    if self._buff_size > max_buff_size:
                        self._buff_size = max_buff_size
                    write_log(
                        "|-发送顺利, 尝试调整分片大小为: {}".format(toSize(self._buff_size)))
            except Exception as e:
                times = time.time() - start_time
                total_time += times
                ex = str(e)
                if ex.find('Read timed out') != -1 or ex.find('Connection aborted') != -1:
                    # 发生超时的时候尝试调整分片大小, 以确保网络情况不好的时候能继续上传
                    self._buff_size = int(self._buff_size / 2)
                    if self._buff_size < min_buff_size:
                        self._buff_size = min_buff_size
                    success_num = 0
                    write_log(
                        "|-发送超时, 尝试调整分片大小为: {}".format(toSize(self._buff_size)))
                    continue

                # 如果连接超时
                if ex.find('Max retries exceeded with') != -1 and err_num <= max_err_num:
                    err_num += 1
                    write_log("|-连接超时, 第{}次重试".format(err_num))
                    time.sleep(1)
                    continue

                # 超过重试次数
                write_log("|-上传失败, 跳过本次上传任务")
                write_log(mw.getTracebackInfo())
                return False

            result = res.json()
            times = time.time() - start_time
            total_time += times

            if type(result) == int:
                if result == split_done:
                    split_num += 1
                else:
                    split_num = 0
                split_done = result
                if split_num > 10:
                    write_log("|-上传失败, 跳过本次上传任务")
                    return False
                if result > pdata['size']:
                    write_log("|-上传失败, 跳过本次上传任务")
                    return False
                self.write_speed('used', result)
                self.write_speed('speed', int(buff_size / times))
                write_log("|-已上传 {},上传速度 {}/s, 共用时 {}分{:.2f}秒,  {:.2f}%".format(toSize(float(result)), toSize(
                    buff_size / times), int(total_time // 60), total_time % 60, (float(result) / float(pdata['size']) * 100)))
                pdata['start'] = result  # 设置断点
            else:
                if not result['status']:  # 如果服务器响应上传失败
                    write_log(result['msg'])
                    return False

                if pdata['size']:
                    self.write_speed('used', pdata['size'])
                    self.write_speed('speed', int(buff_size / times))
                    write_log("|-已上传 {},上传速度 {}/s, 共用时 {}分{:.2f}秒,  {:.2f}%".format(toSize(float(pdata['size'])), toSize(
                        buff_size / times), int(total_time // 60), total_time % 60, (float(pdata['size']) / float(pdata['size']) * 100)))
                break

        self.write_speed('total_size', pdata['size'])
        self.write_speed('end_time', int(time.time()))
        write_log("|-总耗时：{} 分钟, {:.2f} 秒, 平均速度：{}/s".format(int(total_time //
                                                                60), total_time % 60, toSize(pdata['size'] / total_time)))
        return True

    def send_list(self, s_files):
        # 发送文件列表
        for f in s_files:
            if not os.path.exists(f[0]):
                continue
            self.send_file_list(f[0], f[0])

    def send_file_list(self, spath, dpath):

        if os.path.islink(spath):
            dpath = os.readlink(spath)
            # mw.buildSoftLink(spath, dpath, True)
            self.send('/files/exec_shell',
                      {"shell": 'ln -sf "' + spath + '" "' + dpath + '"', "path": "/www"}, 30)
            return True

        if not os.path.isdir(spath):
            return self.upload_file(spath, dpath, True)

        # 创建目录
        self.send('/files/create_dir', {"path": dpath})

        backup_path = mw.getRootDir() + '/backup'
        if not os.path.exists(backup_path):
            os.makedirs(backup_path, 384)

        zip_file = backup_path + \
            "/psync_tmp_{}.tar.gz".format(os.path.basename(spath))
        zip_dst = mw.getRunDir() + '/tmp/psync_tmp_{}.tar.gz'.format(
            os.path.basename(dpath))
        write_log("|-正在压缩目录[{}]...".format(spath))
        self.write_speed('done', '正在压缩')

        mw.execShell(
            "cd {} && tar zcvf {} ./ > /dev/null".format(spath, zip_file))
        if not os.path.exists(zip_file):
            self.error("目录[{}]打包失败!".format(spath))
            return False

        self.set_mode(zip_file, 600)
        if not self.upload_file(zip_file, zip_dst, True):
            self.error("目录[{}]上传失败!".format(spath))
            if os.path.exists(zip_file):
                os.remove(zip_file)
            return False

        if os.path.exists(zip_file):
            os.remove(zip_file)
        write_log("|-正在解压文件到目录[{}]...".format(dpath))
        self.write_speed('done', '正在解压')

        self.send('/files/uncompress',
                  {"sfile": zip_dst, "dfile": dpath, 'path': dpath})
        self.send('/files/exec_shell',
                  {"shell": "rm -f " + zip_dst, "path": "/www"}, 30)
        return True

    def state(self, stype, index, state, error=''):
        # 设置状态
        self._SYNC_INFO[stype][index]['state'] = state
        self._SYNC_INFO[stype][index]['error'] = error
        if self._SYNC_INFO[stype][index]['state'] == 1:
            self._SYNC_INFO['speed'] += 1
        self.save()

    def save(self):
        # 保存迁移配置
        mw.writeFile(self._INFO_FILE, json.dumps(self._SYNC_INFO))

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
            self.state('sites', index, -1, err_msg)
            self.error(err_msg)
            return False
        return True

    def send_site(self, siteInfo, index):
        if not os.path.exists(siteInfo['path']):
            err_msg = "网站根目录[{}]不存在,跳过!".format(siteInfo['path'])
            self.state('sites', index, -1, err_msg)
            self.error(err_msg)
            return False

        self.create_site(siteInfo, index)
        # if not self.create_site(siteInfo, index):
        #     return False

        s_files = [
            [self.__VHOST_PATH +
                '/nginx/vhost/{}.conf'.format(siteInfo['name']), "网站配置文件"],
            [self.__VHOST_PATH +
             '/nginx/pass/{}.conf'.format(siteInfo['name']), "PASS"],
            [self.__VHOST_PATH +
             '/nginx/rewrite/{}.conf'.format(siteInfo['name']), "伪静态配置"],
            [self.__VHOST_PATH +
             '/nginx/redirect/{}'.format(siteInfo['name']), "重定向配置"],
            [self.__VHOST_PATH +
             '/nginx/proxy/{}'.format(siteInfo['name']), "反向代理配置"],
            [self.__VHOST_PATH +
                "/letsencrypt/{}".format(siteInfo['name']), "网站[LETS]SSL证书"],
            [self.__VHOST_PATH + "/ssl/" + siteInfo['name'], "网站SSL目录"],
        ]

        if not mw.isAppleSystem():
            acme_dir = mw.getAcmeDomainDir(siteInfo['name'])
            s_files.append([acme_dir, "网站[ACME]SSL证书"])

        s_files.append(
            [self.__VHOST_PATH + "/ssl/{}/fullchain.pem".format(siteInfo['name']), "网站SSL[fullchain]证书"])
        s_files.append(
            [self.__VHOST_PATH + "/ssl/{}/privkey.pem".format(siteInfo['name']), "网站SSL[privkey]证书"])

        self.send_list(s_files)

        if not self.send_file_list(siteInfo['path'], siteInfo['path']):
            self.state('sites', index, -1, '数据传输失败!')
            return False

    def sync_site(self):
        data = getCfgData()
        sites = self._SYNC_INFO['sites']
        for i in range(len(sites)):

            site_name = sites[i]['name']
            try:
                self.state('sites', i, 1)
                siteInfo = mw.M('sites').where('name=?', (site_name,)).field(
                    'id,name,path,ps,status,edate,addtime').find()

                if not siteInfo:
                    err_msg = "指定站点[{}]不存在!".format(site_name)
                    self.state('sites', i, -1, err_msg)
                    self.error(err_msg)
                    continue
                pid = siteInfo['id']

                siteInfo['port'] = mw.M('domain').where(
                    'pid=? and name=?', (pid, site_name,)).getField('port')

                siteInfo['domain'] = mw.M('domain').where(
                    'pid=? and name!=?', (pid, site_name)).field('name,port').select()

                siteInfo['binding'] = mw.M('binding').where(
                    'pid=?', (id,)).field('domain,path,port').select()

                if self.send_site(siteInfo, i):
                    self.state('sites', i, 2)
                write_log("=" * 50)
            except Exception as e:
                self.error(mw.getTracebackInfo())

    def getConf(self, mtype='mysql'):
        path = mw.getServerDir() + '/' + mtype + '/etc/my.cnf'
        return path

    def getSocketFile(self, mtype='mysql'):
        file = self.getConf(mtype)
        content = mw.readFile(file)
        rep = 'socket\s*=\s*(.*)'
        tmp = re.search(rep, content)
        return tmp.groups()[0].strip()

    def getDbPort(self, mtype='mysql'):
        file = self.getConf(mtype)
        content = mw.readFile(file)
        rep = 'port\s*=\s*(.*)'
        tmp = re.search(rep, content)
        return tmp.groups()[0].strip()

    def getDbConn(self, mtype='mysql', db='databases'):
        my_db_pos = mw.getServerDir() + '/' + mtype
        conn = mw.M(db).dbPos(my_db_pos, 'mysql')
        return conn

    def getMyConn(self, mtype='mysql'):
        # pymysql
        db = mw.getMyORM()

        db.setPort(self.getDbPort(mtype))
        db.setSocket(self.getSocketFile(mtype))
        pwd = self.getDbConn(mtype, 'config').where(
            'id=?', (1,)).getField('mysql_root')
        db.setPwd(pwd)
        return db

    def getDbList(self):
        conn = self.getDbConn()
        alist = conn.field(
            'id,name,username,password,ps').order("id desc").select()
        return alist

    def getDbInfo(self, name):
        conn = self.getDbConn()
        info = conn.field(
            'id,name,username,password,ps').where('name=?', (name,)).find()
        return info

    def mapToList(self, map_obj):
        # map to list
        try:
            if type(map_obj) != list and type(map_obj) != str:
                map_obj = list(map_obj)
            return map_obj
        except:
            return []

    # 取数据库权限
    def getDatabaseAccess(self, name):
        return '127.0.0.1'
        try:
            conn = self.getMyConn()
            users = conn.query(
                "select Host from mysql.user where User='" + name + "' AND Host!='localhost'")
            users = self.mapToList(users)
            if len(users) < 1:
                return "127.0.0.1"
            accs = []
            for c in users:
                accs.append(c[0])
            userStr = ','.join(accs)
            return userStr
        except:
            return '127.0.0.1'

    def isSqlError(self, mysqlMsg):
        # 检测数据库执行错误
        mysqlMsg = str(mysqlMsg)
        if "MySQLdb" in mysqlMsg:
            return mw.returnData(False, 'DATABASE_ERR_MYSQLDB')
        if "2002," in mysqlMsg or '2003,' in mysqlMsg:
            return mw.returnData(False, 'DATABASE_ERR_CONNECT')
        if "using password:" in mysqlMsg:
            return mw.returnData(False, 'DATABASE_ERR_PASS')
        if "Connection refused" in mysqlMsg:
            return mw.returnData(False, 'DATABASE_ERR_CONNECT')
        if "1133" in mysqlMsg:
            return mw.returnData(False, 'DATABASE_ERR_NOT_EXISTS')
        return None

    def getDatabaseCharacter(self, db_name):
        try:
            conn = self.getMyConn()
            tmp = conn.query("show create database `%s`" % db_name.strip(), ())
            # print(tmp)
            c_type = str(re.findall(r"SET\s+([\w\d-]+)\s", tmp[0][1])[0])
            c_types = ['utf8', 'utf-8', 'gbk', 'big5', 'utf8mb4']
            if not c_type.lower() in c_types:
                return 'utf8'
            return c_type
        except Exception as e:
            # print(str(e))
            return 'utf8'

    # 创建远程数据库
    def create_database(self, dbInfo, index):
        pdata = {}
        pdata['name'] = dbInfo['name']
        pdata['db_user'] = dbInfo['username']
        pdata['password'] = dbInfo['password']
        pdata['dataAccess'] = dbInfo['accept']
        if dbInfo['accept'] != '%' and dbInfo['accept'] != '127.0.0.1':
            pdata['dataAccess'] = '127.0.0.1'
        pdata['address'] = dbInfo['accept']
        pdata['ps'] = dbInfo['ps']
        pdata['codeing'] = dbInfo['character']

        result = self.sendPlugins('mysql', 'add_db', pdata)
        if result['status']:
            return True
        err_msg = '数据库[{}]创建失败,{}'.format(dbInfo['name'], result['msg'])
        self.state('databases', index, -1, err_msg)
        self.error(err_msg)
        return False

    # 数据库密码处理
    def myPass(self, act, root):
        # conf_file = '/etc/my.cnf'
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

    def recognizeDbMode(self):
        conf = self.getConf('mysql')
        con = mw.readFile(conf)

        path = mw.getServerDir() + '/mysql'
        rep = r"!include %s/(.*)?\.cnf" % (path + "/etc/mode",)
        mode = 'none'
        try:
            data = re.findall(rep, con, re.M)
            mode = data[0]
        except Exception as e:
            pass
        return mode

    def export_database(self, name, index):
        self.write_speed('done', '正在导出数据库')
        write_log("|-正在导出数据库{}...".format(name))
        conn = self.getMyConn()
        result = conn.execute("show databases")
        isError = self.isSqlError(result)
        if isError:
            err_msg = '数据库[{}]导出失败,{}!'.format(name, isError['msg'])
            self.state('databases', index, -1, err_msg)
            self.error(err_msg)
            return None

        root = self.getDbConn('mysql', 'config').where(
            'id=?', (1,)).getField('mysql_root')

        backup_path = mw.getRootDir() + '/backup'
        if not os.path.exists(backup_path):
            os.makedirs(backup_path, 384)

        backup_name = backup_path + '/psync_import.sql.gz'
        if os.path.exists(backup_name):
            os.remove(backup_name)

        root_dir = mw.getServerDir() + '/mysql'
        my_cnf = self.getConf('mysql')

        mode = self.recognizeDbMode()
        gtid_option = ''
        if mode == 'gtid':
            gtid_option = ' --set-gtid-purged=off '

        self.myPass(True, root)
        cmd = root_dir + "/bin/mysqldump --defaults-file=" + my_cnf + " --default-character-set=" + \
            self.getDatabaseCharacter(
                name) + gtid_option + " --force --opt \"" + name + "\" | gzip > " + backup_name
        # print(cmd)
        mw.execShell(cmd)

        self.myPass(False, root)
        if not os.path.exists(backup_name) or os.path.getsize(backup_name) < 30:
            if os.path.exists(backup_name):
                os.remove(backup_name)
            err_msg = '数据库[{}]导出失败!'.format(name)
            self.state('databases', index, -1, err_msg)
            self.error(err_msg)
            write_log("失败")
            return None
        write_log("成功")
        return backup_name

    def send_database(self, dbInfo, index):
        # print(dbInfo)
        # 创建远程库
        # if not self.create_database(dbInfo, index):
        #     return False

        self.create_database(dbInfo, index)
        filename = self.export_database(dbInfo['name'], index)
        if not filename:
            return False

        db_dir = '/www/backup/import'
        new_db_name = 'psync_import_{}.sql.gz'.format(dbInfo['name'])
        upload_file = db_dir + '/' + new_db_name
        self.send('/files/exec_shell',
                  {"shell": "rm -f " + upload_file, "path": "/www"}, 30)

        if self.upload_file(filename, upload_file):
            self.write_speed('done', '正在导入数据库')
            write_log("|-正在导入数据库{}...".format(dbInfo['name']))

            t = self.sendPlugins('mysql', 'import_db_external', {
                "file": new_db_name, "name": dbInfo['name']})
            # print(t)
            self.send('/files/exec_shell',
                      {"shell": "rm -f " + upload_file, "path": "/www"}, 30)
            return True
        self.state('databases', index, -1, "数据传输失败")
        return False

    def sync_database(self):
        data = getCfgData()

        databases = self._SYNC_INFO['databases']
        for i in range(len(databases)):
            db = databases[i]['name']
            try:
                self.state('databases', i, 1)
                sp_msg = "|-迁移数据库: [{}]".format(db)
                self.write_speed('action', sp_msg)
                write_log(sp_msg)
                dbInfo = self.getDbInfo(db)
                dbInfo['accept'] = self.getDatabaseAccess(db)
                dbInfo['character'] = self.getDatabaseCharacter(db)
                # print(dbInfo)
                if self.send_database(dbInfo, i):
                    self.state('databases', i, 2)
                write_log("=" * 50)
            except:
                self.error(mw.getTracebackInfo())

    def run(self):
        # 开始迁移
        # self.upload_file("/tmp/mysql-boost-5.7.39.tar.gz",
        # "/tmp/mysql-boost-5.7.39.tar.gz")

        # self.sync_other()
        self.sync_site()
        self.sync_database()
        # self.sync_path()
        self.write_speed('action', 'True')
        write_log('|-所有项目迁移完成!')


# 字节单位转换
def toSize(size):
    d = ('b', 'KB', 'MB', 'GB', 'TB')
    s = d[0]
    for b in d:
        if size < 1024:
            return ("%.2f" % size) + ' ' + b
        size = size / 1024
        s = b
    return ("%.2f" % size) + ' ' + b


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
        mw.writeFile(path, "{}")

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
    path = getServerDir() + '/config'
    if not os.path.exists(path):
        os.makedirs(path)
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

    speed_file = getServerDir() + '/config/speed.json'
    if os.path.exists(speed_file):
        os.remove(speed_file)

    sync_file = getServerDir() + '/config/sync_info.json'
    if os.path.exists(sync_file):
        os.remove(sync_file)

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
    return mw.returnJson(True, '获取成功!', data)


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
    return mw.returnJson(True, '同步数据,获取成功!', data)


def getPid():
    result = mw.execShell(
        "ps aux|grep 'plugins/migration_api/index.py bg_process' |grep -v grep|awk '{print $2}'|xargs")[0].strip()
    if not result:
        return None
    return result


def write_log(log_str):
    log_file = getServerDir() + '/sync.log'
    f = open(log_file, 'ab+')
    log_str += "\n"
    if __name__ == '__main__':
        print(log_str)
    f.write(log_str.encode('utf-8'))
    f.close()
    return True


def bgProcessRun():
    data = getCfgData()

    # demo_url = 'http://127.0.0.1:7200'
    # demo_key = 'HfJNKGP5RPqGvhIOyrwpXG4A2fTjSh9B'
    # api = classApi(demo_url, demo_key)
    api = classApi(data['url'], data['token'])
    api.run()
    return ''


def stepFour():
    if getPid():
        return mw.returnJson(True, '正在运行中..')
    args = getArgs()
    data = checkArgs(args, ['sites', 'databases'])
    if not data[0]:
        return data[1]

    sites = args['sites']
    databases = args['databases']

    data = getCfgData()
    args = {
        'sites': sites.strip(',').split(','),
        'databases': databases.strip(',').split(',')
    }
    api = classApi(data['url'], data['token'])
    return api.set_sync_info(args)


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
    data = getCfgData()
    api = classApi(data['url'], data['token'])
    sync_info = api.get_sync_info(None)
    speed_info['all_total'] = sync_info['total']
    speed_info['all_speed'] = sync_info['speed']
    speed_info['total_time'] = speed_info['end_time'] - speed_info['time']
    speed_info['total_time'] = str(int(speed_info[
        'total_time'] // 60)) + "分" + str(int(speed_info['total_time'] % 60)) + "秒"
    log_file = getServerDir() + '/sync.log'
    speed_info['log'] = mw.execShell("tail -n 10 {}".format(log_file))[0]
    speed_info['log_file'] = log_file
    return mw.returnJson(True, 'ok', speed_info)

if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print(status())
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
