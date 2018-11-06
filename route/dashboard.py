# coding:utf-8

from flask import Flask
from flask import Blueprint, render_template
from flask import jsonify
from flask import request

import psutil
import time
import os
import sys


sys.path.append(os.getcwd() + "/class/")


dashboard = Blueprint('dashboard', __name__, template_folder='templates')


@dashboard.route("/")
def index():
    return render_template('default/index.html')


@dashboard.route("/code")
def code():
    import vilidate
    vie = vilidate.vieCode()
    codeImage = vie.GetCodeImage(80, 4)
    try:
        from cStringIO import StringIO
    except:
        from StringIO import StringIO

    out = StringIO()
    print out
    codeImage[0].save(out, "png")

    return out.getvalue()


@dashboard.route("/login")
def login():
    return render_template('default/login.html')
