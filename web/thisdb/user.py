# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import core.mw as mw

# 初始化用户信息
def initAdminUser():
    data = mw.M('users').field('id').where('id=?', (1,)).find()
    if data is None:
        name = mw.getRandomString(8).lower()
        password = mw.getRandomString(8).lower()
        insert_time = mw.formatDate()
        login_ip = '127.0.0.1'
        add_user = {
            'name':name, 
            'password':mw.md5(password),
            'login_ip':login_ip,
            'login_time':insert_time,
            'phone':'',
            'email':'',
            'add_time':insert_time,
            'update_time':insert_time
        }
        file_pass_pl = mw.getPanelDataDir() + '/default.pl'
        mw.writeFile(file_pass_pl, password)
        mw.M('users').insert(add_user)
    return True


def getUserByName(name,
) -> None:
    '''
    获取用户信息通过用户名
    '''
    users_field = 'id,name,password,login_ip,login_time,phone,email,add_time,update_time'
    data =  mw.M('users').field(users_field).where('name=?', (name,)).find()
    if data is None:
        return None
    row = {}
    row['id'] = data['id']
    row['name'] = data['name']
    row['password'] = data['password']
    row['login_ip'] = data['login_ip']
    row['login_time'] = data['login_time']
    row['phone'] = data['phone']
    row['email'] = data['email']
    row['add_time'] = data['add_time']
    row['update_time'] = data['update_time']
    return row

def getUserById(id,
) -> None:
    '''
    获取用户信息通过用户名
    '''
    users_field = 'id,name,password,login_ip,login_time,phone,email,add_time,update_time'
    data =  mw.M('users').field(users_field).where('id=?', (1,)).find()
    if data is None:
        return None
    row = {}
    row['id'] = data['id']
    row['name'] = data['name']
    row['password'] = data['password']
    row['login_ip'] = data['login_ip']
    row['login_time'] = data['login_time']
    row['phone'] = data['phone']
    row['email'] = data['email']
    row['add_time'] = data['add_time']
    row['update_time'] = data['update_time']
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