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
from flask import make_response
from flask import send_file
from flask import send_from_directory

from werkzeug.utils import secure_filename

from admin.user_login_check import panel_login_required
from admin import session

import core.mw as mw
import utils.file as file
import thisdb

blueprint = Blueprint('files', __name__, url_prefix='/files', template_folder='../../templates')
@blueprint.route('/index', endpoint='index')
@panel_login_required
def index():
    name = thisdb.getOption('template', default='default')
    return render_template('%s/files.html' % name)

# 获取文件内容
@blueprint.route('/check_exists_files', endpoint='check_exists_files', methods=['POST'])
@panel_login_required
def check_exists_files():
    dfile = request.form.get('dfile', '')
    filename = request.form.get('filename', '')
    data = []
    filesx = []
    if filename == '':
        filesx = json.loads(session['selected']['data'])
    else:
        filesx.append(filename)

    for fn in filesx:
        if fn == '.':
            continue
        filename = dfile + '/' + fn
        if os.path.exists(filename):
            tmp = {}
            stat = os.stat(filename)
            tmp['filename'] = fn
            tmp['size'] = os.path.getsize(filename)
            tmp['mtime'] = str(int(stat.st_mtime))
            data.append(tmp)
    return mw.returnData(True, 'ok', data)

# 获取文件内容
@blueprint.route('/copy_file', endpoint='copy_file', methods=['POST'])
@panel_login_required
def copy_file():
    sfile = request.form.get('sfile', '')
    dfile = request.form.get('dfile', '')
    return file.copyFile(sfile, dfile)

# 获取文件内容
@blueprint.route('/get_body', endpoint='get_body', methods=['POST'])
@panel_login_required
def get_body():
    path = request.form.get('path', '')
    return file.getFileBody(path)

# 获取文件内容
@blueprint.route('/save_body', endpoint='save_body', methods=['POST'])
@panel_login_required
def save_body():
    path = request.form.get('path', '')
    data = request.form.get('data', '')
    encoding = request.form.get('encoding', '')
    return file.saveBody(path,data,encoding)

# 获取文件内容(最新行数)
@blueprint.route('/get_last_body', endpoint='get_file_last_body', methods=['POST'])
@panel_login_required
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
@panel_login_required
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


# 上传文件
@blueprint.route('/upload_file', endpoint='upload_file', methods=['POST'])
@panel_login_required
def upload_file():
    path = request.args.get('path', '')
    if not os.path.exists(path):
        os.makedirs(path)
    f = request.files['zunfile']
    filename = os.path.join(path, f.filename)

    s_path = path
    if os.path.exists(filename):
        s_path = filename
    p_stat = os.stat(s_path)

    # print(filename)
    f.save(filename)
    os.chown(filename, p_stat.st_uid, p_stat.st_gid)
    os.chmod(filename, p_stat.st_mode)

    msg = mw.getInfo('上传文件[{1}] 到 [{2}]成功!', (filename, path))
    mw.writeLog('文件管理', msg)
    return mw.returnData(True, '上传成功!')

# 创建文件
@blueprint.route('/create_file', endpoint='create_file', methods=['POST'])
@panel_login_required
def create_file():
    path = request.form.get('path', '')
    return file.createFile(path)


# 创建目录
@blueprint.route('/create_dir', endpoint='create_dir', methods=['POST'])
@panel_login_required
def create_dir():
    path = request.form.get('path', '')
    return file.createDir(path)


# 获取站点日志目录
@blueprint.route('/get_dir_size', endpoint='get_dir_size', methods=['POST'])
@panel_login_required
def get_dir_size():
    path = request.form.get('path', '')
    size = file.getDirSize(path)
    return mw.returnData(True, mw.toSize(size))


# 删除文件
@blueprint.route('/delete', endpoint='delete', methods=['POST'])
@panel_login_required
def delete():
    path = request.form.get('path', '')
    return file.fileDelete(path)


# 删除文件
@blueprint.route('/delete_dir', endpoint='delete_dir', methods=['POST'])
@panel_login_required
def delete_dir():
    path = request.form.get('path', '')
    return file.dirDelete(path)

# 删除文件
@blueprint.route('/download', endpoint='download', methods=['GET'])
@panel_login_required
def download():
    filename = request.args.get('filename', '')
    if not os.path.exists(filename):
        return ''
    is_attachment = True
    if filename.endswith(".svg"):
        is_attachment = False

    response = make_response(send_from_directory(os.path.dirname(filename), os.path.basename(filename), as_attachment=is_attachment))
    return response

# 日志清空
@blueprint.route('/close_logs', endpoint='close_logs', methods=['POST'])
@panel_login_required
def close_logs():
    return file.closeLogs()













