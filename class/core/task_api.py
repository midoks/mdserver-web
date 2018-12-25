# coding: utf-8

import psutil
import time
import os
import sys
import public
import re
import json
import pwd


class task_api:

    def __init__(self):
        pass

    def countApi(self):
        c = public.M('tasks').where("status!=?", ('1',)).count()
        return str(c)

    def list(self):
        _list = public.M('tasks').where('', ()).field('id,name,type,status,addtime,start,end').limit(
            '0,5').order('id desc').select()
        _ret = {}
        _ret['data'] = _list

        count = public.M('tasks').where('', ()).count()
        _page = {}
        _page['count'] = count
        _page['tojs'] = 'remind'

        _ret['page'] = public.getPage(_page)
        return public.getJson(_ret)

    def getExecLog(self):
        file = os.getcwd() + "/tmp/panelExec.log"
        v = public.getLastLine(file, 100)
        return v

    def getTaskSpeed(self):
        tempFile = os.getcwd() + '/tmp/panelExec.log'
        freshFile = os.getcwd() + '/tmp/panelFresh'

        find = public.M('tasks').where('status=? OR status=?',
                                       ('-1', '0')).field('id,type,name,execstr').find()
        if not len(find):
            return public.returnJson(False, '当前没有任务队列在执行-2!')

        isTask = os.getcwd() + '/tmp/panelTask.pl'
        public.writeFile(isTask, 'True')

        echoMsg = {}
        echoMsg['name'] = find['name']
        echoMsg['execstr'] = find['execstr']
        if find['type'] == 'download':
            import json
            try:
                tmp = public.readFile(tempFile)
                if len(tmp) < 10:
                    return public.returnMsg(False, '当前没有任务队列在执行-3!')
                echoMsg['msg'] = json.loads(tmp)
                echoMsg['isDownload'] = True
            except:
                db.Sql().table('tasks').where(
                    "id=?", (find['id'],)).save('status', ('0',))
                return public.returnMsg(False, '当前没有任务队列在执行-4!')
        else:
            echoMsg['msg'] = public.getLastLine(tempFile, 20)
            echoMsg['isDownload'] = False

        echoMsg['task'] = public.M('tasks').where("status!=?", ('1',)).field(
            'id,status,name,type').order("id asc").select()
        return public.getJson(echoMsg)
