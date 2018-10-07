# coding:utf-8

from flask import Blueprint, render_template
from flask import jsonify
from flask import request

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


@plugins.route("/list", methods=['GET', 'POST'])
def list():

    data = json.loads(public.readFile("data/type.json"))
    ret = {}
    ret["type"] = data

    plugins_info = []

    print request.args['type']

    for dirinfo in os.listdir(__plugin_name):
        path = __plugin_name + "/" + dirinfo
        if os.path.isdir(path):
            jsonFile = path + "/info.json"
            if os.path.exists(jsonFile):
                try:
                    tmp = json.loads(public.readFile(jsonFile))
                    plugins_info.append(tmp)
                    # print tmp
                except:
                    pass
        # print dirinfo
    ret['data'] = plugins_info
    return jsonify(ret)
