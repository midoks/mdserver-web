# coding:utf-8

import sys
import io
import os
import time
import re
import json

sys.path.append(os.getcwd() + "/class/core")
import mw

import docker


app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getDClient():
    try:
        client = docker.from_env()
    except Exception as e:
        client = docker.DockerClient(
            base_url='unix:///Users/midoks/.docker/run/docker.sock')
    return client


def getPluginName():
    return 'docker'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getConf():
    path = getServerDir() + "/redis.conf"
    return path


def getConfTpl():
    path = getPluginDir() + "/config/redis.conf"
    return path


def getInitDTpl():
    path = getPluginDir() + "/init.d/" + getPluginName() + ".tpl"
    return path


def getArgs():
    args = sys.argv[2:]
    tmp = {}
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
            t = args[i].split(':', 1)
            tmp[t[0]] = t[1]
    return tmp


def checkArgs(self, data, ck=[]):
    for i in range(len(ck)):
        print(data[i])
        if not ck[i] in data:
            return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, mw.returnJson(True, 'ok'))


def status():
    data = mw.execShell(
        "ps -ef|grep docker |grep -v grep | grep -v python | grep -v mdserver-web | awk '{print $2}'")

    if data[0] == '':
        return 'stop'
    return 'start'


def initDreplace():
    return ''


def dockerOp(method):
    file = initDreplace()

    if not mw.isAppleSystem():
        data = mw.execShell('systemctl ' + method + ' docker')
        if data[1] == '':
            return 'ok'
        return data[1]
    return 'fail'


def start():
    return dockerOp('start')


def stop():
    return dockerOp('stop')


def restart():
    status = dockerOp('restart')

    log_file = runLog()
    mw.execShell("echo '' > " + log_file)
    return status


def reload():
    return dockerOp('reload')


def initdStatus():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    shell_cmd = 'systemctl status ' + \
        getPluginName() + ' | grep loaded | grep "enabled;"'
    data = mw.execShell(shell_cmd)
    if data[0] == '':
        return 'fail'
    return 'ok'


def initdInstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl enable ' + getPluginName())
    return 'ok'


def initdUinstall():
    if mw.isAppleSystem():
        return "Apple Computer does not support"

    mw.execShell('systemctl disable ' + getPluginName())
    return 'ok'

# UTC时间转换为时间戳


def utc_to_local(utc_time_str, utc_format='%Y-%m-%dT%H:%M:%S'):
    import pytz
    import datetime
    import time
    local_tz = pytz.timezone('Asia/Chongqing')
    local_format = "%Y-%m-%d %H:%M"
    utc_dt = datetime.datetime.strptime(utc_time_str, utc_format)
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    time_str = local_dt.strftime(local_format)
    return int(time.mktime(time.strptime(time_str, local_format)))


def conList():
    c = getDClient()
    clist = c.containers.list(all=True)
    conList = []
    for con in clist:
        tmp = con.attrs
        tmp['Created'] = utc_to_local(tmp['Created'].split('.')[0])
        conList.append(tmp)
    return conList


def conListData():
    try:
        clist = conList()
    except Exception as e:
        return mw.returnJson(False, '未开启Docker')
    return mw.returnJson(True, 'ok', clist)


def dockerRemoveCon():
    args = getArgs()
    data = checkArgs(args, ['Hostname'])
    if not data[0]:
        return data[1]

    Hostname = args['Hostname']

    c = getDClient()
    try:
        conFind = c.containers.get(Hostname)
        try:
            path_list = conFind.attrs['GraphDriver'][
                'Data']['LowerDir'].split(':')
            for i in path_list:
                mw.execShell('chattr -R -i %s' % i)
        except:
            pass
        conFind.remove(force=True)
        return mw.returnJson(True, '成功删除!')
    except docker.errors.APIError as ex:
        return mw.returnJson(False, '删除失败!' + str(ex))


def dockerLogCon():

    args = getArgs()
    data = checkArgs(args, ['Hostname'])
    if not data[0]:
        return data[1]

    Hostname = args['Hostname']

    c = getDClient()
    try:
        conFind = c.containers.get(Hostname)
        if not conFind:
            return mw.returnJson(False, 'The specified container does not exist!')
        log = conFind.logs()
        if not isinstance(log, str):
            log = log.decode()
        return mw.returnJson(True, log)
    except docker.errors.APIError as ex:
        return mw.returnJson(False, 'Get Logs failed')


