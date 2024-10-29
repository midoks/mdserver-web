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

from admin import model
from admin.model import db,Tasks

import core.mw as mw

blueprint = Blueprint('task', __name__, url_prefix='/task', template_folder='../../templates/default')


@blueprint.route('/count', endpoint='task_count')
def task_count():
    return str(model.getTaskUnexecutedCount())


@blueprint.route('/list', endpoint='list', methods=['POST'])
def list():
    p = request.form.get('p', '1')
    limit = request.form.get('limit', '10').strip()
    search = request.form.get('search', '').strip()

    count = Tasks.query.filter_by().count()
    pagination = Tasks.query.filter_by().order_by(Tasks.id.desc()).paginate(page=int(p), per_page=int(limit))
  
    rows = []
    for item in pagination.items:
        t = {}
        t['id'] = item.id
        t['name'] = item.name
        t['type'] = item.type
        t['cmd'] = item.cmd
        t['start'] = item.start
        t['end'] = item.end
        t['status'] = item.status
        t['add_time'] = item.add_time
        rows.append(t)

    data = {}
    data['data'] = rows
    data['page'] = mw.getPage({'count':count,'tojs':'remind','p':p})
    return data

@blueprint.route('/get_exec_log', endpoint='get_exec_log', methods=['POST'])
def get_exec_log():
    file = mw.getPanelTaskLog()
    return mw.getLastLine(file, 100)


@blueprint.route('/get_task_speed', endpoint='get_task_speed', methods=['POST'])
def get_task_speed():
    count = model.getTaskUnexecutedCount()
    if count == 0:
        return mw.returnData(False, '当前没有任务队列在执行-2!')
    
    row = model.getTaskFirstByRun()
    if row is None:
        return mw.returnData(False, '当前没有任务队列在执行-3!')

    task_logfile = mw.getPanelTaskLog()

    data = {}
    data['name'] = row['name']
    data['cmd'] = row['cmd']

    if row['type'] == 'download':
        readLine = ""
        for i in range(3):
            try:
                readLine = mw.readFile(task_logfile)
                if len(readLine) > 10:
                    data['msg'] = json.loads(readLine)
                    data['isDownload'] = True
                    break
            except Exception as e:
                if i == 2:
                    model.setTaskStatus(row['id'],0)
                    return mw.returnData(False, '当前没有任务队列在执行-4:' + str(e))
            time.sleep(0.5)
    else:
        data['msg'] = mw.getLastLine(task_logfile, 10)
        data['isDownload'] = False


    data['task'] = model.getTaskList(status=-1)
    return data
    


    