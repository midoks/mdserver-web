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

from admin.model import Sites
from admin.user_login_check import panel_login_required

from utils.mwplugin import MwPlugin
import core.mw as mw

blueprint = Blueprint('site', __name__, url_prefix='/site', template_folder='../../templates/default')
@blueprint.route('/index', endpoint='index')
def index():
    return render_template('site.html')

# 插件列表
@blueprint.route('/list', endpoint='list', methods=['GET','POST'])
@panel_login_required
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
@panel_login_required
def get_site_types():
    return []

@blueprint.route('/get_cli_php_version', endpoint='get_cli_php_version',methods=['POST'])
@panel_login_required
def get_cli_php_version():
    php_dir = mw.getServerDir() + '/php'
    if not os.path.exists(php_dir):
        return mw.returnData(False, '未安装PHP,无法设置')

    php_bin = '/usr/bin/php'
    php_versions = self.getPhpVersion()
    php_versions = php_versions[1:]

    if len(php_versions) < 1:
        return mw.returnData(False, '未安装PHP,无法设置')

    if os.path.exists(php_bin) and os.path.islink(php_bin):
        link_re = os.readlink(php_bin)
        for v in php_versions:
            if link_re.find(v['version']) != -1:
                return mw.returnData({"select": v, "versions": php_versions})

    return mw.getJson({"select": php_versions[0],"versions": php_versions})