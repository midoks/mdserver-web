# coding:utf-8

from flask import Flask
from flask import Blueprint, render_template


task = Blueprint('task', __name__, template_folder='templates')


@task.route("/")
def index():
    return render_template('default/site.html')


@task.route("/count")
def count():
    return "0"
