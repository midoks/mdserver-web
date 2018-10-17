# coding:utf-8

from flask import Blueprint, render_template

config = Blueprint('config', __name__, template_folder='templates')


@config.route("/")
def index():
    return render_template('default/config.html')
