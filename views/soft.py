# coding:utf-8

from flask import Flask
from flask import Blueprint,render_template


soft = Blueprint('soft', __name__, template_folder='templates')

@soft.route("/")
def index():
    return render_template('default/soft.html')