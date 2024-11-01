# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os

from flask import Blueprint, render_template
from flask import request

from admin.model import Sites
from admin.user_login_check import panel_login_required

from utils.mwplugin import MwPlugin
import utils.site as site
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
    php_versions = site.getPhpVersion()
    php_versions = php_versions[1:]

    if len(php_versions) < 1:
        return mw.returnData(False, '未安装PHP,无法设置')

    if os.path.exists(php_bin) and os.path.islink(php_bin):
        link_re = os.readlink(php_bin)
        for v in php_versions:
            if link_re.find(v['version']) != -1:
                return mw.returnData({"select": v, "versions": php_versions})

    return mw.getJson({"select": php_versions[0],"versions": php_versions})

@blueprint.route('/set_cli_php_version', endpoint='set_cli_php_version',methods=['POST'])
@panel_login_required
def set_cli_php_version():
    if mw.isAppleSystem():
        return mw.returnData(False, "开发机不可设置!")

    version = request.form.get('version', '')

    php_bin = '/usr/bin/php'
    php_bin_src = "/www/server/php/%s/bin/php" % version
    php_ize = '/usr/bin/phpize'
    php_ize_src = "/www/server/php/%s/bin/phpize" % version
    php_fpm = '/usr/bin/php-fpm'
    php_fpm_src = "/www/server/php/%s/sbin/php-fpm" % version
    php_pecl = '/usr/bin/pecl'
    php_pecl_src = "/www/server/php/%s/bin/pecl" % version
    php_pear = '/usr/bin/pear'
    php_pear_src = "/www/server/php/%s/bin/pear" % version
    if not os.path.exists(php_bin_src):
        return mw.returnData(False, '指定PHP版本未安装!')

    is_chattr = mw.execShell('lsattr /usr|grep /usr/bin')[0].find('-i-')
    if is_chattr != -1:
        mw.execShell('chattr -i /usr/bin')
    mw.execShell("rm -f " + php_bin + ' ' + php_ize + ' ' +
                 php_fpm + ' ' + php_pecl + ' ' + php_pear)
    mw.execShell("ln -sf %s %s" % (php_bin_src, php_bin))
    mw.execShell("ln -sf %s %s" % (php_ize_src, php_ize))
    mw.execShell("ln -sf %s %s" % (php_fpm_src, php_fpm))
    mw.execShell("ln -sf %s %s" % (php_pecl_src, php_pecl))
    mw.execShell("ln -sf %s %s" % (php_pear_src, php_pear))
    if is_chattr != -1:
        mw.execShell('chattr +i /usr/bin')
    mw.writeLog('面板设置', '设置PHP-CLI版本为: %s' % version)
    return mw.returnData(True, '设置成功!')


