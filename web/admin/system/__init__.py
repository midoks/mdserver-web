# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------


from flask import Blueprint, render_template
from flask import request

import core.mw as mw
import utils.system as sys

blueprint = Blueprint('system', __name__, url_prefix='/system', template_folder='../../templates')

# 取系统的统计信息
@blueprint.route('/system_total', endpoint='system_total')
def system_total():
    data = sys.getMemInfo()
    cpu = sys.getCpuInfo(interval=1)
    data['cpuNum'] = cpu[1]
    data['cpuRealUsed'] = cpu[0]
    data['time'] = sys.getBootTime()
    data['system'] = sys.getSystemVersion()
    data['version'] = '0.0.1'
    return data

# 取系统的网络流量信息
@blueprint.route('/network', endpoint='network')
def network():
    stat = {}
    stat['cpu'] = sys.getCpuInfo()
    stat['load'] = sys.getLoadAverage()
    stat['mem'] = sys.getMemInfo()
    stat['iostat'] = sys.stats().disk()
    stat['network'] = sys.stats().network()
    return stat

# 取系统的磁盘信息
@blueprint.route('/disk_info', endpoint='disk_info')
def disk_info():
    data = sys.getDiskInfo()
    return data

# 升级检测
@blueprint.route('/update_server', endpoint='update_server')
def update_server():
    panel_type = request.args.get('type', 'check')
    version = request.args.get('version', '')

    return mw.returnData(False, '已经是最新,无需更新!')



