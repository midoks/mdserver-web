# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import json
import time

from flask import Blueprint, render_template
from flask import request

from admin.user_login_check import panel_login_required

import core.mw as mw
import utils.task as MwTasks
import thisdb

blueprint = Blueprint('task', __name__, url_prefix='/task', template_folder='../../templates/default')


@blueprint.route('/count', endpoint='task_count',methods=['GET','POST'])
@panel_login_required
def task_count():
    return mw.returnData(True, 'ok',thisdb.getTaskUnexecutedCount())

@blueprint.route('/list', endpoint='list', methods=['POST'])
@panel_login_required
def list():
    p = request.form.get('p', '1')
    limit = request.form.get('limit', '10').strip()
    search = request.form.get('search', '').strip()
    return MwTasks.getTaskPage(int(p), int(limit))

@blueprint.route('/get_exec_log', endpoint='get_exec_log', methods=['POST'])
@panel_login_required
def get_exec_log():
    file = mw.getPanelTaskExecLog()
    return mw.getLastLine(file, 100)


@blueprint.route('/get_task_speed', endpoint='get_task_speed', methods=['POST'])
@panel_login_required
def get_task_speed():
    count = thisdb.getTaskUnexecutedCount()
    if count == 0:
        return mw.returnData(False, '当前没有任务队列在执行-2!')
    
    row = thisdb.getTaskFirstByRun()
    if row is None:
        return mw.returnData(False, '当前没有任务队列在执行-3!')

    task_logfile = mw.getPanelTaskExecLog()

    data = {}
    data['name'] = row['name']
    data['cmd'] = row['cmd']

    if row['type'] == 'download':
        readLine = ''
        for i in range(3):
            try:
                readLine = mw.readFile(task_logfile)
                data['msg'] = json.loads(readLine)
                data['isDownload'] = True
            except Exception as e:
                if i == 2:
                    thisdb.setTaskStatus(row['id'],0)
                    return mw.returnData(False, '当前没有任务队列在执行-4:' + str(e))
            time.sleep(0.5)
    else:
        data['msg'] = mw.getLastLine(task_logfile, 10)
        data['isDownload'] = False

    data['count'] = count
    data['task'] = thisdb.getTaskRunList(1,6)
    return data

@blueprint.route('/remove_task', endpoint='remove_task', methods=['POST'])
@panel_login_required
def remove_task():
    task_id = request.form.get('id', '')
    if task_id == '':
        return mw.returnData(False, '任务ID不能为空!')
    return MwTasks.removeTask(task_id)


    