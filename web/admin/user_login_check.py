# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------


from flask import render_template
from flask import Response
from flask import request

from functools import wraps

import hmac
import ipaddress
import re

from admin import session
from admin.common import isLogined

import thisdb


def isIpInWhiteList(remote_addr, white_list):
    """校验请求来源IP是否在API白名单内, 支持单个IP、CIDR与通配符 *"""
    white_list = (white_list or '').strip()
    if white_list == '':
        return False
    if white_list == '*':
        return True

    try:
        ip = ipaddress.ip_address((remote_addr or '').strip())
    except ValueError:
        return False

    # 兼容 IPv4-mapped IPv6 地址
    if ip.version == 6 and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped

    for item in re.split(r'[,;\s]+', white_list):
        item = item.strip()
        if item == '':
            continue
        if item == '*':
            return True
        try:
            if '/' in item:
                if ip in ipaddress.ip_network(item, strict=False):
                    return True
            elif ip == ipaddress.ip_address(item):
                return True
        except ValueError:
            continue
    return False


def panel_login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        # 面板API调用检查
        app_id = request.headers.get('App-Id','')
        app_secret = request.headers.get('App-Secret','')
        if app_id != '' and app_secret != '':
            # 未开启API时, 安全默认应为关闭
            panel_api = thisdb.getOptionByJson('panel_api', default={"open":False})
            if panel_api and panel_api.get('open'):
                return_code = 404
                info = thisdb.getAppByAppId(app_id)

                # APP不存在
                if info is None:
                    return Response(status=int(return_code))

                # APP已被禁用
                if str(info.get('status', 0)) != '1':
                    return Response(status=int(return_code))

                # 来源IP必须在白名单内
                if not isIpInWhiteList(request.remote_addr, info.get('white_list')):
                    return Response(status=int(return_code))

                # 密钥常量时间比较
                app_secret_db = str(info.get('app_secret') or '')
                if not hmac.compare_digest(app_secret_db.encode('utf-8'),
                                           app_secret.encode('utf-8')):
                    return Response(status=int(return_code))
                return func(*args, **kwargs)

        if not isLogined():
            unauthorized_status = thisdb.getOption('unauthorized_status')
            if unauthorized_status == '0':
                return render_template('default/path.html')
            return Response(status=int(unauthorized_status))

        return func(*args, **kwargs)
    return wrapper