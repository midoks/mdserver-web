# coding:utf-8

from flask import Flask
from flask import Blueprint, render_template

import sys
sys.path.append("class/")
import public


task = Blueprint('task', __name__, template_folder='templates')


@task.route("/")
def index():
    return render_template('default/site.html')


@task.route("/count")
def count():
    c = public.M('tasks').where("status!=?", ('1',)).count()
    return str(c)


@task.route("/list", methods=['GET', 'POST'])
def list():
    _list = public.M('tasks').where('', ()).field('id,name,type,status,addtime,start,end').limit(
        '0,5').order('id desc').select()
    _ret = {}
    _ret['data'] = _list

    count = public.M('tasks').where('', ()).count()
    _page = {}
    _page['count'] = count
    _page['tojs'] = 'remind'

    _ret['page'] = public.getPage(_page)
    return public.getJson(_ret)
