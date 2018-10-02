# coding:utf-8

from flask import Blueprint, render_template
from flask import jsonify

plugins = Blueprint('plugins', __name__, template_folder='templates')


@plugins.route("/")
def index():
    return render_template('default/ftp.html')


@plugins.route("/list")
def list():
    return jsonify({"ss": 3})
