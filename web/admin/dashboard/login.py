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
import base64
import hashlib
import hmac
import json
import secrets

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


def getLoginPageUrl():
    admin_path = thisdb.getOption('admin_path')
    if admin_path:
        return '/' + admin_path
    return '/login'


QUICK_LOGIN_KEY_OPTION = 'quick_login_key'
QUICK_LOGIN_TICKET_TTL = 60


def getQuickLoginKey():
    """获取/初始化本面板的快捷登录密钥"""
    key = thisdb.getOption(QUICK_LOGIN_KEY_OPTION, default='')
    if not key:
        key = secrets.token_hex(32)
        thisdb.setOption(QUICK_LOGIN_KEY_OPTION, key)
    return key


def resetQuickLoginKey():
    key = secrets.token_hex(32)
    thisdb.setOption(QUICK_LOGIN_KEY_OPTION, key)
    return key


def isQuickLoginEnabled():
    # 开启二次验证时不签发快捷登录票据, 避免绕过 TOTP
    two_step_verification = thisdb.getOptionByJson('two_step_verification', default={'open':False})
    return not (two_step_verification and two_step_verification.get('open'))


def makeQuickLoginTicket(username):
    """生成一次性登录票据: base64(payload).hmac, 默认 60 秒有效"""
    payload = {
        'u': username,
        'e': int(time.time()) + QUICK_LOGIN_TICKET_TTL,
        'n': secrets.token_hex(16),
    }
    body = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(',', ':')).encode('utf-8')
    ).decode('utf-8').rstrip('=')
    sig = hmac.new(getQuickLoginKey().encode('utf-8'),
                   body.encode('utf-8'), hashlib.sha256).hexdigest()
    return body + '.' + sig


def parseQuickLoginTicket(ticket):
    """校验票据签名与有效期, 通过后返回用户名, 否则返回 None"""
    try:
        body, sig = (ticket or '').split('.', 1)
        expect = hmac.new(getQuickLoginKey().encode('utf-8'),
                          body.encode('utf-8'), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expect, sig):
            return None

        padding = '=' * (-len(body) % 4)
        payload = json.loads(base64.urlsafe_b64decode(body + padding).decode('utf-8'))
        if int(payload.get('e', 0)) < int(time.time()):
            return None
        return payload
    except Exception:
        return None


# 关联面板(A)服务端调用: 用密钥换取一次性登录票据
@blueprint.route('/quick_login/ticket', methods=['POST'])
def quickLoginTicket():
    if thisdb.getOption('admin_close') == 'yes':
        return mw.returnJson(False, '面板已经关闭!')

    if not isQuickLoginEnabled():
        return mw.returnJson(False, '目标面板已开启二次验证, 请手动登录!')

    key = request.form.get('key', '').strip()
    if key == '':
        key = request.headers.get('X-Quick-Login-Key', '').strip()

    if key == '' or not hmac.compare_digest(key, getQuickLoginKey()):
        mw.writeLog('用户登录', mw.getInfo('快捷登录密钥错误, 登录IP:{1}', (request.remote_addr,)))
        return mw.returnJson(False, '登录密钥错误!')

    info = thisdb.getUserByRoot()
    if info is None:
        return mw.returnJson(False, '用户不存在!')

    return mw.returnJson(True, 'ok', {'ticket': makeQuickLoginTicket(info['name'])})


