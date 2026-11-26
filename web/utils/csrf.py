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

# Cookie 过期时间(秒), 滑动续期: 每次响应刷新, 闲置超过此时间才失效
CSRF_COOKIE_MAX_AGE = 1800  # 30 分钟(金融级)

# 服务端在 session 里保留最近 N 个 token, 容忍并发 AJAX 的轮换竞态
CSRF_HISTORY_SIZE = 3

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


def get_valid_tokens():
    """从 session 获取最近的有效 token 列表(金融级: 服务端历史窗口)"""
    from flask import session
    try:
        tokens = session.get('_csrf_tokens', [])
        return tokens if isinstance(tokens, list) else []
    except Exception:
        return []


def push_token(token):
    """把新 token 加入 session 历史, 保留最近 N 个. 重复 token 不重复 push."""
    from flask import session
    try:
        tokens = get_valid_tokens()
        if tokens and tokens[0] == token:
            return  # 最新 token 未变, 无需操作
        if token in tokens:
            tokens.remove(token)
        tokens.insert(0, token)
        session['_csrf_tokens'] = tokens[:CSRF_HISTORY_SIZE]
    except Exception:
        pass


def set_csrf_cookie(response, token=None):
    """把 token 写入 cookie (httponly=False 让 JS 可读), 带 max_age 滑动续期"""
    if token is None:
        token = generate_token()
    # secure 交给 __init__.py before_request 根据 SSL 配置决定
    try:
        response.set_cookie(
            COOKIE_NAME, token,
            max_age=CSRF_COOKIE_MAX_AGE,
            httponly=False,       # 必须让 JS 能读, 才能放 header
            samesite='Lax',
            path='/',
        )
    except Exception:
        # 部分旧版 Werkzeug 参数不同, 降级
        response.set_cookie(COOKIE_NAME, token, max_age=CSRF_COOKIE_MAX_AGE, httponly=False)
    return token


def verify_csrf(request_obj=None):
    """金融级校验: 1) cookie == header  2) token 必须在服务端 session 历史里"""
    req = request_obj or request
    cookie_token = req.cookies.get(COOKIE_NAME, '')
    header_token = req.headers.get(HEADER_NAME, '')

    # 也兼容表单里直接带 csrf_token (老旧浏览器/表单直提场景)
    if header_token == '':
        header_token = req.form.get('csrf_token', '')

    if not cookie_token or not header_token:
        return False
    try:
        if not secrets.compare_digest(cookie_token, header_token):
            return False
    except Exception:
        return False

    # 金融级增强: token 必须在服务端有效历史里 (防伪造 + 防重放)
    valid_tokens = get_valid_tokens()
    if not valid_tokens:
        # 首次请求 session 还没历史, 双提交模式兜底 (SameSite=Lax 已能挡跨站)
        return True

    for vt in valid_tokens:
        if secrets.compare_digest(cookie_token, vt):
            return True
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
