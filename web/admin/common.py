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

# 进程内用户信息缓存: {username: (info_dict, expire_ts)}
# 不用 Flask-Caching 是因为 admin/__init__.py 里 cache 变量在 import common 之后才创建,
# 顶层 from admin import cache 会循环导入. 这里用模块级字典即可.
_USER_CACHE = {}
_USER_CACHE_TTL = 30  # 30 秒


def _get_user_cached(username):
    if username in _USER_CACHE:
        info, expire = _USER_CACHE[username]
        if time.time() < expire:
            return info
        del _USER_CACHE[username]
    info = thisdb.getUserByName(username)
    if info is not None:
        _USER_CACHE[username] = (info, time.time() + _USER_CACHE_TTL)
    return info


def invalidate_user_cache(username=None):
    """用户改密/改名后调用清缓存"""
    if username is None:
        _USER_CACHE.clear()
    else:
        _USER_CACHE.pop(username, None)


def isLogined():
    if 'login' in session and session['login'] == True and 'username' in session:
        username = session['username']
        info = _get_user_cached(username)
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