# 浏览器访问: 消费一次性票据并建立登录会话
@blueprint.route('/quick_login/entry', methods=['GET'])
def quickLoginEntry():
    payload = parseQuickLoginTicket(request.args.get('ticket', ''))
    if payload is None:
        return redirect(getLoginPageUrl())

    if not isQuickLoginEnabled():
        return redirect(getLoginPageUrl())

    # 票据一次性使用, 用完立即失效
    used = thisdb.getOptionByJson('quick_login_used', default={})
    now = int(time.time())
    used = {k: v for k, v in used.items() if v > now}
    nonce = payload.get('n', '')
    if nonce == '' or nonce in used:
        return redirect(getLoginPageUrl())
    used[nonce] = int(payload.get('e', 0))
    thisdb.setOption('quick_login_used', json.dumps(used))

    info = thisdb.getUserByRoot()
    if info is None or info['name'] != payload.get('u', ''):
        return redirect(getLoginPageUrl())

    session.clear()
    session['login'] = True
    session['username'] = info['name']
    session['overdue'] = int(time.time()) + 7 * 24 * 60 * 60
    # regenerate session 防会话固定
    thisdb.updateUserLoginTime()
    mw.writeLog('用户登录', mw.getInfo("快捷登录成功,帐号:{1},登录IP:{2}", (info['name'], mw.getClientIp())))
    return redirect('/')


def _get_login_limit_key():
    """防爆破缓存 key: 按 IP 分桶, 避免一个攻击者把面板锁死"""
    return 'login_limit_' + mw.md5(mw.getClientIp())

def _bump_login_limit(threshold=5, window=3600):
    """递增登录失败计数, 返回 (当前计数, 是否达阈值)"""
    key = _get_login_limit_key()
    count = cache.get(key) or 0
    count += 1
    cache.set(key, count, timeout=window)
    return count, count >= threshold

def _clear_login_limit():
    """登录成功后清本 IP 的失败计数"""
    cache.delete(_get_login_limit_key())

