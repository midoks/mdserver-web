# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

from admin.model import db, Users

import core.mw as mw

def getUserByName(name,
) -> None:
    '''
    获取用户信息通过用户名
    '''
    item =  Users.query.filter(Users.name==name).first()
    if item is None:
        return None
    row = {}
    row['id'] = item.id
    row['name'] = item.name
    row['password'] = item.password
    row['login_ip'] = item.login_ip
    row['login_time'] = item.login_time
    row['phone'] = item.phone
    row['email'] = item.email
    row['add_time'] = item.add_time
    row['update_time'] = item.update_time
    return row

def isLoginCheck(username, password) -> bool:
    info = getUserByName(data['username'])
    if info is None:
        return False

    if info['password'] == mw.md5(password):
        return True
    return False
