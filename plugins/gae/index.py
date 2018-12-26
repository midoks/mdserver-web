# coding: utf-8

import time
import random
import os
import json
import re
import sys

sys.path.append(os.getcwd() + "/class/core")
import public


def getPluginName():
    return 'gae'


def getPluginDir():
    return public.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return public.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getArgs():
    args = sys.argv[2:]
    tmp = {}
    args_len = len(args)

    if args_len == 1:
        t = args[0].strip('{').strip('}')
        t = t.split(':')
        tmp[t[0]] = t[1]
    elif args_len > 1:
        for i in range(len(args)):
            t = args[i].split(':')
            tmp[t[0]] = t[1]

    return tmp


def status():
    return 'start'


def getAllProjectList(search):
    path = public.getWwwDir()
    dlist = []
    if os.path.exists(path):
        for filename in os.listdir(path):
            tmp = {}
            filePath = path + '/' + filename
            if os.path.isdir(filePath):
                if search == '':
                    tmp['name'] = filename
                    tmp['dir'] = filePath
                    dlist.append(tmp)
                else:
                    if filename.find(search) != -1:
                        tmp['name'] = filename
                        tmp['dir'] = filePath
                        dlist.append(tmp)
    return dlist


def checkProjectListIsSet(data):
    dlen = len(data)
    for x in range(dlen):
        path = getServerDir() + '/' + data[x]['name'] + '.json'
        if os.path.exists(path):
            if os.path.getsize(path) == 0:
                data[x]['isset'] = False
            else:
                data[x]['isset'] = True
        else:
            data[x]['isset'] = False

    return data


def projectListEdit():
    args = getArgs()
    if not 'name' in args:
        return 'missing name!'

    file = getServerDir() + '/' + args['name'] + '.json'
    if not os.path.exists(file):
        public.execShell('touch ' + file)
    return file


def projectListDel():
    args = getArgs()
    if not 'name' in args:
        return 'missing name!'

    file = getServerDir() + '/' + args['name'] + '.json'
    if os.path.exists(file):
        content = public.readFile(file)
        contentObj = json.loads(content)
        asyncUser = contentObj['client_email']
        cmd = getServerDir() + '/google-cloud-sdk/bin/'
        public.execShell(cmd + 'gcloud auth revoke ' + asyncUser)
        public.execShell('rm -rf ' + file)
    return 'ok'


def checkUserExist(cmd, user):
    data = public.execShell(cmd + 'gcloud auth list | grep ' + user)
    if data[0] == '':
        return False
    return True


def projectListAsync():
    import subprocess
    args = getArgs()
    if not 'name' in args:
        return 'missing name!'

    file = getServerDir() + '/' + args['name'] + '.json'
    if not os.path.exists(file):
        return 'not configured file!'

    content = public.readFile(file)
    contentObj = json.loads(content)
    asyncUser = contentObj['client_email']
    cmd = getServerDir() + '/google-cloud-sdk/bin/'
    projectDir = public.getWwwDir() + '/' + args['name']

    if not checkUserExist(cmd, asyncUser):
        public.execShell(
            cmd + 'gcloud auth activate-service-account --key-file ' + file)

    pName = contentObj['project_id']
    setUserCmd = cmd + 'gcloud config set account ' + asyncUser
    setUserCmd += ' && ' + cmd + 'gcloud config set project ' + pName
    asyncCmd = setUserCmd + ' && cd ' + projectDir + \
        ' && ' + cmd + 'gcloud app deploy << y'

    taskAdd = (None,  'gae[async]',
               'execshell', '0', time.strftime('%Y-%m-%d %H:%M:%S'), asyncCmd)
    public.M('tasks').add('id,name,type,status,addtime, execstr', taskAdd)
    return 'ok'


def projectListCmd():
    args = getArgs()
    if not 'name' in args:
        return 'missing name!'

    file = getServerDir() + '/' + args['name'] + '.json'
    if not os.path.exists(file):
        return 'not configured file!'

    content = public.readFile(file)
    contentObj = json.loads(content)
    asyncUser = contentObj['client_email']
    cmd = getServerDir() + '/google-cloud-sdk/bin/'
    pName = contentObj['project_id']
    projectDir = public.getWwwDir() + '/' + args['name']

    setUserCmd = cmd + 'gcloud config set account ' + asyncUser
    setUserCmd += ' && ' + cmd + 'gcloud config set project ' + pName
    asyncCmd = setUserCmd + ' && cd ' + projectDir + \
        ' && ' + cmd + 'gcloud app deploy <<EOF y' + "\nEOF"
    return asyncCmd


def projectListUrl():
    args = getArgs()
    if not 'name' in args:
        return 'missing name!'

    file = getServerDir() + '/' + args['name'] + '.json'
    if not os.path.exists(file):
        return 'not configured file!'

    content = public.readFile(file)
    contentObj = json.loads(content)
    asyncUser = contentObj['client_email']
    plist = asyncUser.split('@')

    url = 'https://' + plist[0] + '.appspot.com'
    return url


def projectList():
    args = getArgs()

    page = 1
    page_size = 10
    search = ''
    if 'page' in args:
        page = int(args['page'])

    if 'page_size' in args:
        page_size = int(args['page_size'])

    if 'search' in args:
        search = args['search']

    dlist = getAllProjectList(search)
    dlist_sum = len(dlist)

    start = (page - 1) * page_size
    ret_data = dlist[start:start + page_size]
    ret_data = checkProjectListIsSet(ret_data)

    data = {}
    data['data'] = ret_data
    data['list'] = public.getPage(
        {'count': dlist_sum, 'p': page, 'row': 10, 'tojs': 'projectList'})
    return public.getJson(data)

if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print status()
    elif func == 'project_list':
        print projectList()
    elif func == 'project_list_edit':
        print projectListEdit()
    elif func == 'project_list_del':
        print projectListDel()
    elif func == 'project_list_async':
        print projectListAsync()
    elif func == 'project_list_cmd':
        print projectListCmd()
    elif func == 'project_list_url':
        print projectListUrl()
    else:
        print 'error'
