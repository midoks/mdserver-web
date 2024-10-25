# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

from flask import request

from admin.model import db, Users
import admin.model.option as option
import core.mw as mw

# 初始化用户信息
def init_admin_user():
    data = Users.query.filter_by(id=1).first()
    if not data:
        name = mw.getRandomString(8).lower()
        password = mw.getRandomString(8).lower()
        file_pass_pl = mw.getPanelDataDir() + '/default_new.pl'
        mw.writeFile(file_pass_pl, password)
        insert_time = mw.formatDate()
        login_ip = '127.0.0.1'
        add_user = Users(
            name=name, 
            password=mw.md5(password),
            login_ip=login_ip,
            login_time=insert_time,
            phone='',
            email='',
            add_time=insert_time,
            update_time=insert_time)
        db.session.add(add_user)
        db.session.commit()
        db.session.close()
    return True

def init_option():
    option.setOption('title', '后羿面板')
    option.setOption('recycle_bin', 'open')
    option.setOption('template', 'default')

    # 首页展示初始化
    option.setOption('display_index', '[]')
    return True