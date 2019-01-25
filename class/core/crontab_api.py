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

        data = []
        for i in range(len(_list)):
            tmp = _list[i]
            if _list[i]['type'] == "day":
                tmp['type'] = '每天'
                tmp['cycle'] = public.getInfo('每天, {1}点{2}分 执行', (str(
                    _list[i]['where_hour']), str(_list[i]['where_minute'])))
            elif _list[i]['type'] == "day-n":
                tmp['type'] = public.getInfo(
                    '每{1}天', (str(_list[i]['where1']),))
                tmp['cycle'] = public.getInfo('每隔{1}天, {2}点{3}分 执行',  (str(
                    _list[i]['where1']), str(_list[i]['where_hour']), str(_list[i]['where_minute'])))
            elif _list[i]['type'] == "hour":
                tmp['type'] = '每小时'
                tmp['cycle'] = public.getInfo(
                    '每小时, 第{1}分钟 执行', (str(_list[i]['where_minute']),))
            elif _list[i]['type'] == "hour-n":
                tmp['type'] = public.getInfo(
                    '每{1}小时', (str(_list[i]['where1']),))
                tmp['cycle'] = public.getInfo('每{1}小时, 第{2}分钟 执行', (str(
                    _list[i]['where1']), str(_list[i]['where_minute'])))
            elif _list[i]['type'] == "minute-n":
                tmp['type'] = public.getInfo(
                    '每{1}分钟', (str(_list[i]['where1']),))
                tmp['cycle'] = public.getInfo(
                    '每隔{1}分钟执行', (str(_list[i]['where1']),))
            elif _list[i]['type'] == "week":
                tmp['type'] = '每周'
                if not _list[i]['where1']:
                    _list[i]['where1'] = '0'
                tmp['cycle'] = public.getInfo('每周{1}, {2}点{3}分执行', (self.toWeek(int(
                    _list[i]['where1'])), str(_list[i]['where_hour']), str(_list[i]['where_minute'])))
            elif _list[i]['type'] == "month":
                tmp['type'] = '每月'
                tmp['cycle'] = public.getInfo('每月, {1}日 {2}点{3}分执行', (str(_list[i]['where1']), str(
                    _list[i]['where_hour']), str(_list[i]['where_minute'])))
            data.append(tmp)

        _ret = {}
        _ret['data'] = data

        count = public.M('crontab').where('', ()).count()
        _page = {}
        _page['count'] = count
        _page['tojs'] = 'remind'

        _ret['page'] = public.getPage(_page)
        return public.getJson(_ret)

    def logsApi(self):
        return public.returnJson(False, '添加失败')

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

    # 转换大写星期
    def toWeek(self, num):
        wheres = {
            0:   '日',
            1:   '一',
            2:   '二',
            3:   '三',
            4:   '四',
            5:   '五',
            6:   '六'
        }
        try:
            return wheres[num]
        except:
            return ''
