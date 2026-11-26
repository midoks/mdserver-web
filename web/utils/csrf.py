# coding:utf-8
# ---------------------------------------------------------------------------------
# MW-Linux面板 - CSRF 双提交 Cookie/Header 防护
# ---------------------------------------------------------------------------------
# 后端: 首次 GET 时下发 cookie csrf_token (httponly=False, JS 可读)
# 前端: $.ajaxSetup 全局读取 cookie 放入 X-CSRF-Token header
# 校验: POST/PUT/PATCH/DELETE 请求比较 cookie 与 header, 使用 secrets.compare_digest
# ---------------------------------------------------------------------------------

import secrets

from flask import request, make_response

# 前端全局拦截统一从 cookie 读 token 放 header, 这两个名字必须一致
COOKIE_NAME = 'csrf_token'
HEADER_NAME = 'X-CSRF-Token'

# 自动豁免的路径前缀 (GET/HEAD/OPTIONS 天然豁免, 这里处理 POST 豁免)
EXEMPT_PREFIXES = (
    '/static/', '/favicon.ico', '/code', '/login',
    '/quick_login/ticket', '/quick_login/entry',
    '/download', '/hook', '/down',
)

# 自动豁免的方法
SAFE_METHODS = {'GET', 'HEAD', 'OPTIONS', 'TRACE'}


def is_exempt(path):
    """判断请求路径是否在 CSRF 豁免列表里"""
    if path is None:
        return True
    for prefix in EXEMPT_PREFIXES:
        if path.startswith(prefix):
            return True
    return False


def generate_token():
    """生成 32 字节 urlsafe token, 每次调用随机"""
    return secrets.token_urlsafe(32)


def set_csrf_cookie(response, token=None):
    """把 token 写入 cookie (httponly=False 让 JS 可读)"""
    if token is None:
        token = generate_token()
    # secure 交给 __init__.py before_request 根据 SSL 配置决定
    try:
        response.set_cookie(
            COOKIE_NAME, token,
            httponly=False,       # 必须让 JS 能读, 才能放 header
            samesite='Lax',
            path='/',
        )
    except Exception:
        # 部分旧版 Werkzeug 参数不同, 降级
        response.set_cookie(COOKIE_NAME, token, httponly=False)
    return token


def verify_csrf(request_obj=None):
    """校验请求的 CSRF token: cookie 与 header 必须相等. 相等返回 True, 否则 False"""
    req = request_obj or request
    cookie_token = req.cookies.get(COOKIE_NAME, '')
    header_token = req.headers.get(HEADER_NAME, '')

    # 也兼容表单里直接带 csrf_token (老旧浏览器/表单直提场景)
    if header_token == '':
        header_token = req.form.get('csrf_token', '')

    if not cookie_token or not header_token:
        return False
    try:
        return secrets.compare_digest(cookie_token, header_token)
    except Exception:
        return False


def apply_csrf_before_request():
    """供 Flask before_request 调用:
       1. 对 SAFE_METHODS / exempt 路径直接放行, 首次请求顺便下发 cookie
       2. 对危险方法校验 cookie == header
       返回 None 表示放行, 返回 Response 表示拦截."""
    method = (request.method or 'GET').upper()
    path = request.path or '/'

    # 1. 安全方法直接放行 (顺便让 login 这种 GET 页自然拿到 cookie)
    if method in SAFE_METHODS:
        return None

    # 2. 豁免路径
    if is_exempt(path):
        return None

    # 3. 主面板 BasicAuth / App-Id 认证接口也豁免 (已在 user_login_check 里自行鉴权)
    if request.headers.get('App-Id', '') != '' and request.headers.get('App-Secret', '') != '':
        return None

    # 4. 执行校验
    if verify_csrf():
        return None

    # 校验失败 -> 403 JSON
    import core.mw as mw
    from flask import make_response
    resp = make_response(mw.returnJson(False, 'CSRF token 无效, 请刷新页面重试!'), 403)
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp
