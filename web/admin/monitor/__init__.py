# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------


import time

from flask import Blueprint, render_template
from flask import request

from admin.user_login_check import panel_login_required

import core.mw as mw
import utils.system as sys

import thisdb

blueprint = Blueprint('monitor', __name__, url_prefix='/monitor', template_folder='../../templates')
@blueprint.route('/index', endpoint='index')
@panel_login_required
def index():
    name = thisdb.getOption('template', default='default')
    return render_template('%s/monitor.html' % name)


def _parse_range(range_key):
    mapping = {
        '1h': 3600,
        '24h': 86400,
        '7d': 7 * 86400,
        '30d': 30 * 86400,
    }
    seconds = mapping.get(range_key, 86400)
    end_time = int(time.time())
    start_time = end_time - seconds
    return start_time, end_time

def _to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_num_or_none(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _build_series(start_time, end_time):
    load_data = sys.getLoadAverageByDB(start_time, end_time)
    cpu_data = sys.getCpuIoByDB(start_time, end_time)
    disk_data = sys.getDiskIoByDB(start_time, end_time)
    net_data = sys.getNetworkIoByDB(start_time, end_time)

    def _to_float(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    series = {
        'load': {
            'labels': [item['addtime'] for item in load_data],
            'one': [_to_float(item.get('one')) for item in load_data],
            'five': [_to_float(item.get('five')) for item in load_data],
            'fifteen': [_to_float(item.get('fifteen')) for item in load_data],
        },
        'cpu': {
            'labels': [item['addtime'] for item in cpu_data],
            'cpu': [_to_float(item.get('pro')) for item in cpu_data],
            'mem': [_to_float(item.get('mem')) for item in cpu_data],
        },
        'disk': {
            'labels': [item['addtime'] for item in disk_data],
            'read': [round(_to_float(item.get('read_bytes')) / (1024 * 1024), 2) for item in disk_data],
            'write': [round(_to_float(item.get('write_bytes')) / (1024 * 1024), 2) for item in disk_data],
        },
        'net': {
            'labels': [item['addtime'] for item in net_data],
            'up': [round((_to_float(item.get('up')) * 8) / 1024, 2) for item in net_data],
            'down': [round((_to_float(item.get('down')) * 8) / 1024, 2) for item in net_data],
        },
    }
    return series, load_data, cpu_data, disk_data, net_data


def _is_monitor_open():
    monitor_status = thisdb.getOption('monitor_status', default='open', type='monitor')
    return monitor_status == 'open'


def _should_collect_sample(load_data, cpu_data, disk_data, net_data):
    return not (load_data or cpu_data or disk_data or net_data)


def _safe_latest(data, key):
    if not data:
        return None
    return _to_num_or_none(data[-1].get(key))


def _safe_peak(data, key, extra=None):
    if not data:
        return None
    if extra:
        values = [extra(item) for item in data]
    else:
        values = [_to_num_or_none(item.get(key)) for item in data]

    values = [v for v in values if v is not None]
    if not values:
        return None
    return max(values)


@blueprint.route('/api/overview', endpoint='api_overview', methods=['GET'])
@panel_login_required
def api_overview():
    range_key = request.args.get('range', '24h')
    start_time, end_time = _parse_range(range_key)

    series, load_data, cpu_data, disk_data, net_data = _build_series(start_time, end_time)
    if _should_collect_sample(load_data, cpu_data, disk_data, net_data) and _is_monitor_open():
        # 监控未采样或采样任务异常时，页面会出现空图。这里主动补采样并容错，避免接口直接报错。
        try:
            sys.monitor.instance().run()
        except Exception:
            pass
        series, load_data, cpu_data, disk_data, net_data = _build_series(start_time, end_time)

    latest_net = None
    if net_data:
        latest_net = max(float(net_data[-1].get('up', 0)), float(net_data[-1].get('down', 0)))
    latest_disk = None
    if disk_data:
        latest_disk = float(disk_data[-1].get('read_bytes', 0)) + float(disk_data[-1].get('write_bytes', 0))

    summary = {
        'cpu': {
            'latest': _safe_latest(cpu_data, 'pro'),
            'peak': _safe_peak(cpu_data, 'pro'),
        },
        'mem': {
            'latest': _safe_latest(cpu_data, 'mem'),
            'peak': _safe_peak(cpu_data, 'mem'),
        },
        'net': {
            'latest': latest_net,
            'peak': _safe_peak(net_data, 'up', lambda item: max(float(item.get('up', 0)), float(item.get('down', 0)))),
        },
        'disk': {
            'latest': latest_disk,
            'peak': _safe_peak(disk_data, 'read_bytes', lambda item: float(item.get('read_bytes', 0)) + float(item.get('write_bytes', 0))),
        },
        'load': {
            'latest': _safe_latest(load_data, 'one'),
            'peak': _safe_peak(load_data, 'one'),
        },
    }

    events = []
    if cpu_data:
        top_cpu = max(cpu_data, key=lambda item: _to_float(item.get('pro')))
        top_cpu_val = round(_to_float(top_cpu.get('pro')), 2)
        events.append({'title': f"CPU 峰值 {top_cpu_val}%", 'time': top_cpu['addtime']})
    if cpu_data:
        top_mem = max(cpu_data, key=lambda item: _to_float(item.get('mem')))
        top_mem_val = round(_to_float(top_mem.get('mem')), 2)
        events.append({'title': f"内存峰值 {top_mem_val}%", 'time': top_mem['addtime']})
    if net_data:
        top_net = max(net_data, key=lambda item: max(float(item.get('up', 0)), float(item.get('down', 0))))
        events.append({'title': f"网络峰值 {round((max(float(top_net.get('up', 0)), float(top_net.get('down', 0))) * 8) / 1024, 2)} Mbps", 'time': top_net['addtime']})
    if disk_data:
        top_disk = max(disk_data, key=lambda item: float(item.get('read_bytes', 0)) + float(item.get('write_bytes', 0)))
        total_mb = round((float(top_disk.get('read_bytes', 0)) + float(top_disk.get('write_bytes', 0))) / (1024 * 1024), 2)
        events.append({'title': f"磁盘 IO 峰值 {total_mb} MB", 'time': top_disk['addtime']})

    data = {
        'range': {
            'start': start_time,
            'end': end_time,
            'key': range_key,
        },
        'summary': summary,
        'events': events,
        'series': series,
    }
    return mw.returnData(True, 'ok', data)
