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

from admin.user_login_check import panel_login_required

from utils.plugin import plugin as MwPlugin
from utils.site import sites as MwSites
import core.mw as mw
import thisdb

blueprint = Blueprint('site', __name__, url_prefix='/site', template_folder='../../templates/default')
@blueprint.route('/index', endpoint='index')
@panel_login_required
def index():
    return render_template('site.html')

# 站点列表
@blueprint.route('/list', endpoint='list', methods=['GET','POST'])
@panel_login_required
def list():
    p = request.form.get('p', '1')
    limit = request.form.get('limit', '10')
    type_id = request.form.get('type_id', '0').strip()
    search = request.form.get('search', '').strip()
    order = request.form.get('order', '').strip()

    info = thisdb.getSitesList(page=int(p),size=int(limit),type_id=int(type_id), search=search,order=order)

    data = {}
    data['data'] = info['list']
    data['page'] = mw.getPage({'count':info['count'],'tojs':'getWeb','p':p, 'row':limit})
    return data

# 添加站点
@blueprint.route('/add', endpoint='add',methods=['POST'])
@panel_login_required
def add():
    webinfo = request.form.get('webinfo', '')
    ps = request.form.get('ps', '')
    path = request.form.get('path', '')
    version = request.form.get('version', '')
    port = request.form.get('port', '')
    return MwSites.instance().add(webinfo, port, ps, path, version)

# 站点停止
@blueprint.route('/stop', endpoint='stop',methods=['POST'])
@panel_login_required
def stop():
    site_id = request.form.get('id', '')
    return MwSites.instance().stop(site_id)

# 站点开启
@blueprint.route('/start', endpoint='start',methods=['POST'])
@panel_login_required
def start():
    site_id = request.form.get('id', '')
    return MwSites.instance().start(site_id)

# 添加站点 - 域名
@blueprint.route('/add_domain', endpoint='add_domain',methods=['POST'])
@panel_login_required
def add_domain():
    domain = request.form.get('domain', '')
    site_name = request.form.get('site_name', '')
    site_id = request.form.get('id', '')
    return MwSites.instance().addDomain(site_id, site_name, domain)

# 删除站点 - 域名
@blueprint.route('/del_domain', endpoint='del_domain',methods=['POST'])
@panel_login_required
def del_domain():
    site_name = request.form.get('site_name', '')
    site_id = request.form.get('id', '')
    domain = request.form.get('domain', '')
    port = request.form.get('port', '')
    return MwSites.instance().delDomain(site_id, site_name, domain, port)

# 站点删除
@blueprint.route('/delete', endpoint='delete',methods=['POST'])
@panel_login_required
def delete():
    site_id = request.form.get('id', '')
    path = request.form.get('path', '')
    return MwSites.instance().delete(site_id, path)

# 获取站点根目录
@blueprint.route('/get_root_dir', endpoint='get_root_dir',methods=['POST'])
@panel_login_required
def get_root_dir():
    data = {}
    data['dir'] = mw.getWwwDir()
    return data

# 获取站点默认文档
@blueprint.route('/get_index', endpoint='get_index',methods=['POST'])
@panel_login_required
def get_index():
    site_id = request.form.get('id', '')
    data = {}
    index = MwSites.instance().getIndex(site_id)
    data['index'] = index
    return data

# 获取站点默认文档
@blueprint.route('/set_index', endpoint='set_index',methods=['POST'])
@panel_login_required
def set_index():
    site_id = request.form.get('id', '')
    index = request.form.get('index', '')
    return MwSites.instance().setIndex(site_id, index)

# 获取站点默认文档
@blueprint.route('/get_limit_net', endpoint='get_limit_net',methods=['POST'])
@panel_login_required
def get_limit_net():
    site_id = request.form.get('id', '')
    return  MwSites.instance().getLimitNet(site_id)

