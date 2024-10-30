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

from functools import wraps

from admin import model
from admin import session
from admin.common import isLogined


def panel_login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not isLogined():
            unauthorized_status = model.getOption('unauthorized_status')
            if unauthorized_status == '0':
                return render_template('default/path.html')
            return Response(status=int(unauthorized_status))

        return func(*args, **kwargs)
    return wrapper