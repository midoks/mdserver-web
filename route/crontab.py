# coding:utf-8

import sys
sys.path.append("/class/core")
import public

from flask import Blueprint, render_template

crontab = Blueprint('crontab', __name__, template_folder='templates')


@crontab.route("/")
def index():
    return render_template('default/crontab.html')


@crontab.route("/list", methods=['GET', 'POST'])
def list():
    data = []
    return public.getJson({})
