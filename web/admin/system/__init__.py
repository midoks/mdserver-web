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

from admin.user_login_check import panel_login_required
import admin.model.option as option

import core.mw as mw
import utils.system as sys


blueprint = Blueprint('system', __name__, url_prefix='/system', template_folder='../../templates')

# 获取系统的统计信息
@blueprint.route('/system_total', endpoint='system_total')
@panel_login_required
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
@panel_login_required
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
@panel_login_required
def disk_info():
    data = sys.getDiskInfo()
    return data

# 获取系统的负载统计信息
@blueprint.route('/get_load_average', endpoint='get_load_average', methods=['GET'])
@panel_login_required
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
@panel_login_required
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
@panel_login_required
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
@panel_login_required
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
@panel_login_required
def set_control():
    stype = request.form.get('type', '')
    day = request.form.get('day', '')

    if stype == '0':
        option.setOption('monitor_status', 'close', type='monitor')
        return mw.returnData(True, "设置成功!")
    elif stype == '1':
        _day = int(day)
        if _day < 1:
            return mw.returnData(False, "设置失败!")
        option.setOption('monitor_day', day, type='monitor')
    elif stype == '2':
        option.setOption('monitor_only_netio', 'close', type='monitor')
        return mw.returnData(True, "设置成功!")
    elif stype == '3':
        option.setOption('monitor_only_netio', 'open', type='monitor')
        return mw.returnData(True, "设置成功!")
    elif stype == 'del':
        if not mw.isRestart():
            return mw.returnData(False, '请等待所有安装任务完成再执行')
        os.remove("data/system.db")

        sql = db.Sql().dbfile('system')
        csql = mw.readFile('data/sql/system.sql')
        csql_list = csql.split(';')
        for index in range(len(csql_list)):
            sql.execute(csql_list[index], ())
        return mw.returnData(True, "监控服务已关闭")
    else:
        monitor_status = option.getOption('monitor_status', default='open', type='monitor')
        monitor_day = option.getOption('monitor_day', default='30', type='monitor')
        monitor_only_netio = option.getOption('monitor_only_netio', default='open', type='monitor')
        data = {}
        data['day'] = monitor_day
        if monitor_status == 'open':   
            data['status'] = True
        else:
            data['status'] = False
        if monitor_only_netio == 'open':
            data['stat_all_status'] = True
        else:
            data['stat_all_status'] = False

        return data

    return mw.returnData(False, "异常!")

    


# 升级检测
@blueprint.route('/update_server', endpoint='update_server')
@panel_login_required
def update_server():
    panel_type = request.args.get('type', 'check')
    version = request.args.get('version', '')

    return mw.returnData(False, '已经是最新,无需更新!')



