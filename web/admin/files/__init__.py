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

import core.mw as mw
import utils.file as file

blueprint = Blueprint('files', __name__, url_prefix='/files', template_folder='../../templates/default')
@blueprint.route('/index', endpoint='index')
def index():
    return render_template('files.html')

# 获取文件内容
@blueprint.route('/get_body', endpoint='get_file_body', methods=['POST'])
def get_file_body():
    path = request.form.get('path', '')

    if not os.path.exists(path):
        return mw.returnData(False, '文件不存在', (path,))

    if os.path.getsize(path) > 2097152:
        return mw.returnData(False, '不能在线编辑大于2MB的文件!')

    if os.path.isdir(path):
        return mw.returnData(False, '这不是一个文件!')

    fp = open(path, 'rb')
    data = {}
    data['status'] = True
    if fp:
        srcBody = fp.read()
        fp.close()

        encoding_list = ['utf-8', 'GBK', 'BIG5']
        for el in encoding_list:
            try:
                data['encoding'] = el
                data['data'] = srcBody.decode(data['encoding'])
                break
            except Exception as ex:
                if el == 'BIG5':
                    return mw.returnData(False, '文件编码不被兼容，无法正确读取文件!' + str(ex))
    else:
        return mw.returnData(False, '文件未正常打开!')
    return mw.returnData(True, 'OK', data)

# 获取文件内容
@blueprint.route('/save_body', endpoint='save_body', methods=['POST'])
def save_body():
    path = request.form.get('path', '')
    data = request.form.get('data', '')
    encoding = request.form.get('encoding', '')
    if not os.path.exists(path):
        return mw.returnData(False, '文件不存在')
    try:
        if encoding == 'ascii':
            encoding = 'utf-8'

        data = data.encode(encoding, errors='ignore').decode(encoding)
        fp = open(path, 'w+', encoding=encoding)
        fp.write(data)
        fp.close()

        if path.find("web_conf") > 0:
            mw.restartWeb()
        # mw.writeLog('文件管理', '文件[{1}]保存成功', (path,))
        return mw.returnData(True, '文件保存成功')
    except Exception as ex:
        return mw.returnData(False, '文件保存错误:' + str(ex))

# 获取文件内容(最新行数)
@blueprint.route('/get_last_body', endpoint='get_file_last_body', methods=['POST'])
def get_file_last_body():
    path = request.form.get('path', '')
    line = request.form.get('line', '100')

    if not os.path.exists(path):
        return mw.returnData(False, '文件不存在', (path,))

    try:
        data = mw.getLastLine(path, int(line))
        return mw.returnData(True, 'OK', data)
    except Exception as ex:
        return mw.returnData(False, '无法正确读取文件!' + str(ex))


# 获取文件列表
@blueprint.route('/get_dir', endpoint='get_dir', methods=['POST'])
def get_dir():
    path = request.form.get('path', '')
    if not os.path.exists(path):
        path = mw.getFatherDir() + '/wwwroot'
    search = request.args.get('search', '').strip().lower()
    search_all = request.args.get('all', '').strip().lower()
    page = request.args.get('p', '1').strip().lower()
    row = request.args.get('row', '10')
    order = request.form.get('order', '')

    if search_all == 'yes' and search != '':
        dir_list = file.getAllDirList(path, int(page), int(row),order, search)
    else:
        dir_list = file.getDirList(path, int(page), int(row),order, search)

    dir_list['page'] = mw.getPage({'p':page, 'row': row, 'tojs':'getFiles', 'count': dir_list['count']}, '1,2,3,4,5,6,7,8')
    return dir_list













