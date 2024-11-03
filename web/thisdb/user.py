# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import core.mw as mw


def getUserById(id,
) -> None:
    '''
    获取用户信息通过用户名
    '''
    users_field = 'id,name,password,login_ip,login_time,phone,email,add_time,update_time'
    item =  mw.M('users').field(users_field).where('id=?', (1,)).select()
    if len(item) == 0:
        return None
    row = {}
    row['id'] = item[0]['id']
    row['name'] = item[0]['name']
    row['password'] = item[0]['password']
    row['login_ip'] = item[0]['login_ip']
    row['login_time'] = item[0]['login_time']
    row['phone'] = item[0]['phone']
    row['email'] = item[0]['email']
    row['add_time'] = item[0]['add_time']
    row['update_time'] = item[0]['update_time']
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
        mw.M('users').where('id=?', (1,)).setField('username', name)

    if password is not None:
        pwd = mw.md5(password)
        mw.M('users').where('id=?', (1,)).setField('password', pwd)

    if not data:
        return False
    return True