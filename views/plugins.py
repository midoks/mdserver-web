# coding:utf-8

from flask import Blueprint, render_template

plugins = Blueprint('plugins', __name__, template_folder='templates')


@plugins.route("/")
def index():
    return render_template('default/ftp.html')


@plugins.route("/list")
def list():
    pass