def _get_login_limit_remain(threshold=5):
    """返回本 IP 剩余可尝试次数"""
    count = cache.get(_get_login_limit_key()) or 0
    remain = threshold - count
    return remain if remain > 0 else 0

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
    
    session.clear()  # regenerate session 防会话固定
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
    from utils.csrf import COOKIE_NAME as CSRF_COOKIE_NAME
    name = thisdb.getOption('template', default='default')

    # 临时登录功能
    token = request.args.get('tmp_token', '').strip()
    if token != '':
        return login_temp_user(token)

    # 注销登录: 清 session + 清 csrf cookie + 强制重新下发
    signout = request.args.get('signout', '')
    if signout == 'True':
        session.clear()
        session['login'] = False
        session['overdue'] = 0

    admin_path = thisdb.getOption('admin_path')
    if admin_path == '':
        resp = make_response(render_template('%s/login.html' % name))
    else:
        unauthorized_status = thisdb.getOption('unauthorized_status')
        if unauthorized_status == '0':
            resp = make_response(render_template('%s/path.html' % name))
        else:
            resp = make_response(Response(status=int(unauthorized_status)))

    # 退出时清 csrf_token cookie (让旧 token 失效, 下一次访问会重新下发新的)
    if signout == 'True':
        resp.delete_cookie(CSRF_COOKIE_NAME, path='/')
    return resp

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

    info = thisdb.getUserByRoot()
    if info is None or info['name'] != username:
        # 统一错误: 不泄露用户名存在性; 仍然走一次密码比对掩盖时序
        mw.verifyPassword(password, info['password'] if info else '')
        _, locked = _bump_login_limit()
        if locked:
            thisdb.setOption('admin_close', 'yes')
            return mw.returnJson(-1, '面板已经关闭!')
        mw.writeLog('用户登录', mw.getInfo("二次验证用户不存在,帐号:{1},登录IP:{2}", (username, mw.getClientIp())))
        return mw.returnJson(-1, "密码或二次验证错误")

    # 用 verifyPassword (bcrypt/md5 自动识别 + 常量时间)
    pwd_ok, need_upgrade = mw.verifyPassword(password, info['password'])
    if not pwd_ok:
        _, locked = _bump_login_limit()
        if locked:
            thisdb.setOption('admin_close', 'yes')
            return mw.returnJson(-1, '面板已经关闭!')
        mw.writeLog('用户登录', mw.getInfo("二次验证密码错误,帐号:{1},登录IP:{2}", (username, mw.getClientIp())))
        return mw.returnJson(-1, "密码或二次验证错误")

    # md5 存储的老用户自动升级为 bcrypt
    if need_upgrade:
        thisdb.setUserPwdByName(info['name'], password)

    auth = request.form.get('auth', '').strip()
    two_step_verification = thisdb.getOptionByJson('two_step_verification', default={'open':False})
    if two_step_verification['open']:
        sec = mw.deDoubleCrypt('mdserver-web', two_step_verification['secret'])
        totp = pyotp.TOTP(sec)
        if totp.verify(auth):
            _clear_login_limit()
            session.clear()  # regenerate session 防会话固定
            session['login'] = True
            session['username'] = info['name']
            session['overdue'] = int(time.time()) + 7 * 24 * 60 * 60

            thisdb.updateUserLoginTime()
            mw.writeLog('用户登录', mw.getInfo("二次验证登录成功,帐号:{1},登录IP:{2}", (info['name'], mw.getClientIp())))
            return mw.returnData(1, '二次验证成功!')

    # 二次验证失败 (未开二次验证但还走到这里不会触发此分支, 因为上面直接会返回)
    _, locked = _bump_login_limit()
    if locked:
        thisdb.setOption('admin_close', 'yes')
        return mw.returnJson(-1, '面板已经关闭!')
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

    # 书签/一键跳转使用后台表单提交(redirect=1), 无法携带验证码,
    # 此处跳过验证码; 失败锁定与二次验证仍然生效
    if 'code' in session and request.form.get('redirect', '') == '':
        if session['code'] != mw.md5(code):
            _, locked = _bump_login_limit()
            if locked:
                thisdb.setOption('admin_close', 'yes')
                return mw.returnData(False, '面板已经关闭!')
            remain = _get_login_limit_remain()
            login_err_msg = mw.getInfo("验证码错误,您还可以尝试[{1}]次!", (str(remain)))
            mw.writeLog('用户登录', login_err_msg)
            return mw.returnData(False, login_err_msg)

    info = thisdb.getUserByName(username)

    # 防枚举: 无论用户是否存在都走一次 verifyPassword, 掩盖时序差异
    stored_hash = info['password'] if info else ''
    pwd_ok, need_upgrade = mw.verifyPassword(password, stored_hash)

    if info is None or info['name'] != username or not pwd_ok:
        _, locked = _bump_login_limit()
        if locked:
            thisdb.setOption('admin_close', 'yes')
            return mw.returnData(False, '面板已经关闭!')

        if info is None:
            mw.writeLog('用户登录', mw.getInfo("用户不存在,帐号:{1},登录IP:{2}", (username, mw.getClientIp())))
        else:
            mw.writeLog('用户登录', mw.getInfo("密码错误,帐号:{1},登录IP:{2}", (username, mw.getClientIp())))

        remain = _get_login_limit_remain()
        return mw.returnData(-1, mw.getInfo("用户名或密码错误,您还可以尝试[{1}]次!", (str(remain))))

    # md5 存储的老用户自动升级为 bcrypt (渐进式安全升级)
    if need_upgrade:
        thisdb.setUserPwdByName(info['name'], password)

    _clear_login_limit()
    # 二步验证密钥
    two_step_verification = thisdb.getOptionByJson('two_step_verification', default={'open':False})
    if two_step_verification['open']:
        # 书签跳转等表单登录: 跳回登录页, 由登录页完成二次验证
        if request.form.get('redirect', '') != '':
            return redirect(getLoginPageUrl())
        return mw.returnData(2, '需要两步验证!')

    session.clear()
    session['login'] = True
    session['username'] = info['name']
    session['overdue'] = int(time.time()) + 7 * 24 * 60 * 60
    # regenerate session 防会话固定: session.clear() 后签名 cookie 值完全改变

    thisdb.updateUserLoginTime()
    mw.writeLog('用户登录', mw.getInfo("登录成功,帐号:{1},登录IP:{2}", (info['name'], mw.getClientIp())))
    # 书签跳转等表单登录: 登录成功后直接回到首页
    if request.form.get('redirect', '') != '':
        return redirect('/')
    return mw.returnData(1, '登录成功,正在跳转...')
