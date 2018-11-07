# coding:utf-8

from flask import Flask
from flask import Blueprint, render_template
from flask import jsonify

import os
import sys
sys.path.append("class/")
import public


files = Blueprint('files', __name__, template_folder='templates')


@files.route("/")
def index():
    return render_template('default/files.html')


@files.route("/GetDiskInfo")
def GetDiskInfo():
    return jsonify({'result': 'ok'})


@files.route('/get_exec_log', methods=['POST'])
def getExecLog():
    file = os.getcwd() + "/tmp/panelExec.log"
    v = public.getLastLine(file, 100)
    return v


@files.route('/GetExecLogs', methods=['POST'])
def GetExecLogs():
    pass
