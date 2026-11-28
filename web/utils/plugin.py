# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os
import sys
import re
import json
import threading
import subprocess
import multiprocessing

import core.mw as mw
import thisdb

class pg_thread(threading.Thread):

    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        self.result = self.func(*self.args)

    def getResult(self):
        try:
            return self.result
        except Exception:
            return None

class plugin(object):

    def_plugin_type = [
        {
            "title":"全部",
            "type":0,
            "ps":""
        },
        {
            "title":"已安装",
            "type":-1,
            "ps":""
        },
        {
            "title":"运行环境",
            "type":1,
            "ps":""
        },
        {
            "title":"数据软件",
            "type":2,
            "ps":""
        },
        {
            "title":"代码管理",
            "type":3,
            "ps":""
        },
        {
            "title":"系统工具",
            "type":4,
            "ps":""
        },
        {
            "title":"其他插件",
            "type":5,
            "ps":""
        },
        {
            "title":"辅助插件",
            "type":6,
            "ps":""
        },
        {
            "title":"AI插件",
            "type":7,
            "ps":""
        }
    ]

    __plugin_dir = 'plugins'
    __tasks = None

    __plugin_status_cachekey = 'plugin_list_status'
    __plugin_status_data = None

    # lock
    _instance_lock = threading.Lock()

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(plugin, "_instance"):
            with plugin._instance_lock:
                if not hasattr(plugin, "_instance"):
                    plugin._instance = plugin(*args, **kwargs)
        return plugin._instance

    """插件类初始化"""
    def __init__(self):
        self.__plugin_dir = mw.getPluginDir()


    def getIndexList(self):
        indexList = thisdb.getOptionByJson('display_index')
        plist = []
        for i in indexList:
            tmp = i.split('-')
            tmp_len = len(tmp)
            plugin_name = tmp[0]
            plugin_ver = tmp[1]
            if tmp_len > 2:
                tmpArr = tmp[0:tmp_len - 1]
                plugin_name = '-'.join(tmpArr)
                plugin_ver = tmp[tmp_len - 1]

            read_json_file = self.__plugin_dir + '/' + plugin_name + '/info.json'
            if os.path.exists(read_json_file):
                content = mw.readFile(read_json_file)
                try:
                    data = json.loads(content)
                    data = self.makeCoexistList(data)
                    for index in range(len(data)):
                        if data[index]['coexist']:
                            if data[index]['versions'] == plugin_ver or plugin_ver in data[index]['versions']:
                                data[index]['display'] = True
                                plist.append(data[index])
                                continue
                        else:
                            data[index]['display'] = True
                            plist.append(data[index])

                except Exception as e:
                    print('getIndexList:', mw.getTracebackInfo())

        plist = self.checkStatusMThreadsByCache(plist)
        return mw.returnData(True, 'ok', plist)

    def init(self):
        plugin_names = {
            'openresty': '1.31.1',
            'php': '74',
            'swap': '1.1',
            'mysql': '5.7',
            'phpmyadmin': '4.4.15',
        }

        pn_dir = mw.getPluginDir()
        pn_server_dir = mw.getServerDir()
        pn_list = []
        for pn in plugin_names:
            info = {}
            pn_json = pn_dir + '/' + pn + '/info.json'
            pn_server = pn_server_dir + '/' + pn
            if not os.path.exists(pn_server):

                tmp = mw.readFile(pn_json)
                tmp = json.loads(tmp)

                info['title'] = tmp['title']
                info['name'] = tmp['name']
                info['versions'] = tmp['versions']
                info['default_ver'] = plugin_names[pn]
                pn_list.append(info)
            else:
                return mw.returnData(False, 'ok')

        return mw.returnData(True, 'ok', pn_list)

    def initInstall(self, plugin_list):
        try:
            pn_list = json.loads(plugin_list)
            for pn in pn_list:
                name = pn['name']
                version = pn['version']
                # 防止目录穿越/命令注入
                if not re.fullmatch(r'[A-Za-z0-9_.-]+', name) or '..' in name:
                    continue
                info_file = self.__plugin_dir + '/' + name + '/' + 'info.json'
                pluginInfo = json.loads(mw.readFile(info_file))
                self.hookInstall(pluginInfo)

                cmd = 'cd {0} && bash {1} install {2}'.format(
                    mw.quote(mw.getPluginDir() + '/' + name),
                    mw.quote(pluginInfo['shell']),
                    mw.quote(version)
                )
                title = '安装[' + name + '-' + version + ']'
                thisdb.addTask(name=title,cmd=cmd)
            os.mkdir(mw.getServerDir() + '/php')
            # 任务执行相关
            mw.triggerTask()
            return mw.returnData(True, '添加成功')
        except Exception as e:
            return mw.returnData(False, mw.getTracebackInfo())

    def menuGetAbsPath(self, tag, path):
        if path[0:1] == '/':
            return path
        else:
            return mw.getPluginDir() + '/' + tag + '/' + path

    def addIndex(self, name, version):
        vname = name + '-' + version
        indexList = thisdb.getOptionByJson('display_index',default=[])

        if vname in indexList:
            return mw.returnData(False, '请不要重复添加!')
        if len(indexList) > 12:
            return mw.returnData(False, '首页最多只能显示12个软件!')

        indexList.append(vname)

        thisdb.setOption('display_index', json.dumps(indexList))
        return mw.returnData(True, '添加成功!')

    def removeIndex(self, name, version):
        vname = name + '-' + version
        indexList = thisdb.getOptionByJson('display_index')
        if not vname in indexList:
            return mw.returnData(True, '删除成功!!')
        indexList.remove(vname)
        thisdb.setOption('display_index', json.dumps(indexList))
        return mw.returnData(True, '删除成功!')

    def hookInstallOption(self, hook_name, info):
        hn_name = 'hook_'+hook_name
        src_data = thisdb.getOptionByJson(hn_name,type='hook',default=[])
        isNeedAdd = True
        for x in range(len(src_data)):
            if src_data[x]['title'] == info['title'] and src_data[x]['name'] == info['name']:
                isNeedAdd = False

        if isNeedAdd:
            src_data.append(info)

        thisdb.setOption(hn_name, json.dumps(src_data), type='hook')
        return True

    def hookUninstallOption(self, hook_name, info):
        hn_name = 'hook_'+hook_name
        src_data = thisdb.getOptionByJson(hn_name,type='hook',default=[])
        for idx in range(len(src_data)):
            if src_data[idx]['name'] == info['name']:
                src_data.remove(src_data[idx])
                break
        thisdb.setOption(hn_name, json.dumps(src_data), type='hook')
        return True

    def hookInstall(self, info):
        valid_hook = ['backup', 'database']
        valid_list_hook = ['menu', 'global_static', 'site_cb']
        if 'hook' in info:
            hooks = info['hook']
            for h in hooks:
                hooks_type = type(h)
                if hooks_type == dict:
                    tag = h['tag']
                    if tag in valid_list_hook:
                        self.hookInstallOption(tag, h[tag])
                elif hooks_type == str:
                    for x in hooks:
                        if x in valid_hook:
                            self.hookInstallOption(x, info)
                            return True
        return False

    def hookUninstall(self, info):
        valid_hook = ['backup', 'database']
        valid_list_hook = ['menu', 'global_static', 'site_cb']
        if 'hook' in info:
            hooks = info['hook']
            for h in hooks:
                hooks_type = type(h)
                if hooks_type == dict:
                    tag = h['tag']
                    if tag in valid_list_hook:
                        self.hookUninstallOption(tag, h[tag])
                elif hooks_type == str:
                    for x in hooks:
                        if x in valid_hook:
                            self.hookUninstallOption(x, info)
                            return True
        return False

    def install(self, name, version,
        upgrade = None
    ):
        if name.strip() == '':
            return mw.returnData(False, '缺少插件名称!', ())

        if version.strip() == '':
            return mw.returnData(False, '缺少版本信息!', ())

        msg_head = '安装'
        op_cmd = "install"
        if upgrade is not None and upgrade is True:
            msg_head = '更新'
            op_cmd = "upgrade"

        # 防止目录穿越/命令注入
        if not re.fullmatch(r'[A-Za-z0-9_.-]+', name) or '..' in name:
            return mw.returnData(False, '非法的插件名称!', ())

        info_file = self.__plugin_dir + '/' + name + '/' + 'info.json'
        if not os.path.exists(info_file):
            return mw.returnData(False, "配置文件不存在!", ())

        info_data = json.loads(mw.readFile(info_file))

        exec_bash = 'cd {0} && bash {1} {2} {3}'.format(
            mw.quote(mw.getPluginDir() + '/' + name),
            mw.quote(info_data['shell']),
            op_cmd,
            mw.quote(version)
        )

        self.hookInstall(info_data)
        title = '{0}[{1}-{2}]'.format(msg_head,name,version)
        thisdb.addTask(name=title,cmd=exec_bash, status=0)
        mw.triggerTask()
        # 调式日志
        mw.debugLog(exec_bash)
        return mw.returnData(True, '已将安装任务添加到队列!')

    # 卸载插件
    def uninstall(self, name, version):
        if name.strip() == '':
            return mw.returnData(False, "缺少插件名称!", ())

        if version.strip() == '':
            return mw.returnData(False, "缺少版本信息!", ())

        # 防止目录穿越/命令注入
        if not re.fullmatch(r'[A-Za-z0-9_.-]+', name) or '..' in name:
            return mw.returnData(False, '非法的插件名称!', ())

        info_file = self.__plugin_dir + '/' + name + '/' + 'info.json'
        if not os.path.exists(info_file):
            return mw.returnData(False, "配置文件不存在!", ())

        info_data = json.loads(mw.readFile(info_file))

        exec_bash = "cd {0} && /bin/bash {1} uninstall {2}".format(
            mw.quote(mw.getPluginDir() + '/' + name),
            mw.quote(info_data['shell']),
            mw.quote(version)
        )
        self.hookUninstall(info_data)
        data = mw.execShell(exec_bash)
        self.removeIndex(name, version)
        mw.debugLog(exec_bash, data)
        return mw.returnData(True, '卸载执行成功!')

    # 插件搜索匹配
    def searchKey(self, info,
        keyword = None,
    ):
        if keyword == None:
            return True
        try:
            if info['title'].lower().find(keyword) > -1:
                return True
            if info['ps'].lower().find(keyword) > -1:
                return True
            if info['name'].lower().find(keyword) > -1:
                return True
        except Exception as e:
            return False

    def getVersion(self, path):
        version_pl = path + '/version.pl'
        if os.path.exists(version_pl):
            return mw.readFile(version_pl).strip()
        return ''

    def checkIndexList(self, name, version):
        indexList = thisdb.getOptionByJson('display_index',default=[])
        for i in indexList:
            t = i.split('-')
            tlen = len(t)
            plugin_name = t[0]
            plugin_ver = t[1]
            if tlen > 2:
                tArr = t[0:tlen - 1]
                plugin_name = '-'.join(tArr)
                plugin_ver = t[tlen - 1]
            if plugin_name == name:
                return True
        return False

    def checkSetupTask(self, name, version, coexist):
        self.__tasks = thisdb.getTaskRunAll()
        isTask = '1'
        for task in self.__tasks:
            tmpt = mw.getStrBetween('[', ']', task['name'])
            if not tmpt:
                continue
            task_sign = tmpt.split('-')
            task_len = len(task_sign)
            if task_len<2:
                continue

            task_name = task_sign[0].lower()
            task_ver = task_sign[1]
            if task_len > 2:
                nameArr = task_sign[0:task_len - 1]
                task_name = '-'.join(nameArr).lower()
                task_ver = task_sign[task_len - 1]
            if coexist:
                if task_name == name and task_ver == version:
                    isTask = task['status']
            else:
                if task_name == name:
                    isTask = task['status']
        return isTask

    def checkDisplayIndex(self, name, version, coexist):
        indexList = thisdb.getOptionByJson('display_index',default=[])
        if coexist:
            if type(version) == list:
                for index in range(len(version)):
                    vname = name + '-' + version[index]
                    if vname in indexList:
                        return True
            else:
                vname = name + '-' + version
                if vname in indexList:
                    return True
        else:
            if type(version) == list:
                for index in range(len(version)):
                    return self.checkIndexList(name, version)
            else:
                return self.checkIndexList(name, version)
        return False

    def makeCoexist(self, data):
        plugins_info = []
        for index in range(len(data['versions'])):
            data_t = data.copy()
            data_t['title'] = data_t['title'] + '-' + data['versions'][index]
            data_t['versions'] = data['versions'][index]
            pg = self.makePluginInfo(data_t)
            plugins_info.append(pg)

        return plugins_info

    # 构造插件基本信息
    def makePluginInfo(self, info):
        checks = ''
        path = ''
        coexist = False

        if info["checks"].startswith('/'):
            checks = info["checks"]
        else:
            checks = mw.getFatherDir() + '/' + info['checks']

        if 'path' in info:
            path = info['path']

        if not path.startswith('/'):
            path = mw.getFatherDir() + '/' + path

        if 'coexist' in info and info['coexist']:
            coexist = True

        app_upgrade = False
        if 'upgrade' in info and info['upgrade']:
            app_upgrade = True 

        pInfo = {
            "id": 10000,
            "sort": 10000,
            "pid": info['pid'],
            "type": 1000,
            "name": info['name'],
            "title": info['title'],
            "ps": info['ps'],
            "dependnet": "",
            "mutex": "",
            "icon": "",
            "path": path,
            "install_checks": checks,
            "uninsatll_checks": checks,
            "upgrade": app_upgrade,
            "coexist": coexist,
            "versions": info['versions'],
            # "updates": info['updates'],
            "task": True,
            "display": False,
            "setup": False,
            "setup_version": "",
            "status": False,
            "install_pre_inspection": False,
            "uninstall_pre_inspection": False,
        }

        if 'icon' in info:
            pInfo['icon'] = info['icon']

        if 'sort' in info:
            pInfo['sort'] = info['sort']

        if checks.find('VERSION') > -1:
            pInfo['install_checks'] = checks.replace('VERSION', info['versions'])

        if path.find('VERSION') > -1:
            pInfo['path'] = path.replace('VERSION', info['versions'])

        pInfo['task'] = self.checkSetupTask(pInfo['name'], info['versions'], coexist)
        pInfo['display'] = self.checkDisplayIndex(info['name'], pInfo['versions'], coexist)
        pInfo['setup'] = os.path.exists(pInfo['install_checks'])


        if coexist and pInfo['setup']:
            pInfo['setup_version'] = info['versions']
        elif pInfo['setup']:
            if os.path.isdir(pInfo['install_checks']):
                pInfo['setup_version'] = self.getVersion(pInfo['install_checks'])
            else:
                pInfo['setup_version'] = mw.readFile(pInfo['install_checks']).strip()

        if 'install_pre_inspection' in info:
            pInfo['install_pre_inspection'] = info['install_pre_inspection']
        if 'uninstall_pre_inspection' in info:
            pInfo['uninstall_pre_inspection'] = info['uninstall_pre_inspection']

        return pInfo

    def makeCoexistData(self, data):
        plugins = []
        if type(data['versions']) == list and 'coexist' in data and data['coexist']:
            data_t = self.makeCoexist(data)
            for index in range(len(data_t)):
                plugins.append(data_t[index])
        else:
            pg = self.makePluginInfo(data)
            plugins.append(pg)
        return plugins

    def makeCoexistDataInstalled(self, data):
        plugins = []
        if type(data['versions']) == list and 'coexist' in data and data['coexist']:
            data_t = self.makeCoexist(data)
            for index in range(len(data_t)):
                if data_t[index]['setup']:
                    plugins.append(data_t[index])
        else:
            pg = self.makePluginInfo(data)
            if pg['setup']:
                plugins.append(pg)
        return plugins

    # 对多版本共存进行处理
    def makeCoexistList(self, data,
        plugin_type = None,
    ):
        plugins_t = []
        # 返回指定类型
        if plugin_type != None and data.get('pid') == plugin_type:
            return self.makeCoexistData(data)

        # 全部
        if plugin_type == None or plugin_type == '0':
            return self.makeCoexistData(data)
        # 已经安装
        if str(plugin_type) == '-1':
            return self.makeCoexistDataInstalled(data)
        return plugins_t

    # info.json 必填字段, 缺失会导致插件列表接口直接报错
    __plugin_required_fields = ('name', 'title', 'ps', 'versions', 'checks')

    def checkPluginInfo(self, name):
        """读取并校验插件 info.json, 返回 (data, error); 校验失败时 data 为 {}"""
        info_path = self.__plugin_dir + '/' + name + '/info.json'
        if not os.path.exists(info_path):
            return {}, '缺少 info.json'

        try:
            content = mw.readFile(info_path)
            data = json.loads(content)
        except Exception as e:
            return {}, 'info.json 解析失败: %s' % str(e)

        if not isinstance(data, dict):
            return {}, 'info.json 内容必须是 JSON 对象'

        missing_fields = [field for field in self.__plugin_required_fields if field not in data]
        if missing_fields:
            return {}, '缺少必填字段: %s' % ', '.join(missing_fields)

        if not isinstance(data['versions'], (str, list)):
            return {}, 'versions 必须为字符串或数组'
        if not isinstance(data['checks'], str) or data['checks'] == '':
            return {}, 'checks 必须为非空字符串'

        # 旧插件未声明分类时归入“其他插件”
        data.setdefault('pid', '5')
        return data, None

    def getPluginInfo(self, name):
        data, error = self.checkPluginInfo(name)
        if error:
            print('getPluginInfo: %s %s' % (name, error))
        return data

    def getPluginInfoErrors(self):
        """返回所有 info.json 不完整的插件, 供页面提示"""
        errors = []
        if not os.path.isdir(self.__plugin_dir):
            return errors
        for name in sorted(os.listdir(self.__plugin_dir)):
            if name.startswith('.'):
                continue
            if not os.path.isdir(self.__plugin_dir + '/' + name):
                continue
            data, error = self.checkPluginInfo(name)
            if error:
                errors.append({'name': name, 'error': error})
        return errors

    def getPluginList(self, name,
        keyword = None,
        type = None,
    ):
        infos = []
        data = self.getPluginInfo(name)
        if data is None or len(data) == 0:
            return infos
        
        # 判断是否搜索
        if keyword != '' and not self.searchKey(data, keyword):
            return infos

        plugin_t = self.makeCoexistList(data, type)
        for index in range(len(plugin_t)):
            infos.append(plugin_t[index])
        return infos

    # 检查插件状态
    def checkStatusThreads(self, info, i):
        if not info['setup']:
            return False
        data = self.run(info['name'], 'status', info['setup_version'])
        if data[0].strip() == 'start':
            return True
        else:
            return False

    # 检查插件状态
    def checkStatusThreadsByCache(self, info, i):
        # 初始化db
        if not info['setup']:
            return False

        plugin_list_status = self.__plugin_status_data
        if plugin_list_status is not None:
            k = info['name']
            if 'coexist' in info and info['coexist']:
                k = info['title']
            # print(k)
            if k in plugin_list_status:
                if plugin_list_status[k]:
                    return True
                else: 
                    return False

        data = self.run(info['name'], 'status', info['setup_version'])
        if data[0].strip() == 'start':
            return True
        else:
            return False

    # 多线程检查插件状态[cache]
    def checkStatusMThreadsByCache(self, info):
        try:
            self.__plugin_status_data = thisdb.getOptionByJson(self.__plugin_status_cachekey, default=None)
            threads = []
            ntmp_list = range(len(info))
            for i in ntmp_list:
                t = pg_thread(self.checkStatusThreadsByCache,(info[i], i))
                threads.append(t)

            for i in ntmp_list:
                threads[i].start()
            for i in ntmp_list:
                threads[i].join()

            for i in ntmp_list:
                t = threads[i].getResult()
                k = info[i]['name']
                self.__plugin_status_data[k] = t
                info[i]['status'] = t

            thisdb.setOption(self.__plugin_status_cachekey, json.dumps(self.__plugin_status_data))
        except Exception as e:
            print(mw.getTracebackInfo())
            print('checkStatusMThreadsByCache:', str(e))
        return info

    def autoCachePluginStatus(self):
        info = []
        for name in os.listdir(self.__plugin_dir):
            if name.startswith('.'):
                continue
            t = self.getPluginList(name)
            for index in range(len(t)):
                info.append(t[index])

        self.__plugin_status_data = {}
        for x in info:
            if not x['setup']:
                continue
            data = self.run(x['name'], 'status', x['setup_version'])
            k = x['name']
            if 'coexist' in x and x['coexist']:
                k = x['title']
            if data[0].strip() == 'start':
                self.__plugin_status_data[k] = True
            else:
                self.__plugin_status_data[k] = False
        # print(self.__plugin_status_data)
        # mw.writeFileLog(json.dumps(self.__plugin_status_data))
        thisdb.setOption(self.__plugin_status_cachekey, json.dumps(self.__plugin_status_data))
        # print(thisdb.getOption(self.__plugin_status_cachekey))
        return True

    # 多线程检查插件状态
    def checkStatusMThreads(self, info):
        try:
            threads = []
            ntmp_list = range(len(info))
            for i in ntmp_list:
                t = pg_thread(self.checkStatusThreads,(info[i], i))
                threads.append(t)

            for i in ntmp_list:
                threads[i].start()
            for i in ntmp_list:
                threads[i].join()

            for i in ntmp_list:
                t = threads[i].getResult()
                info[i]['status'] = t
        except Exception as e:
            print('checkStatusMThreads:', str(e))

        return info

    def getAllPluginList(
        self,
        type = None,
        keyword = None,
        page = 1, 
        size = 10, 
    ):
        info = []
        for name in os.listdir(self.__plugin_dir):
            if name.startswith('.'):
                continue
            t = self.getPluginList(name, keyword, type=type)
            for index in range(len(t)):
                info.append(t[index])

        info = sorted(info, key=lambda f: int(f['sort']), reverse=False)
        
        start = (page - 1) * size
        end = start + size
        x = info[start:end]

        x = self.checkStatusMThreadsByCache(x)
        return (x, len(info))

    def getList(
        self,
        type = None,
        keyword = None,
        page = 1, 
        size  = 10, 
    ) -> object:
        '''
        # print(type,keyword,page,size)
        '''
        rdata = {}
        rdata['type'] = self.def_plugin_type
        rdata['info_errors'] = self.getPluginInfoErrors()
    
        data = self.getAllPluginList(type, keyword, page, size)
        rdata['data'] = data[0]
        rdata['list'] = mw.getPage({'count':data[1],'p':page,'tojs':'getSList','row':size})
        return rdata

    def updateZip(self, request_zip):
        tmp_path = mw.getPanelDir() + '/temp'
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        mw.execShell("rm -rf " + tmp_path + '/*')

        tmp_file = tmp_path + '/plugin_tmp.zip'
        if request_zip.filename[-4:] != '.zip':
            return mw.returnData(False, '仅支持zip文件!')

        request_zip.save(tmp_file)
        mw.execShell('cd ' + tmp_path + ' && unzip ' + tmp_file)
        os.remove(tmp_file)

        p_info = tmp_path + '/info.json'
        if not os.path.exists(p_info):
            d_path = None
            for df in os.walk(tmp_path):
                if len(df[2]) < 3:
                    continue
                if not 'info.json' in df[2]:
                    continue
                if not 'install.sh' in df[2]:
                    continue
                if not os.path.exists(df[0] + '/info.json'):
                    continue
                d_path = df[0]
            if d_path:
                tmp_path = d_path
                p_info = tmp_path + '/info.json'
        try:
            data = json.loads(mw.readFile(p_info))
            data['size'] = mw.getPathSize(tmp_path)
            if not 'author' in data:
                data['author'] = '未知'
            if not 'home' in data:
                data['home'] = 'https://github.com/midoks/mdserver-web'
            plugin_path = mw.getPluginDir() + data['name'] + '/info.json'
            data['old_version'] = '0'
            data['tmp_path'] = tmp_path
            if os.path.exists(plugin_path):
                try:
                    old_info = json.loads(mw.readFile(plugin_path))
                    data['old_version'] = old_info['versions']
                except:
                    pass
        except:
            mw.execShell("rm -rf " + tmp_path)
            return mw.returnData(False, '在压缩包中没有找到插件信息,请检查插件包!')
        protectPlist = ('openresty', 'mysql', 'php', 'redis', 'memcached'
                        'mongodb', 'swap', 'gogs', 'pureftp')
        if data['name'] in protectPlist:
            return mw.returnData(False, '[' + data['name'] + '],重要插件不可修改!')
        return data

    def inputZipApi(self, plugin_name,tmp_path):
        # 防止目录穿越与命令注入: 插件名只允许安全字符, 临时目录必须位于面板 temp 下
        if not re.fullmatch(r'[A-Za-z0-9_.-]+', plugin_name or '') or '..' in plugin_name:
            return mw.returnData(False, '非法的插件名称!')
        temp_dir = os.path.realpath(mw.getPanelDir() + '/temp')
        tmp_path = os.path.realpath(tmp_path or '')
        if not (tmp_path == temp_dir or tmp_path.startswith(temp_dir + os.sep)):
            return mw.returnData(False, '非法的临时目录!')
        if not os.path.exists(tmp_path):
            return mw.returnData(False, '临时文件不存在,请重新上传!')
        plugin_path = mw.getPluginDir() + '/' + plugin_name
        if not os.path.exists(plugin_path):
            print(mw.execShell('mkdir -p ' + mw.quote(plugin_path)))
        mw.execShell("cp -rf " + mw.quote(tmp_path) + '/* ' + mw.quote(plugin_path) + '/')
        mw.execShell('chmod -R 755 ' + mw.quote(plugin_path))
        p_info = mw.readFile(plugin_path + '/info.json')
        if p_info:
            mw.writeLog('软件管理', '安装第三方插件[%s]' %json.loads(p_info)['title'])
            return mw.returnData(True, '安装成功!')
        mw.execShell("rm -rf " + mw.quote(plugin_path))
        return mw.returnData(False, '安装失败!')

    # [start|stop]操作,删除缓存!
    def runByCache(self, name, func, version):
        ppos = mw.getServerDir()+'/'+name
        if not os.path.exists(ppos):
            return
        data = thisdb.getOptionByJson(self.__plugin_status_cachekey, default={})
        info = self.getPluginInfo(name)
        if 'coexist' in info and info['coexist']:
            name = info['title'] + '-'+ version
        if name in data:
            del(data[name])
            thisdb.setOption(self.__plugin_status_cachekey, json.dumps(data))

    # shell/bash方式调用
    def run(self, name, func,
        version = '',
        args  = '',
        script  = 'index',
    ):
        # 防止目录穿越与命令注入: 插件名/脚本名只允许安全字符
        if not re.fullmatch(r'[A-Za-z0-9_.-]+', name or '') or '..' in name:
            return ('', '非法的插件名称!')
        if not re.fullmatch(r'[A-Za-z0-9_.-]+', script or '') or '..' in script:
            return ('', '非法的脚本名称!')
        if not re.fullmatch(r'[A-Za-z0-9_.-]+', func or ''):
            return ('', '非法的函数名称!')
        if version != '' and not re.fullmatch(r'[A-Za-z0-9_.:-]+', version):
            return ('', '非法的版本参数!')

        if mw.inArray(['start','stop','restart','reload','uninstall_pre_inspection','install','uninstall'], func):
            self.runByCache(name, func, version)

        path = self.__plugin_dir + '/' + name + '/' + script + '.py'
        if not os.path.exists(path):
            path = self.__plugin_dir + '/' + name + '/' + name + '.py'

        if not os.path.exists(path):
            return ('', '')

        # 使用参数列表直接调用, 不经过 shell, 避免 func/version/args 被解释执行
        panel_dir = mw.getPanelDir()
        python_bin = 'python3'
        if os.path.exists(panel_dir + "/bin/python3"):
            python_bin = panel_dir + "/bin/python3"
        elif os.path.exists(panel_dir + "/bin/python"):
            python_bin = panel_dir + "/bin/python"

        cmd = [python_bin, path, func]
        if version != '':
            cmd.append(version)
        if args != '':
            # 插件的老式 getArgs() 只认 'key:value' argv 列表, 不认整个 JSON 字符串
            # 把 JSON dict 拆成 key:value 列表, 让插件无需修改即可继续工作
            parsed_args = None
            try:
                obj = json.loads(args)
                if isinstance(obj, dict):
                    # parsed_args = ['%s:%s' % (k, v) for k, v in obj.items()]
                    post_args = []
                    for k, v in obj.items():
                        arg_item = '%s:%s' % (k, v)
                        if not re.fullmatch(r'[A-Za-z0-9_.:/@=,+-]+', arg_item):
                            return ('', '非法的参数内容!')
                        post_args.append(arg_item)
                    parsed_args = post_args
            except (ValueError, TypeError):
                pass
            if parsed_args is not None:
                cmd.extend(parsed_args)
            else:
                # 非 JSON 字符串(老格式或简单字符串)原样传
                if not re.fullmatch(r'[A-Za-z0-9_.:/@=,+-]+', args):
                    return ('', '非法的参数内容!')
                cmd.append(args)

        env = os.environ.copy()
        if os.path.exists(panel_dir + "/bin/activate"):
            env['VIRTUAL_ENV'] = panel_dir
            env['PATH'] = panel_dir + "/bin:" + env.get('PATH', '')

        try:
            p = subprocess.Popen(cmd, cwd=panel_dir,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 env=env)
            stdout, stderr = p.communicate()
            data = (stdout.decode('utf-8', 'ignore'),
                    stderr.decode('utf-8', 'ignore'))
        except Exception as e:
            data = ('', str(e))

        # print(data)
        if mw.isDebugMode():
            print('run:', ' '.join(cmd))
            print('return:',data)
        # print os.path.exists(py_cmd)
        return (data[0].strip(), data[1].strip())

    # 映射包调用
    def callback(self, name, func,
        args = '',
        script = 'index',
    ):
        package = self.__plugin_dir + '/' + name
        if not os.path.exists(package):
            return (False, "插件不存在!")

        # 各插件脚本同名(如 index.py),目标插件目录需置于 sys.path 最前
        if package in sys.path:
            sys.path.remove(package)
        sys.path.insert(0, package)

        # 清除其他插件的同名模块缓存,避免 __import__ 命中错误模块
        if script in sys.modules:
            mod_file = getattr(sys.modules[script], '__file__', '') or ''
            if not mod_file.startswith(package):
                del sys.modules[script]

        cmd = "__import__('" + script + "')." + func + '(' + args + ')'
        if mw.isDebugMode():
            print('callback:', cmd)

        data = None
        try:
            data = eval(cmd)
        except Exception as e:
            print(mw.getTracebackInfo())
            return (False, mw.getTracebackInfo())        
        return (True, data)



        