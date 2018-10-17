# coding:utf-8

from flask import Blueprint, render_template

crontab = Blueprint('crontab', __name__, template_folder='templates')


@crontab.route("/")
def index():
    return render_template('default/crontab.html')