def dockerRunCon():
    # 启动容器
    args = getArgs()
    data = checkArgs(args, ['Hostname'])
    if not data[0]:
        return data[1]

    Hostname = args['Hostname']
    c = getDClient()
    try:
        conFind = c.containers.get(Hostname)
        if not conFind:
            return mw.returnJson(False, 'The specified container does not exist!')
        conFind.start()
        return mw.returnJson(True, '启动成功!')
    except docker.errors.APIError as ex:
        return mw.returnJson(False, '启动失败!' + str(ex))


def dockerStopCon():
    # 停止容器
    args = getArgs()
    data = checkArgs(args, ['Hostname'])
    if not data[0]:
        return data[1]

    Hostname = args['Hostname']
    c = getDClient()
    try:
        conFind = c.containers.get(Hostname)
        if not conFind:
            return mw.returnJson(False, 'The specified container does not exist!')
        conFind.stop()
        return mw.returnJson(True, '停止成功!')
    except docker.errors.APIError as ex:
        return mw.returnJson(False, '停止失败!' + str(ex))


def dockerExec():
    # 容器执行命令
    args = getArgs()
    data = checkArgs(args, ['Hostname'])
    if not data[0]:
        return data[1]

    Hostname = args['Hostname']

    debug_path = 'data/debug.pl'
    if os.path.exists(debug_path):
        return mw.returnJson(False, '开发模式不能进入!')

    c = getDClient()
    try:
        conFind = c.containers.get(Hostname)
        cmd = 'docker container exec -it %s /bin/sh' % Hostname
        return mw.returnJson(True, cmd)
    except docker.errors.APIError as ex:
        return mw.returnJson(False, '连接失败!')


def imageList():
    imageList = []
    c = getDClient()
    ilist = c.images.list()
    for image in ilist:
        tmp_attrs = image.attrs
        if len(tmp_attrs['RepoTags']) == 1:
            tmp_image = {}
            tmp_image['Id'] = tmp_attrs['Id'].split(':')[1][:12]
            tmp_image['RepoTags'] = tmp_attrs['RepoTags'][0]
            tmp_image['Size'] = tmp_attrs['Size']
            tmp_image['Labels'] = tmp_attrs['Config']['Labels']
            tmp_image['Comment'] = tmp_attrs['Comment']
            tmp_image['Created'] = utc_to_local(
                tmp_attrs['Created'].split('.')[0])
            imageList.append(tmp_image)
        else:
            for i in range(len(tmp_attrs['RepoTags'])):
                tmp_image = {}
                tmp_image['Id'] = tmp_attrs['Id'].split(':')[1][:12]
                tmp_image['RepoTags'] = tmp_attrs['RepoTags'][i]
                tmp_image['Size'] = tmp_attrs['Size']
                tmp_image['Labels'] = tmp_attrs['Config']['Labels']
                tmp_image['Comment'] = tmp_attrs['Comment']
                tmp_image['Created'] = utc_to_local(
                    tmp_attrs['Created'].split('.')[0])
                imageList.append(tmp_image)
    imageList = sorted(imageList, key=lambda x: x['Created'], reverse=True)
    return imageList


def dockerPull():
    # pull Dockr 官方镜像
    args = getArgs()
    data = checkArgs(args, ['images'])
    if not data[0]:
        return data[1]

    images = args['images']
    if ':' in images:
        pass
    else:
        images = images + ':latest'

    c = getDClient()
    try:
        ret = c.images.pull(images)
        if ret:
            return mw.returnJson(True, '拉取成功！')
        else:
            return mw.returnJson(False, '拉取失败，请检查镜像名称或是否需要登录docker进行下载')
    except:
        ret = mw.execShell('docker image pull %s' % images)
        if 'invalid' in ret[-1]:
            return mw.returnJson(False, '拉取失败，请检查镜像名称或是否需要登录docker进行下载')
        else:
            return mw.returnJson(True, '拉取成功！')


def dockerPlulPath(path):
    if not path and path == '':
        return mw.returnJson(False, 'Invalid address')

    ret = mw.execShell('docker image pull %s' % path)
    if 'invalid' in ret[-1]:
        return mw.returnJson(False, '拉取失败，请检查镜像名称或是否需要登录docker进行下载')
    else:
        return mw.returnJson(True, '拉取成功！')


def dockerPullReg():
    # pull Dockr 官方镜像
    args = getArgs()
    data = checkArgs(args, ['path'])
    if not data[0]:
        return data[1]

    path = args['path']
    return dockerPlulPath(path)


