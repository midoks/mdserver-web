# coding:utf-8

from flask import Flask
from flask import Blueprint, render_template
from flask import request


import sys
import os
sys.path.append(os.getcwd() + "/class/core/")
import db

firewall = Blueprint('firewall', __name__, template_folder='templates')


@firewall.route("/")
def index():
    return render_template('default/firewall.html')


'''
* 取数据列表
* @param String _GET['tab'] 数据库表名
* @param Int _GET['count'] 每页的数据行数
* @param Int _GET['p'] 分页号  要取第几页数据
* @return Json  page.分页数 , count.总行数   data.取回的数据
'''


@firewall.route("/log_list", methods=['GET', 'POST'])
def log_list():
    try:
        table = request.form.get('table', '')
        data = GetSql(request.form)
        SQL = public.M(table)

        if table == 'backup':
            import os
            for i in range(len(data['data'])):
                if data['data'][i]['size'] == 0:
                    if os.path.exists(data['data'][i]['filename']):
                        data['data'][i]['size'] = os.path.getsize(
                            data['data'][i]['filename'])

        elif table == 'sites' or table == 'databases':
            type = '0'
            if table == 'databases':
                type = '1'
            for i in range(len(data['data'])):
                data['data'][i]['backup_count'] = SQL.table('backup').where(
                    "pid=? AND type=?", (data['data'][i]['id'], type)).count()
            if table == 'sites':
                for i in range(len(data['data'])):
                    data['data'][i]['domain'] = SQL.table('domain').where(
                        "pid=?", (data['data'][i]['id'],)).count()
        elif table == 'firewall':
            for i in range(len(data['data'])):
                if data['data'][i]['port'].find(':') != -1 or data['data'][i]['port'].find('.') != -1 or data['data'][i]['port'].find('-') != -1:
                    data['data'][i]['status'] = -1
                else:
                    data['data'][i]['status'] = CheckPort(
                        int(data['data'][i]['port']))

        # 返回
        return data
    except Exception as ex:
        return str(ex)

'''
 * 获取数据与分页
 * @param string table 表
 * @param string where 查询条件
 * @param int limit 每页行数
 * @param mixed result 定义分页数据结构
 * @return array
'''


def GetSql(get, result='1,2,3,4,5,8'):
    # 判断前端是否传入参数
    order = "id desc"
    if hasattr(get, 'order'):
        order = get.order

    limit = 20
    if hasattr(get, 'limit'):
        limit = int(get.limit)

    if hasattr(get, 'result'):
        result = get.result

    SQL = db.Sql()
    data = {}
    # 取查询条件
    where = ''
    if hasattr(get, 'search'):
        where = self.GetWhere(get.table, get.search)
        if get.table == 'backup':
            where += " and type='" + get.type + "'"

        if get.table == 'sites':
            pid = SQL.table('domain').where(
                'name=?', (get.search,)).getField('pid')
            if pid:
                where = "id=" + str(pid)

    field = self.GetField(get.table)
    # 实例化数据库对象

    # 是否直接返回所有列表
    if hasattr(get, 'list'):
        data = SQL.table(get.table).where(
            where, ()).field(field).order(order).select()
        return data

    # 取总行数
    count = SQL.table(get.table).where(where, ()).count()
    #get.uri = get
    # 包含分页类
    import page
    # 实例化分页类
    page = page.Page()

    info = {}
    info['count'] = count
    info['row'] = limit

    info['p'] = 1
    if hasattr(get, 'p'):
        info['p'] = int(get['p'])
    info['uri'] = get
    info['return_js'] = ''
    if hasattr(get, 'tojs'):
        info['return_js'] = get.tojs

    data['where'] = where

    # 获取分页数据
    data['page'] = page.GetPage(info, result)
    # 取出数据
    data['data'] = SQL.table(get.table).where(where, ()).order(order).field(
        field).limit(str(page.SHIFT) + ',' + str(page.ROW)).select()
    return data
