# coding:utf-8

from flask import Flask
from flask import Blueprint, render_template


firewall = Blueprint('firewall', __name__, template_folder='templates')


@firewall.route("/")
def index():
    return render_template('default/firewall.html')