# 判断镜像是否存在
def checkImage(path):
    image_list = imageList()
    for i in image_list:
        if path == i["RepoTags"]:
            return mw.returnData(False, '镜像已存在!')


def dockerPullPrivateNew():
    # pull Dockr 官方镜像
    args = getArgs()
    data = checkArgs(args, ['path'])
    if not data[0]:
        return data[1]

    path = args['path']
    check = checkImage(path)
    if check:
        return mw.getJson(check)

    my_repo = repoList()
    if not my_repo:
        return mw.returnJson(False, '未登录任何私人存储库，请登录然后拉取')
    return dockerPlulPath(path)


def imageListData():
    try:
        ilist = imageList()
    except Exception as e:
        return mw.returnJson(False, '未开启Docker')
    return mw.returnJson(True, 'ok', ilist)


def dockerRemoveImage():
    args = getArgs()
    data = checkArgs(args, ['imageId', 'repoTags'])
    if not data[0]:
        return data[1]

    repoTags = args['repoTags']
    imageId = args['imageId']

    c = getDClient()
    try:
        c.images.remove(repoTags)
        return mw.returnJson(True, '成功删除')
    except:
        try:
            c.images.remove(imageId)
            return mw.returnJson(True, '成功删除!')
        except docker.errors.APIError as ex:
            return mw.returnJson(False, '删除失败, 当前镜像正在使用!')


def getImageListFunc(dbname=''):
    bkDir = mw.getRootDir() + '/backup/docker'
    blist = os.listdir(bkDir)
    r = []

    bname = 'db_' + dbname
    blen = len(bname)
    for x in blist:
        fbstr = x[0:blen]
        if fbstr == bname:
            r.append(x)
    return r


def dockerImagePickDir():
    bkDir = mw.getRootDir() + '/backup/docker'
    return mw.returnJson(True, 'ok', bkDir)


def dockerImagePickList():

    bkDir = mw.getRootDir() + '/backup/docker'
    if not os.path.exists(bkDir):
        os.mkdir(bkDir)

    r = os.listdir(bkDir)
    rr = []
    for x in range(0, len(r)):
        p = bkDir + '/' + r[x]
        data = {}
        data['name'] = r[x]

        rsize = os.path.getsize(p)
        data['size'] = mw.toSize(rsize)

        t = os.path.getctime(p)
        t = time.localtime(t)

        data['time'] = time.strftime('%Y-%m-%d %H:%M:%S', t)
        rr.append(data)

        data['file'] = p

    return mw.returnJson(True, 'ok', rr)


def dockerImagePickSave():
    # image 导出
    args = getArgs()
    data = checkArgs(args, ['images'])
    if not data[0]:
        return data[1]

    bkDir = mw.getRootDir() + '/backup/docker/'
    images = args['images']
    try:
        file_name = bkDir + \
            str(time.strftime('%Y%m%d_%H%M%S', time.localtime())) + '.tar.gz'
        mw.execShell('docker image save %s | gzip > %s' %
                     (images, file_name))
        return mw.returnJson(True, '导出镜像 {} 成功!'.format(file_name))
    except docker.errors.APIError as ex:
        return mw.returnJson(False, '操作失败: ' + str(ex))


def dockerImagePickLoad():
    # 镜像文件导入
    args = getArgs()
    data = checkArgs(args, ['file'])
    if not data[0]:
        return data[1]
    try:
        file_path = args['file']
        if not os.path.exists(file_path):
            return mw.returnJson(False, '文件不存在')
        if file_path.endswith('.tar'):
            mw.execShell('docker image load < %s' % file_path)
        elif file_path.endswith('.tar.gz'):
            mw.execShell('gunzip -c %s | docker image load' % file_path)
        else:
            return mw.returnJson(False, '不支持改文件类型!')
        return mw.returnJson(True, '导入镜像文件成功!')
    except docker.errors.APIError as ex:
        return mw.returnJson(False, '操作失败: ' + str(ex))


def dockerLoginCheck(user_name, user_pass, registry):
    # 登陆验证
    cmd = 'docker login -u=%s -p %s %s' % (user_name, user_pass, registry)
    # print(cmd)
    login_test = mw.execShell(cmd)
    # print(login_test)
    ret = 'required$|Error'
    ret2 = re.findall(ret, login_test[-1])
    if len(ret2) == 0:
        return True
    else:
        return False


