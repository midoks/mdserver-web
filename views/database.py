# coding:utf-8

from flask import Flask
from flask import Blueprint, render_template


database = Blueprint('database', __name__, template_folder='templates')


@database.route("/")
def index():
    return render_template('default/database.html')


@database.route("/count")
def count():
    return "0"
