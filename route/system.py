# coding:utf-8

import time
import psutil
import os
import sys

from flask import Flask, session
from flask import Blueprint, render_template
from flask import jsonify
from flask import request

sys.path.append("class/core")
import public
import system_api

system = Blueprint('system', __name__, template_folder='templates')


@system.route("/network")
def network():
    data = system_api.system_api().getNetWork()
    return public.getJson(data)


@system.route("/update_server")
def updateServer():
    stype = request.args.get('type', 'check')
    version = request.args.get('version', '')
    data = system_api.system_api().updateServer(stype, version)
    return data


@system.route("/system_total")
def systemTotal():
    data = system_api.system_api().getSystemTotal()
    return public.getJson(data)


@system.route("/disk_info")
def diskInfo():
    diskInfo = system_api.system_api().getDiskInfo()
    return public.getJson(diskInfo)


@system.route('/set_control', methods=['POST'])
def setControl():
    stype = request.form.get('type', '')
    day = request.form.get('day', '')
    data = system_api.system_api().setControl(stype, day)
    return data


@system.route('/get_load_average', methods=['GET'])
def getLoadAverage():
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    data = system_api.system_api().getLoadAverageData(start, end)
    return public.getJson(data)


@system.route('/get_cpu_io', methods=['GET'])
def getCpuIo():
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    data = system_api.system_api().getCpuIoData(start, end)
    return public.getJson(data)


@system.route('/get_disk_io', methods=['GET'])
def getDiskIo():
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    data = system_api.system_api().getDiskIoData(start, end)
    return public.getJson(data)


@system.route('/get_network_io', methods=['GET'])
def getNetworkIo():
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    data = system_api.system_api().getNetWorkIoData(start, end)
    return public.getJson(data)