def getDockerIpListData():
    # 取IP列表
    path = getServerDir()
    ipConf = path + '/iplist.json'
    if not os.path.exists(ipConf):
        return []
    iplist = json.loads(mw.readFile(ipConf))
    return iplist


def getDockerIpList():
    data = getDockerIpListData()
    return mw.returnJson(True, 'ok!', data)


def dockerAddIP():
    # 添加IP
    args = getArgs()
    data = checkArgs(args, ['address', 'netmask', 'gateway'])
    if not data[0]:
        return data[1]

    path = getServerDir()
    ipConf = path + '/iplist.json'
    if not os.path.exists(ipConf):
        iplist = []
        mw.writeFile(ipConf, json.dumps(iplist))

    iplist = json.loads(mw.readFile(ipConf))
    ipInfo = {
        'address': args['address'],
        'netmask': args['netmask'],
        'gateway': args['gateway'],
    }
    iplist.append(ipInfo)
    mw.writeFile(ipConf, json.dumps(iplist))
    return mw.returnJson(True, '添加成功!')


def dockerDelIP():
    # 删除IP
    args = getArgs()
    data = checkArgs(args, ['address'])
    if not data[0]:
        return data[1]

    path = getServerDir()
    ipConf = path + '/iplist.json'
    if not os.path.exists(ipConf):
        return mw.returnJson(False, '指定的IP不存在。！')
    iplist = json.loads(mw.readFile(ipConf))
    newList = []
    for ipInfo in iplist:
        if ipInfo['address'] == args['address']:
            continue
        newList.append(ipInfo)
    mw.writeFile(ipConf, json.dumps(newList))
    return mw.returnJson(True, '成功删除!')


def getDockerCreateInfo():
    # 取创建依赖
    import psutil
    data = {}
    data['images'] = imageList()
    data['memSize'] = int(psutil.virtual_memory().total / 1024 / 1024)
    data['iplist'] = getDockerIpListData()
    return mw.returnJson(True, 'ok!', data)


def __release_port(port):
    from collections import namedtuple
    try:
        import firewall_api
        firewall_api.firewall_api().addAcceptPortArgs(port, 'docker', 'port')
        return port
    except Exception as e:
        return "Release failed {}".format(e)


def dockerPortCheck():
    args = getArgs()
    data = checkArgs(args, ['port'])
    if not data[0]:
        return data[1]

    port = args['port']
    is_ok = IsPortExists(port)
    if is_ok:
        return mw.returnJson(True, 'ok')
    return mw.returnJson(False, 'fail')


def IsPortExists(port):
    # 判断端口是否被占用
    ret = __check_dst_port(ip='localhost', port=port)
    ret2 = __check_dst_port(ip='0.0.0.0', port=port)
    if ret:
        return ret
    if not ret and ret2:
        return ret2
    if not ret and not ret2:
        return False


def __check_dst_port(ip, port, timeout=3):
    # 端口检测
    import socket
    ok = True
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((ip, port))
        s.close()
    except:
        ok = False
    return ok


def dockerCreateCon():
    args = getArgs()
    data = checkArgs(args, ['environments', 'command',
                            'entrypoint', 'image', 'mem_limit', 'ports', 'volumes'])
    if not data[0]:
        return data[1]

    environments = args['environments']
    environments = environments.strip().split()

    command = args['command']
    entrypoint = args['entrypoint']
    image = args['image']
    mem_limit = args['mem_limit']
    ports = args['ports']
    ports = ports.replace('[', '(').replace(']', ')')
    volumes = args['volumes']

    # if __name__ == "__main__":
    #     print(args)
    try:

        c = getDClient()
        conObject = c.containers.run(
            image=image,
            mem_limit=mem_limit + 'M',
            ports=eval(ports),
            auto_remove=False,
            command=command,
            detach=True,
            stdin_open=True,
            tty=True,
            entrypoint=entrypoint,
            privileged=True,
            volumes=json.loads(volumes),
            cpu_shares=10,
            environment=environments
        )
        if conObject:
            __release_port(ports)
            return mw.returnJson(True, '创建成功!')

        return mw.returnJson(False, '创建失败!')
    except docker.errors.APIError as ex:
        return mw.returnJson(False, '创建失败!' + str(ex))