# 获取站点默认文档
@blueprint.route('/set_limit_net', endpoint='set_limit_net',methods=['POST'])
@panel_login_required
def set_limit_net():
    site_id = request.form.get('id', '')
    perserver = request.form.get('perserver', '')
    perip = request.form.get('perip', '')
    limit_rate = request.form.get('limit_rate', '')
    return MwSites.instance().setLimitNet(site_id, perserver,perip,limit_rate)

# 获取站点默认文档
@blueprint.route('/close_limit_net', endpoint='close_limit_net',methods=['POST'])
@panel_login_required
def close_limit_net():
    site_id = request.form.get('id', '')
    return  MwSites.instance().closeLimitNet(site_id)

# 获取站点配置
@blueprint.route('/get_host_conf', endpoint='get_host_conf',methods=['POST'])
@panel_login_required
def get_host_conf():
    siteName = request.form.get('siteName', '')      
    host = MwSites.instance().getHostConf(siteName)
    return {'host': host}

# 设置站点配置
@blueprint.route('/save_host_conf', endpoint='save_host_conf',methods=['POST'])
@panel_login_required
def save_host_conf():
    path = request.form.get('path', '')
    data = request.form.get('data', '')
    encoding = request.form.get('encoding', '')
    return MwSites.instance().saveHostConf(path,data,encoding)

# 获取站点PHP版本
@blueprint.route('/get_site_php_version', endpoint='get_site_php_version',methods=['POST'])
@panel_login_required
def get_site_php_version():
    siteName = request.form.get('siteName', '')      
    return MwSites.instance().getSitePhpVersion(siteName)

# 获取站点PHP版本
@blueprint.route('/get_site_domains', endpoint='get_site_domains',methods=['POST'])
@panel_login_required
def get_site_domains():
    site_id = request.form.get('id', '')
    data = thisdb.getSitesDomainById(site_id)
    return mw.returnData(True, 'OK', data)

# 设置站点PHP版本
@blueprint.route('/set_php_version', endpoint='set_php_version',methods=['POST'])
@panel_login_required
def set_php_version():
    siteName = request.form.get('siteName', '')
    version = request.form.get('version', '') 
    return MwSites.instance().setPhpVersion(siteName,version)

# 检查OpenResty安装/启动状态
@blueprint.route('/check_web_status', endpoint='check_web_status',methods=['POST'])
@panel_login_required
def check_web_status():
    '''
    创建站点检查web服务
    '''
    if not mw.isInstalledWeb():
        return mw.returnJson(False, '请安装并启动OpenResty服务!')

    # 这个快点
    pid = mw.getServerDir() + '/openresty/nginx/logs/nginx.pid'
    if not os.path.exists(pid):
        return mw.returnData(False, '请启动OpenResty服务!')
    return mw.returnData(True, 'OK')

# 获取PHP版本
@blueprint.route('/get_php_version', endpoint='get_php_version',methods=['POST'])
@panel_login_required
def get_php_version():
    return MwSites.instance().getPhpVersion()

# 设置网站到期
@blueprint.route('/set_end_date', endpoint='set_end_date',methods=['POST'])
@panel_login_required
def set_end_date():
    site_id = request.form.get('id', '')
    edate = request.form.get('edate', '')
    return MwSites.instance().setEndDate(site_id, edate)


# 设置网站备注
@blueprint.route('/set_ps', endpoint='set_ps',methods=['POST'])
@panel_login_required
def set_ps():
    site_id = request.form.get('id', '')
    ps = request.form.get('ps', '')
    return MwSites.instance().setPs(site_id, ps)

# 站点绑定域名
@blueprint.route('/get_domain', endpoint='get_domain',methods=['POST'])
@panel_login_required
def get_domain():
    site_id = request.form.get('pid', '')
    return MwSites.instance().getDomain(site_id)

# 获取默认为静态列表
@blueprint.route('/get_rewrite_list', endpoint='get_rewrite_list',methods=['POST'])
@panel_login_required
def get_rewrite_list():
    return MwSites.instance().getRewriteList()

