# coding:utf-8

from flask import Blueprint, render_template
from flask import jsonify

import psutil
import time
import sys
import os


sys.path.append("class/")
import public
import json


plugins = Blueprint('plugins', __name__, template_folder='templates')

__plugin_name = "plugins"


@plugins.route("/")
def index():
    return render_template('default/ftp.html')


@plugins.route("/list")
def list():

    data = json.loads(public.readFile("data/type.json"))
    ret = {}
    ret["type"] = data

    for dirinfo in os.listdir(__plugin_name):
        path = __plugin_name + "/" + dirinfo
        if os.path.isdir(path):
            jsonFile = path + "/info.json"
            if os.path.exists(jsonFile):
                try:
                    tmp = json.loads(public.readFile(jsonFile))
                    print tmp
                except:
                    pass
        print dirinfo

    return jsonify(ret)
