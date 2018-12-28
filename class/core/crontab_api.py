# coding: utf-8

import psutil
import time
import os
import sys
import public
import re
import json
import pwd

from flask import request


class crontab_api:

    def __init__(self):
        pass

    ##### ----- start ----- ###
    def listApi(self):
        _list = public.M('crontab').where('', ()).field('id,name,type,where1,where_hour,where_minute,echo,addtime,status,save,backup_to,stype,sname,sbody,urladdress').limit(
            '0,5').order('id desc').select()
        _ret = {}
        _ret['data'] = _list

        count = public.M('crontab').where('', ()).count()
        _page = {}
        _page['count'] = count
        _page['tojs'] = 'remind'

        _ret['page'] = public.getPage(_page)
        return public.getJson(_ret)

    def addApi(self):
        name = request.form.get('name', '')
        type = request.form.get('type', '')
        where1 = request.form.get('where1', '')
        hour = request.form.get('hour', '')
        minute = request.form.get('minute', '')
        save = request.form.get('save', '')
        backupTo = request.form.get('backupTo', '')
        sType = request.form.get('sType', '')
        sName = request.form.get('sName', '')
        sBody = request.form.get('sBody', '')
        urladdress = request.form.get('urladdress', '')
        if len(name) < 1:
            return public.returnJson(False, '任务名称不能为空!')

        addData = public.M('crontab').add('name,type,where1,where_hour,where_minute,echo,addtime,status,save,backup_to,stype,sname,sbody,urladdress',
                                          (name, type, where1, hour, minute, name,
                                           time.strftime('%Y-%m-%d %X', time.localtime()), 1, save, backupTo, sType, sName, sBody, urladdress))
        if addData > 0:
            return public.returnJson(True, '添加成功')
        return public.returnJson(False, '添加失败')

    def delApi(self):
        id = request.form.get('id', '')
        try:
            public.M('crontab').where("id=?", (id,)).delete()
            return public.returnJson(True, '添加成功')
        except Exception as e:
            return public.returnJson(False, '删除失败')
    ##### ----- start ----- ###
