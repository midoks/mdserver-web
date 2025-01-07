# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import io
import time

from flask import Blueprint, render_template
from flask import make_response
from flask import redirect
from flask import Response
from flask import request,g

from admin.common import isLogined
from admin.user_login_check import panel_login_required
from admin import cache,session

import core.mw as mw
import thisdb

from .dashboard import blueprint


def getErrorNum(key, limit=None):
    key = mw.md5(key)
    num = cache.get(key)
    if not num:
        num = 0
    if not limit:
        return num
    if limit > num:
        return True
    return False


def setErrorNum(key, empty=False, expire=3600):
    key = mw.md5(key)
    num = cache.get(key)
    if not num:
        num = 0
    else:
        if empty:
            cache.delete(key)
            return True
    cache.set(key, num + 1, expire)
    return True

def login_temp_user(token):
    if len(token) != 32:
        return '错误的参数!'

    skey = mw.getClientIp() + '_temp_login'
    if not getErrorNum(skey, 10):
        return '连续10次验证失败，禁止1小时'

    stime = int(time.time())

    tmp_data = thisdb.getTempLoginByToken(token)
    if not tmp_data:
        setErrorNum(skey)
        return '验证失败!'

    if stime > int(tmp_data['expire']):
        setErrorNum(skey)
        return "过期"

    user_data = thisdb.getUserById(1)
    login_addr = mw.getClientIp() + ":" + str(request.environ.get('REMOTE_PORT'))
    mw.writeLog('用户临时登录', "登录成功,帐号:{1},登录IP:{2}",(user_data['name'], login_addr))

    mw.M('temp_login').where('id=?',(tmp_data['id'],)).update({"login_time": stime, 'state': 1, 'login_addr': login_addr})
    
    session['login'] = True
    session['username'] = user_data['name']
    session['tmp_login'] = True
    session['tmp_login_id'] = str(tmp_data['id'])
    session['tmp_login_expire'] = int(tmp_data['expire'])
    session['uid'] = user_data['id']
    
    return redirect('/')

# 登录页: 当设置了安全路径,本页失效。
@blueprint.route('/login')
def login():
    name = thisdb.getOption('template', default='default')

    # 临时登录功能
    token = request.args.get('tmp_token', '').strip()
    if token != '':
        return login_temp_user(token)

    # 注销登录
    signout = request.args.get('signout', '')
    if signout == 'True':
        session.clear()
        session['login'] = False
        session['overdue'] = 0

    admin_path = thisdb.getOption('admin_path')
    if admin_path == '':
        return render_template('%s/login.html' % name)
    else:
        unauthorized_status = thisdb.getOption('unauthorized_status')
        if unauthorized_status == '0':
            return render_template('%s/path.html' % name)
        return Response(status=int(unauthorized_status))

@blueprint.route('/close')
def close():
    name = thisdb.getOption('template', default='default')
    admin_close = thisdb.getOption('admin_close')
    if admin_close == 'no':
        return redirect('/', code=302)
    return render_template('%s/close.html' % name)


# 验证码
@blueprint.route('/code')
def code():
    import utils.vilidate as vilidate
    vie = vilidate.vieCode()
    codeImage = vie.GetCodeImage(80, 4)
    out = io.BytesIO()
    codeImage[0].save(out, "png")
    session['code'] = mw.md5(''.join(codeImage[1]).lower())

    img = Response(out.getvalue(), headers={'Content-Type': 'image/png'})
    return make_response(img)

# 检查是否登录
@blueprint.route('/check_login',methods=['GET','POST'])
def check_login():
    if isLogined():
        return mw.returnData(True,'已登录')
    return mw.returnData(False,'未登录')