def dockerLogin():
    args = getArgs()

    # print(args)
    data = checkArgs(args, ['user', 'passwd', 'hub_name',
                            'namespace', 'registry', 'repository_name'])
    if not data[0]:
        return data[1]

    user_name = args['user']
    user_pass = args['passwd']
    registry = args['registry']
    hub_name = args['hub_name']
    namespace = args['namespace']
    repository_name = args['repository_name']

    ret_status = dockerLoginCheck(user_name, user_pass, registry)
    path = getServerDir()
    if ret_status:
        user_file = path + '/user.json'
        user_info = mw.readFile(user_file)
        if not user_info:
            user_info = []
        else:
            user_info = json.loads(user_info)

        ret = {}
        ret['user_name'] = user_name
        ret['user_pass'] = user_pass
        ret['registry'] = registry
        ret['hub_name'] = hub_name
        ret['namespace'] = namespace
        ret['repository_name'] = repository_name
        if not registry:
            ret['registry'] = "docker.io"
        user_info.append(ret)
        mw.writeFile(user_file, json.dumps(user_info))
        return mw.returnJson(True, '成功登录!')
    return mw.returnJson(False, '登录失败!')


# 删除用户信息
def delete_user_info(registry):
    path = getServerDir()
    user_file = path + '/user.json'
    user_info = mw.readFile(user_file)
    if user_info:
        user_info = json.loads(user_info)
        for i in range(len(user_info)):
            if registry in user_info[i].values():
                del(user_info[i])
                mw.writeFile(user_file, json.dumps(user_info))
                return True


def dockerLogout():
    args = getArgs()
    data = checkArgs(args, ['registry'])
    if not data[0]:
        return data[1]

    registry = args['registry']
    if registry == "docker.io":
        registry = ""
        login_test = mw.execShell('docker logout %s' % registry)
        if registry == "":
            registry = "docker.io"
        ret = 'required$|Error'
        ret2 = re.findall(ret, login_test[-1])
        delete_user_info(registry)
        if len(ret2) == 0:
            return mw.returnJson(True, '退出成功')
        else:
            return mw.returnJson(True, '退出失败')


def repoList():
    path = getServerDir()
    repostory_info = []
    user_file = path + '/user.json'

    if os.path.exists(user_file):
        user_info = mw.readFile(user_file)
        user_info = json.loads(user_info)
        for i in user_info:
            tmp = {}
            tmp["hub_name"] = i["hub_name"]
            tmp["registry"] = i["registry"]
            tmp["namespace"] = i["namespace"]
            tmp['repository_name'] = i["repository_name"]
            repostory_info.append(tmp)

    return mw.returnJson(True, 'ok', repostory_info)


if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print(status())
    elif func == 'start':
        print(start())
    elif func == 'stop':
        print(stop())
    elif func == 'restart':
        print(restart())
    elif func == 'reload':
        print(reload())
    elif func == 'initd_status':
        print(initdStatus())
    elif func == 'initd_install':
        print(initdInstall())
    elif func == 'initd_uninstall':
        print(initdUinstall())
    elif func == 'conf':
        print(getConf())
    elif func == 'con_list':
        print(conListData())
    elif func == 'docker_con_log':
        print(dockerLogCon())
    elif func == 'docker_remove_con':
        print(dockerRemoveCon())
    elif func == 'docker_run_con':
        print(dockerRunCon())
    elif func == 'docker_stop_con':
        print(dockerStopCon())
    elif func == 'docker_exec':
        print(dockerExec())
    elif func == 'docker_pull':
        print(dockerPull())
    elif func == 'docker_pull_reg':
        print(dockerPullReg())
    elif func == 'image_list':
        print(imageListData())
    elif func == 'image_pick_dir':
        print(dockerImagePickDir())
    elif func == 'image_pick_save':
        print(dockerImagePickSave())
    elif func == 'image_pick_load':
        print(dockerImagePickLoad())
    elif func == 'image_pick_list':
        print(dockerImagePickList())
    elif func == 'docker_get_iplist':
        print(getDockerIpList())
    elif func == 'docker_del_ip':
        print(dockerDelIP())
    elif func == 'docker_add_ip':
        print(dockerAddIP())
    elif func == 'get_docker_create_info':
        print(getDockerCreateInfo())
    elif func == 'docker_create_con':
        print(dockerCreateCon())
    elif func == 'docker_remove_image':
        print(dockerRemoveImage())
    elif func == 'docker_port_check':
        print(dockerPortCheck())
    elif func == 'docker_login':
        print(dockerLogin())
    elif func == 'docker_logout':
        print(dockerLogout())
    elif func == 'repo_list':
        print(repoList())
    else:
        print('error')
