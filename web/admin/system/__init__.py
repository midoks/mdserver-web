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

# 获取系统的统计信息
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

# 获取系统的网络流量信息
@blueprint.route('/network', endpoint='network')
def network():
    stat = {}
    stat['cpu'] = sys.getCpuInfo()
    stat['load'] = sys.getLoadAverage()
    stat['mem'] = sys.getMemInfo()
    stat['iostat'] = sys.stats().disk()
    stat['network'] = sys.stats().network()
    return stat

# 获取系统的磁盘信息
@blueprint.route('/disk_info', endpoint='disk_info')
def disk_info():
    data = sys.getDiskInfo()
    return data

# 获取系统的负载统计信息
@blueprint.route('/get_load_average', endpoint='get_load_average', methods=['GET'])
def get_load_average():
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    data = mw.M('load_average').dbPos(mw.getPanelDataDir(),'system')\
        .where("addtime>=? AND addtime<=?", (start, end,))\
        .field('id,pro,one,five,fifteen,addtime')\
        .order('id asc').select()
    # return self.toAddtime(data)
    # print(data)
    return data

# 获取系统的磁盘IO统计信息
@blueprint.route('/get_disk_io', endpoint='get_disk_io', methods=['GET'])
def get_disk_io():
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    data = mw.M('diskio').dbPos(mw.getPanelDataDir(),'system')\
        .where("addtime>=? AND addtime<=?", (start, end))\
        .field('id,read_count,write_count,read_bytes,write_bytes,read_time,write_time,addtime')\
        .order('id asc').select()
    return data

# 获取系统的CPU/IO统计信息
@blueprint.route('/get_cpu_io', endpoint='get_cpu_io', methods=['GET'])
def get_cpu_io():
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    data = mw.M('cpuio').dbPos(mw.getPanelDataDir(),'system')\
        .where("addtime>=? AND addtime<=?",(start, end))\
        .field('id,pro,mem,addtime')\
        .order('id asc').select()
    # return self.toAddtime(data)
    # print(data)
    return data


# 获取系统网络IO统计信息
@blueprint.route('/get_network_io', endpoint='get_network_io', methods=['GET'])
def get_network_io():
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    data = mw.M('network').dbPos(mw.getPanelDataDir(),'system')\
        .where("addtime>=? AND addtime<=?", (start, end))\
        .field('id,up,down,total_up,total_down,down_packets,up_packets,addtime')\
        .order('id asc').select()
    # return self.toAddtime(data)
    # print(data)
    return data

# 获取系统网络IO统计信息
@blueprint.route('/set_control', endpoint='set_control', methods=['POST'])
def set_control():
    stype = request.form.get('type', '')
    day = request.form.get('day', '')
    return mw.returnData(True, "设置成功!")


# 升级检测
@blueprint.route('/update_server', endpoint='update_server')
def update_server():
    panel_type = request.args.get('type', 'check')
    version = request.args.get('version', '')

    return mw.returnData(False, '已经是最新,无需更新!')



