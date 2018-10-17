# coding:utf-8

from flask import Flask
from flask import Blueprint, render_template
from flask import jsonify
import psutil
import time


dashboard = Blueprint('dashboard', __name__, template_folder='templates')


@dashboard.route("/")
def index():
    return render_template('default/index.html')
