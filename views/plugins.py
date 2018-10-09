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


@plugins.route("/file", methods=['GET'])
def file():
    file = request.args.get('f', '')
    print file
    return jsonify({})
    # if file:
    #     print file
    # else:
    #     print "error"


@plugins.route("/list", methods=['GET', 'POST'])
def list():

    data = json.loads(public.readFile("data/type.json"))
    ret = {}
    ret["type"] = data

    plugins_info = []

    typeVal = request.args.get('type', '')
    if typeVal == "":
        typeVal = "0"

    for dirinfo in os.listdir(__plugin_name):
        path = __plugin_name + "/" + dirinfo
        if os.path.isdir(path):
            jsonFile = path + "/info.json"
            if os.path.exists(jsonFile):
                try:
                    tmp = json.loads(public.readFile(jsonFile))
                    if typeVal == "0":
                        plugins_info.append(tmp)
                    else:
                        if tmp['pid'] == typeVal:
                            plugins_info.append(tmp)
                except ValueError, Argument:
                    pass

    ret['data'] = plugins_info
    return jsonify(ret)
