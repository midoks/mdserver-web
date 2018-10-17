# coding:utf-8

from flask import Flask
from flask import Blueprint, render_template


control = Blueprint('control', __name__, template_folder='templates')


@control.route("/")
def index():
    return render_template('default/control.html')
