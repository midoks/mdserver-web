# coding:utf-8

import sys
import io
import os
import time
import re

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
    args = sys.argv[3:]
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


# 登陆验证
def dockerLoginCheck(user_name, user_pass, registry):
    login_test = mw.execShell('docker login -u=%s -p %s %s' %
                              (user_name, user_pass, registry))
    ret = 'required$|Error'
    ret2 = re.findall(ret, login_test[-1])
    if len(ret2) == 0:
        return True
    else:
        return False


def imageListData():
    try:
        ilist = imageList()
    except Exception as e:
        return mw.returnJson(False, '未开启Docker')
    return mw.returnJson(True, 'ok', ilist)


def runLog():
    return getServerDir() + '/data/redis.log'


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
    elif func == 'run_log':
        print(runLog())
    elif func == 'con_list':
        print(conListData())
    elif func == 'image_list':
        print(imageListData())
    else:
        print('error')
