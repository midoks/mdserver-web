# coding: utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------
# 日志类操作
# ---------------------------------------------------------------------------------

import psutil
import time
import os
import sys
import mw
import re
import json
import pwd

from flask import request


class logs_api:

    def __init__(self):
        pass

    def delPanelLogsApi(self):
        mw.M('logs').where('id>?', (0,)).delete()
        mw.writeLog('面板设置', '面板操作日志已清空!')
        return mw.returnJson(True, '面板操作日志已清空!')

    def getLogListApi(self):
        p = request.form.get('p', '1').strip()
        limit = request.form.get('limit', '10').strip()
        search = request.form.get('search', '').strip()
        return self.getLogList(int(p), int(limit), search)

    def getLogList(self, page, limit, search=''):
        find_search = ''
        if search != '':
            find_search = "type like '%" + search + "%' or log like '%" + \
                search + "%' or addtime like '%" + search + "%'"

        start = (page - 1) * limit

        _list = mw.M('logs').where(find_search, ()).field(
            'id,type,log,addtime').limit(str(start) + ',' + str(limit)).order('id desc').select()
        data = {}
        data['data'] = _list

        count = mw.M('logs').where(find_search, ()).count()
        _page = {}
        _page['count'] = count
        _page['tojs'] = 'getLogs'
        _page['p'] = page

        data['page'] = mw.getPage(_page)
        return mw.getJson(data)
