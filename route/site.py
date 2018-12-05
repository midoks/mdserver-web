# coding:utf-8

import time
import sys
import os
import json

from flask import Flask
from flask import Blueprint, render_template


sys.path.append("class/core")
import public
site = Blueprint('site', __name__, template_folder='templates')


@site.route('/')
def index():
    return render_template('default/site.html')


@site.route('/list', methods=['POST'])
def list():
    _list = public.M('sites').where('', ()).field(
        'id,name,path,status,ps,addtime').limit('0,5').order('id desc').select()
    _ret = {}
    _ret['data'] = _list

    count = public.M('sites').where('', ()).count()
    _page = {}
    _page['count'] = count
    _page['tojs'] = 'getWeb'

    _ret['page'] = public.getPage(_page)
    return public.getJson(_ret)
