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


class firewall_api:

    def __init__(self):
        pass

    ##### ----- start ----- ###
    def getWwwPathApi(self):
        path = public.getLogsDir()
        return public.getJson({'path': path})

    def getListApi(self):
        p = request.form.get('p', '1').strip()
        limit = request.form.get('limit', '10').strip()
        return self.getList(int(p), int(limit))

    def getLogListApi(self):
        p = request.form.get('p', '1').strip()
        limit = request.form.get('limit', '10').strip()
        search = request.form.get('search', '').strip()
        return self.getLogList(int(p), int(limit), search)

    def getSshInfoApi(self):
        file = '/etc/ssh/sshd_config'
        conf = public.readFile(file)
        rep = "#*Port\s+([0-9]+)\s*\n"
        port = re.search(rep, conf).groups(0)[0]

        data = {}
        data['port'] = port
        data['status'] = True
        data['ping'] = True
        if public.isAppleSystem():
            data['firewall_status'] = False
        else:
            data['firewall_status'] = True
        return public.getJson(data)
    ##### ----- start ----- ###

    def getList(self, page, limit):

        start = (page - 1) * limit

        _list = public.M('firewall').field('id,port,ps,addtime').limit(
            str(start) + ',' + str(limit)).order('id desc').select()
        data = {}
        data['data'] = _list

        count = public.M('firewall').count()
        _page = {}
        _page['count'] = count
        _page['tojs'] = 'showAccept'
        _page['p'] = page

        data['page'] = public.getPage(_page)
        return public.getJson(data)

    def getLogList(self, page, limit, search=''):
        find_search = ''
        if search != '':
            find_search = "type like '%" + search + "%' or log like '%" + \
                search + "%' or addtime like '%" + search + "%'"

        start = (page - 1) * limit

        _list = public.M('logs').where(find_search, ()).field(
            'id,type,log,addtime').limit(str(start) + ',' + str(limit)).order('id desc').select()
        data = {}
        data['data'] = _list

        count = public.M('logs').where(find_search, ()).count()
        _page = {}
        _page['count'] = count
        _page['tojs'] = 'getLogs'
        _page['p'] = page

        data['page'] = public.getPage(_page)
        return public.getJson(data)
