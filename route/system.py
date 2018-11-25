# coding:utf-8

import time
import psutil
import os
import sys

from flask import Flask, session
from flask import Blueprint, render_template
from flask import jsonify

sys.path.append("class/core")
import public
import system_api

system = Blueprint('system', __name__, template_folder='templates')


@system.route("/network")
def network():
    data = system_api.system_api().getNetWork()
    return public.getJson(data)


@system.route("/update_panel")
def updatePanel():
    return public.returnJson(False, "12")


@system.route("/system_total")
def systemTotal():
    data = system_api.system_api().getSystemTotal()
    return public.getJson(data)


@system.route("/disk_info")
def diskInfo():
    diskInfo = system_api.system_api().getDiskInfo()
    return public.getJson(diskInfo)
