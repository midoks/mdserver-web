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

from utils.mwplugin import MwPlugin

import core.mw as mw
from admin.model import Sites

blueprint = Blueprint('site', __name__, url_prefix='/site', template_folder='../../templates/default')
@blueprint.route('/index', endpoint='index')
def index():
    return render_template('site.html')

# 插件列表
@blueprint.route('/list', endpoint='list', methods=['GET','POST'])
def list():
    p = request.form.get('p', '1')
    limit = request.form.get('limit', '10')
    type_id = request.form.get('type_id', '0').strip()
    search = request.form.get('search', '').strip()

    count = Sites.query.count()
    pagination = Sites.query.paginate(page=int(p), per_page=int(limit))

    site_list = []
    for item in pagination.items:
        t = {}
        t['id'] = item.id
        t['name'] = item.name
        t['path'] = item.path
        t['index'] = item.index
        t['ps'] = item.ps
        t['edate'] = item.edate
        t['type_id'] = item.type_id
        t['status'] = item.status
        t['add_time'] = item.add_time
        t['update_time'] = item.update_time
        site_list.append(t)

    data = {}
    data['data'] = site_list
    data['page'] = mw.getPage({'count':count,'tojs':'getWeb','p':p, 'row':limit})

    return data

@blueprint.route('/get_site_types', endpoint='get_site_types',methods=['POST'])
def get_site_types():
    return []