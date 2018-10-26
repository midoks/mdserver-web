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