@blueprint.route("/verify_login", methods=['POST'])
def verifyLogin():
    import pyotp

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    password = mw.md5(password)

    info = thisdb.getUserByRoot()
    if info['name'] != username or info['password'] != password:
        return mw.returnJson(-1, "密码错误?")

    auth = request.form.get('auth', '').strip()    
    two_step_verification = thisdb.getOptionByJson('two_step_verification', default={'open':False})
    if two_step_verification['open']:
        sec = mw.deDoubleCrypt('mdserver-web', two_step_verification['secret'])
        totp = pyotp.TOTP(sec)
        if totp.verify(auth):
            session['login'] = True
            session['username'] = info['name']
            session['overdue'] = int(time.time()) + 7 * 24 * 60 * 60

            thisdb.updateUserLoginTime()
            return mw.returnData(1, '二次验证成功!')
    return mw.returnData(-1, '二次验证失败!')

# 执行登录操作
@blueprint.route('/do_login', endpoint='do_login', methods=['POST'])
def do_login():
    admin_close = thisdb.getOption('admin_close')
    if admin_close == 'yes':
        return mw.returnData(False, '面板已经关闭!')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    code = request.form.get('code', '').strip()

    login_cache_count = 5
    login_cache_limit = cache.get('login_cache_limit')

    if 'code' in session:
        if session['code'] != mw.md5(code):
            if login_cache_limit == None:
                login_cache_limit = 1
            else:
                login_cache_limit = int(login_cache_limit) + 1

            if login_cache_limit >= login_cache_count:
                thisdb.setOption('admin_close', 'yes')
                return mw.returnData(False, '面板已经关闭!')

            cache.set('login_cache_limit', login_cache_limit, timeout=10000)
            login_cache_limit = cache.get('login_cache_limit')
            login_err_msg = mw.getInfo("验证码错误,您还可以尝试[{1}]次!", (str(login_cache_count - login_cache_limit)))
            mw.writeLog('用户登录', login_err_msg)
            return mw.returnData(False, login_err_msg)

    info = thisdb.getUserByName(username)
    password = mw.md5(password)

    if info is None:
        msg = mw.getInfo("<a style='color: red'>密码错误</a>,帐号:{1},密码:{2},登录IP:{3}", (username, '******', request.remote_addr))
        if login_cache_limit == None:
            login_cache_limit = 1
        else:
            login_cache_limit = int(login_cache_limit) + 1

        if login_cache_limit >= login_cache_count:
            thisdb.setOption('admin_close', 'yes')
            return mw.returnData(False, '面板已经关闭!')

        cache.set('login_cache_limit', login_cache_limit, timeout=10000)
        login_cache_limit = cache.get('login_cache_limit')
        mw.writeLog('用户登录', msg)
        return mw.returnData(-1, mw.getInfo("用户名或密码错误,您还可以尝试[{1}]次!", (str(login_cache_count - login_cache_limit))))

    # print(info)
    if info['name'] != username or info['password'] != password:
        msg = mw.getInfo("<a style='color: red'>密码错误</a>,帐号:{1},密码:{2},登录IP:{3}", (username, '******', request.remote_addr))

        if login_cache_limit == None:
            login_cache_limit = 1
        else:
            login_cache_limit = int(login_cache_limit) + 1

        if login_cache_limit >= login_cache_count:
            thisdb.setOption('admin_close', 'yes')
            return mw.returnData(False, '面板已经关闭!')

        cache.set('login_cache_limit', login_cache_limit, timeout=10000)
        login_cache_limit = cache.get('login_cache_limit')
        mw.writeLog('用户登录', msg)
        return mw.returnData(-1, mw.getInfo("用户名或密码错误,您还可以尝试[{1}]次!", (str(login_cache_count - login_cache_limit))))

    cache.delete('login_cache_limit')
    # 二步验证密钥
    two_step_verification = thisdb.getOptionByJson('two_step_verification', default={'open':False})
    if two_step_verification['open']:
        return mw.returnData(2, '需要两步验证!')

    session['login'] = True
    session['username'] = info['name']
    session['overdue'] = int(time.time()) + 7 * 24 * 60 * 60
    
    thisdb.updateUserLoginTime()
    return mw.returnData(1, '登录成功,正在跳转...')
