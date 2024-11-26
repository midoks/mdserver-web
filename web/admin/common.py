# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import time

from admin import session
import thisdb

def isLogined():
    if 'login' in session  and session['login'] == True and 'username' in session:
        username = session['username']
        info = thisdb.getUserByName(username)
        if info is None:
            return False

        # print(userInfo)
        if info['name'] != session['username']:
            return False

        now_time = int(time.time())

        if 'overdue' in session and now_time > session['overdue']:
            # 自动续期
            session['overdue'] = int(time.time()) + 7 * 24 * 60 * 60
            return False

        if 'tmp_login_expire' in session and now_time > int(session['tmp_login_expire']):
            session.clear()
            return False
        return True