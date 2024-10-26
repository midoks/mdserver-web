# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

from functools import wraps

def panel_login_required(func):
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # print('panel_login_required', args, kwargs)
        return func(*args, **kwargs)
    return wrapper