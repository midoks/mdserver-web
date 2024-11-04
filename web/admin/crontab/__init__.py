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

blueprint = Blueprint('crontab', __name__, url_prefix='/crontab', template_folder='../../templates/default')
@blueprint.route('/index', endpoint='index')
def index():
    return render_template('crontab.html')

# 插件列表
@blueprint.route('/list', endpoint='list', methods=['GET','POST'])
@panel_login_required
def list():
    page = request.args.get('p', '1').strip()
    limit = request.args.get('limit', '10').strip()
    return MwCrontab.instance().getCrontabList(page=int(page),size=int(limit))

# 插件列表
@blueprint.route('/logs', endpoint='logs', methods=['GET','POST'])
def logs(self):
    sid = request.form.get('id', '')
    echo = mw.M('crontab').where("id=?", (sid,)).field('echo').find()
    logFile = mw.getServerDir() + '/cron/' + echo['echo'] + '.log'
    if not os.path.exists(logFile):
        return mw.returnData(False, '当前日志为空!')
    log = mw.getLastLine(logFile, 500)
    return mw.returnData(True, log)

# 获取计划任务
@blueprint.route('/del', endpoint='del', methods=['GET','POST'])
def crontab_del():
    task_id = request.form.get('id', '')   
    return MwCrontab.instance().delete(task_id) 

# 获取计划任务
@blueprint.route('/get_crond_find', endpoint='get_crond_find', methods=['GET','POST'])
def get_crond_find():
    sid = request.form.get('id', '')
    data = MwCrontab.instance().getCrondFind(sid)
    return data

# 添加计划任务
@blueprint.route('/add', endpoint='add', methods=['GET','POST'])
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
    request_data['backup_to'] = request.form.get('backupTo', '')
    request_data['stype'] = request.form.get('sType', '')
    request_data['sname'] = request.form.get('sName', '')
    request_data['sbody'] = request.form.get('sBody', '')
    request_data['url_address'] = request.form.get('urladdress', '')
    return MwCrontab.instance().add(request_data)


