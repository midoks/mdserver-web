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

def getUserById(id,
) -> None:
    '''
    获取用户信息通过用户名
    '''
    item =  Users.query.filter(Users.id==id).first()
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

def getUserByRoot() -> None:
    '''
    获取用户信息通过用户名
    '''
    return getUserById(1)

def setUserByRoot(
    name: str | None = None,
    password: str | None = None,
) -> bool:
    '''
    设置配置的值
    :name -> str 名称 (必填)
    :value -> object值 (必填)
    :type -> str 类型 (可选|默认common)
    '''
    data = {}

    if name is not None:
        data['name'] = name

    if password is not None:
        data['password'] = mw.md5(password)
    
    Users.query.filter(Users.id==1).update(data)
    db.session.commit()
    return True

def isLoginCheck(username, password) -> bool:
    info = getUserByName(data['username'])
    if info is None:
        return False

    if info['password'] == mw.md5(password):
        return True
    return False
