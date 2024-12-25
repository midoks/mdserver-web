# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os
import time
import json

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


# 粘贴内容
@blueprint.route('/batch_paste', endpoint='batch_paste', methods=['POST'])
@panel_login_required
def batch_paste():
    path = request.form.get('path', '')
    stype = request.form.get('type', '')
    return file.batchPaste(path, stype)

# 压缩文件
@blueprint.route('/zip', endpoint='zip', methods=['POST'])
@panel_login_required
def zip():
    sfile = request.form.get('sfile', '')
    dfile = request.form.get('dfile', '')
    stype = request.form.get('type', '')
    path = request.form.get('path', '')
    return file.zip(sfile, dfile, stype, path)

# 文件权限查看
@blueprint.route('/file_access', endpoint='file_access', methods=['POST'])
@panel_login_required
def file_access():
    filename = request.form.get('filename', '')
    data = file.getAccess(filename)
    data['sys_users'] = file.getSysUserList()
    return data

# 设置权限
@blueprint.route('/set_file_access', endpoint='set_file_access', methods=['POST'])
@panel_login_required
def set_file_access():
    if mw.isAppleSystem():
        return mw.returnData(True, '开发机不设置!')

    filename = request.form.get('filename', '')
    user = request.form.get('user', '')
    access = request.form.get('access', '755')
    return file.setFileAccess(filename, user, access)


# 复制文件内容
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
    search = request.form.get('search', '').strip().lower()
    search_all = request.form.get('all', '').strip().lower()
    page = request.form.get('p', '1').strip().lower()
    row = request.form.get('row', '10')
    order = request.form.get('order', '')

    if search_all == 'yes' and search != '':
        dir_list = file.getAllDirList(path, int(page), int(row), order, search)
    else:
        dir_list = file.getDirList(path, int(page), int(row), order, search)

    dir_list['page'] = mw.getPage({'p':page, 'row': row, 'tojs':'getFiles', 'count': dir_list['count']}, '1,2,3,4,5,6,7,8')
    return dir_list

# 解压ZIP
@blueprint.route('/unzip', endpoint='unzip', methods=['POST'])
@panel_login_required
def unzip():
    sfile = request.form.get('sfile', '')
    dfile = request.form.get('dfile', '')
    stype = request.form.get('type', '')
    path = request.form.get('path', '')
    return file.unzip(sfile, dfile, stype, path)

# 解压可解压文件
@blueprint.route('/uncompress', endpoint='uncompress', methods=['POST'])
@panel_login_required
def uncompress():
    sfile = request.form.get('sfile', '')
    dfile = request.form.get('dfile', '')
    path = request.form.get('path', '')
    return file.uncompress(sfile, dfile, path)

# 批量操作
@blueprint.route('/set_batch_data', endpoint='set_batch_data', methods=['POST'])
@panel_login_required
def set_batch_data():
    path = request.form.get('path', '')
    stype = request.form.get('type', '')
    access = request.form.get('access', '')
    user = request.form.get('user', '')
    data = request.form.get('data')
    return file.setBatchData(path, stype, access, user, data)

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


# 上传文件
@blueprint.route('/upload_segment', endpoint='upload_segment', methods=['POST'])
@panel_login_required
def upload_segment():
    path = request.form.get('path', '')
    name = request.form.get('name', '')
    size = request.form.get('size')
    start = request.form.get('start')
    dir_mode = request.form.get('dir_mode', '')
    file_mode = request.form.get('file_mode', '')
    b64_data = request.form.get('b64_data', '0')
    upload_files = request.files.getlist("blob")
    return file.uploadSegment(path,name,size,start,dir_mode,file_mode,b64_data,upload_files)


# 修改文件名
@blueprint.route('/mv_file', endpoint='mv_file', methods=['POST'])
@panel_login_required
def mv_file():
    sfile = request.form.get('sfile', '')
    dfile = request.form.get('dfile', '')
    return file.mvFile(sfile, dfile)

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
    size = file.getDirSizeByBash(path)
    return mw.returnData(True, size)
    # size = file.getDirSize(path)
    # return mw.returnData(True, mw.toSize(size))


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

# 下载文件
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

# 远程下载
@blueprint.route('/download_file', endpoint='download_file', methods=['POST'])
@panel_login_required
def download_file():
    url = request.form.get('url', '')
    path = request.form.get('path', '')
    filename = request.form.get('filename', '')
    
    execstr = url + '|mw|' + path + '/' + filename
    execstr = execstr.strip()

    title = '下载文件[' + filename + ']'
    thisdb.addTaskByDownload(name=title, cmd=execstr)
    # self.setFileAccept(path + '/' + filename)
    mw.triggerTask()
    return mw.returnData(True, '已将下载任务添加到队列!')

# 日志清空
@blueprint.route('/close_logs', endpoint='close_logs', methods=['POST'])
@panel_login_required
def close_logs():
    return file.closeLogs()













