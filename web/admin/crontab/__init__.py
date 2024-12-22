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

from utils.crontab import crontab as MwCrontab
import core.mw as mw
import thisdb

blueprint = Blueprint('crontab', __name__, url_prefix='/crontab', template_folder='../../templates')
@blueprint.route('/index', endpoint='index')
@panel_login_required
def index():
    name = thisdb.getOption('template', default='default')
    return render_template('%s/crontab.html' % name)

# 计划任务列表
@blueprint.route('/list', endpoint='list', methods=['POST'])
@panel_login_required
def list():
    page = request.args.get('p', '1').strip()
    limit = request.args.get('limit', '10').strip()
    return MwCrontab.instance().getCrontabList(page=int(page),size=int(limit))

# 计划任务日志
@blueprint.route('/logs', endpoint='logs', methods=['POST'])
def logs():
    cron_id = request.form.get('id', '')
    return MwCrontab.instance().cronLog(cron_id)

# 删除计划任务
@blueprint.route('/del', endpoint='del', methods=['POST'])
def crontab_del():
    cron_id = request.form.get('id', '')   
    return MwCrontab.instance().delete(cron_id)

# 删除计划任务日志
@blueprint.route('/del_logs', endpoint='del_logs', methods=['POST'])
def del_logs():
    cron_id = request.form.get('id', '')   
    return MwCrontab.instance().delLogs(cron_id)


# 设置计划任务状态
@blueprint.route('/set_cron_status', endpoint='set_cron_status', methods=['POST'])
def set_cron_status():
    cron_id = request.form.get('id', '')   
    return MwCrontab.instance().setCronStatus(cron_id)

# 设置计划任务状态
@blueprint.route('/get_data_list', endpoint='get_data_list', methods=['POST'])
def get_data_list():
    stype = request.form.get('type', '')
    return MwCrontab.instance().getDataList(stype)


# 获取计划任务
@blueprint.route('/get_crond_find', endpoint='get_crond_find', methods=['POST'])
def get_crond_find():
    cron_id = request.form.get('id', '')
    data = MwCrontab.instance().getCrondFind(cron_id)
    return data

# 修改计划任务
@blueprint.route('/modify_crond', endpoint='modify_crond', methods=['POST'])
def modify_crond():
    request_data = {}
    
    request_data['name'] = request.form.get('name', '')
    request_data['type'] = request.form.get('type', '')
    request_data['week'] = request.form.get('week', '')
    request_data['where1'] = request.form.get('where1', '')
    request_data['hour'] = request.form.get('hour', '')
    request_data['minute'] = request.form.get('minute', '')
    request_data['save'] = request.form.get('save', '')
    request_data['backup_to'] = request.form.get('backup_to', '')
    request_data['stype'] = request.form.get('stype', '')
    request_data['sname'] = request.form.get('sname', '')
    request_data['sbody'] = request.form.get('sbody', '')
    request_data['url_address'] = request.form.get('urladdress', '')
    cron_id = request.form.get('id', '')
    data = MwCrontab.instance().modifyCrond(cron_id,request_data)
    return data

# 执行计划任务
@blueprint.route('/start_task', endpoint='start_task', methods=['POST'])
def start_task():
    cron_id = request.form.get('id', '')
    return MwCrontab.instance().startTask(cron_id)

# 添加计划任务
@blueprint.route('/add', endpoint='add', methods=['POST'])
@panel_login_required
def add():
    request_data = {}
    request_data['name'] = request.form.get('name', '')
    request_data['type'] = request.form.get('type', '')
    request_data['week'] = request.form.get('week', '')
    request_data['where1'] = request.form.get('where1', '')
    request_data['hour'] = request.form.get('hour', '')
    request_data['minute'] = request.form.get('minute', '')
    request_data['save'] = request.form.get('save', '')
    request_data['backup_to'] = request.form.get('backup_to', '')
    request_data['stype'] = request.form.get('stype', '')
    request_data['sname'] = request.form.get('sname', '')
    request_data['sbody'] = request.form.get('sbody', '')
    request_data['url_address'] = request.form.get('urladdress', '')

    info = thisdb.getCronByName(request_data['name'])
    if info is not None:
        return mw.returnData(False, '任务名称重复')

    cron_id = MwCrontab.instance().add(request_data)
    if cron_id > 0:
        return mw.returnData(True, '添加成功')
    return mw.returnData(False, '添加失败')