# 获取站点Rewrite配置
@blueprint.route('/get_rewrite_conf', endpoint='get_rewrite_conf',methods=['POST'])
@panel_login_required
def get_rewrite_conf():
    siteName = request.form.get('siteName', '')
    rewrite = MwSites.instance().getRewriteConf(siteName)
    return {'rewrite': rewrite}

# 获取Rewrite模版名
@blueprint.route('/get_rewrite_tpl', endpoint='get_rewrite_tpl',methods=['POST'])
@panel_login_required
def get_rewrite_tpl():
    tplname = request.form.get('tplname', '')
    return MwSites.instance().getRewriteTpl(tplname)

# 设置站点Rewrite
@blueprint.route('/set_rewrite', endpoint='set_rewrite',methods=['POST'])
@panel_login_required
def set_rewrite():
    data = request.form.get('data', '')
    path = request.form.get('path', '')
    encoding = request.form.get('encoding', '')
    return MwSites.instance().setRewrite(path,data,encoding)


# 设置Rewrite模版名
@blueprint.route('/set_rewrite_tpl', endpoint='set_rewrite_tpl',methods=['POST'])
@panel_login_required
def set_rewrite_tpl():
    name = request.form.get('name', '')
    data = request.form.get('data', '')
    return MwSites.instance().setRewriteTpl(name,data)

# 网站日志开关
@blueprint.route('/logs_open', endpoint='logs_open',methods=['POST'])
@panel_login_required
def logs_open():
    site_id = request.form.get('id', '')
    return MwSites.instance().logsOpen(site_id)

# 设置网站路径
@blueprint.route('/set_path', endpoint='set_path',methods=['POST'])
@panel_login_required
def set_path():
    site_id = request.form.get('id', '')
    path = request.form.get('path', '')
    return MwSites.instance().setSitePath(site_id, path)


# 设置网站路径
@blueprint.route('/set_site_run_path', endpoint='set_site_run_path',methods=['POST'])
@panel_login_required
def set_site_run_path():
    site_id = request.form.get('id', '')
    run_path = request.form.get('run_path', '')
    return MwSites.instance().setSiteRunPath(site_id, run_path)


# 设置网站 - 开启密码访问
@blueprint.route('/set_has_pwd', endpoint='set_has_pwd',methods=['POST'])
@panel_login_required
def set_has_pwd():
    site_id = request.form.get('id', '')
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    return MwSites.instance().setHasPwd(site_id, username, password)

# 设置网站 - 关闭密码访问
@blueprint.route('/close_has_pwd', endpoint='close_has_pwd',methods=['POST'])
@panel_login_required
def close_has_pwd():
    site_id = request.form.get('id', '')
    return MwSites.instance().closeHasPwd(site_id)

# 获取防盗链信息
@blueprint.route('/get_security', endpoint='get_security',methods=['POST'])
@panel_login_required
def get_security():
    site_id = request.form.get('id', '')
    return MwSites.instance().getSecurity(site_id)

# 设置防盗链
@blueprint.route('/set_security', endpoint='set_security',methods=['POST'])
@panel_login_required
def set_security():
    fix = request.form.get('fix', '')
    domains = request.form.get('domains', '')
    status = request.form.get('status', '')
    name = request.form.get('name', '')
    none = request.form.get('none', '')
    site_id = request.form.get('id', '')
    return MwSites.instance().setSecurity(site_id, fix, domains, status, none)


# 设置默认网站信息
@blueprint.route('/get_default_site', endpoint='get_default_site',methods=['POST'])
@panel_login_required
def get_default_site():
    return MwSites.instance().getDefaultSite()

# 设置默认站
@blueprint.route('/set_default_site', endpoint='set_default_site',methods=['POST'])
@panel_login_required
def set_default_site():
    name = request.form.get('name', '')
    return MwSites.instance().setDefaultSite(name)



