# coding:utf-8

import os
import sys
sys.path.append("class/core")
import public

from flask import Flask
from flask import Blueprint, render_template
from flask import jsonify
from flask import request


files = Blueprint('files', __name__, template_folder='templates')


@files.route("/")
def index():
    return render_template('default/files.html')


@files.route('get_body', methods=['POST'])
def getBody():
    path = request.form.get('path', '').encode('utf-8')
    if not os.path.exists(path):
        return public.returnJson(False, '文件不存在', (path,))

    if os.path.getsize(path) > 2097152:
        return public.returnJson(False, u'不能在线编辑大于2MB的文件!')

    fp = open(path, 'rb')
    data = {}
    data['status'] = True
    try:
        if fp:
            from chardet.universaldetector import UniversalDetector
            detector = UniversalDetector()
            srcBody = b""
            for line in fp.readlines():
                detector.feed(line)
                srcBody += line
            detector.close()
            char = detector.result
            data['encoding'] = char['encoding']
            if char['encoding'] == 'GB2312' or not char['encoding'] or char[
                    'encoding'] == 'TIS-620' or char['encoding'] == 'ISO-8859-9':
                data['encoding'] = 'GBK'
            if char['encoding'] == 'ascii' or char[
                    'encoding'] == 'ISO-8859-1':
                data['encoding'] = 'utf-8'
            if char['encoding'] == 'Big5':
                data['encoding'] = 'BIG5'
            if not char['encoding'] in ['GBK', 'utf-8',
                                        'BIG5']:
                data['encoding'] = 'utf-8'
            try:
                if sys.version_info[0] == 2:
                    data['data'] = srcBody.decode(
                        data['encoding']).encode('utf-8', errors='ignore')
                else:
                    data['data'] = srcBody.decode(data['encoding'])
            except:
                data['encoding'] = char['encoding']
                if sys.version_info[0] == 2:
                    data['data'] = srcBody.decode(
                        data['encoding']).encode('utf-8', errors='ignore')
                else:
                    data['data'] = srcBody.decode(data['encoding'])
        else:
            if sys.version_info[0] == 2:
                data['data'] = srcBody.decode('utf-8').encode('utf-8')
            else:
                data['data'] = srcBody.decode('utf-8')
            data['encoding'] = u'utf-8'

        return public.returnJson(True, 'OK', data)
    except Exception as ex:
        return public.returnJson(False, u'文件编码不被兼容，无法正确读取文件!' + str(ex))


@files.route('save_body', methods=['POST'])
def saveBody():
    path = request.form.get('path', '').encode('utf-8')
    data = request.form.get('data', '').encode('utf-8')
    encoding = request.form.get('encoding', '').encode('utf-8')
    if not os.path.exists(path):
        return public.returnJson(False, '文件不存在')
    try:
        if encoding == 'ascii':
            encoding = 'utf-8'
        if sys.version_info[0] == 2:
            data = data.encode(encoding, errors='ignore')
            fp = open(path, 'w+')
        else:
            data = data.encode(
                encoding, errors='ignore').decode(encoding)
            fp = open(path, 'w+', encoding=encoding)
        fp.write(data)
        fp.close()

        public.writeLog('TYPE_FILE', '文件保存成功', (path,))
        return public.returnJson(True, '文件保存成功')
    except Exception as ex:
        return public.returnJson(False, 'FILE_SAVE_ERR:' + str(ex))


@files.route('/get_dir', methods=['POST'])
def getDir():
    path = request.form.get('path', '').encode('utf-8')
    if not os.path.exists(path):
        path = '/'

    import pwd
    dirnames = []
    filenames = []

    info = {}
    info['count'] = 10
    info['row'] = 10
    info['p'] = 1
    if request.form.has_key('p'):
        info['p'] = int(request.form.get('p'))
    info['uri'] = {}
    info['return_js'] = ''
    if request.form.has_key('tojs'):
        info['return_js'] = request.form.get('tojs')
    if request.form.has_key('showRow'):
        info['row'] = int(request.form.get('showRow'))

    data = {}
    data['PAGE'] = public.getPage(info, '1,2,3,4,5,6,7,8')

    search = None
    if request.form.has_key('search'):
        search = request.form.get('search').strip().lower()
    i = 0
    n = 0
    for filename in os.listdir(path):
        if search:
            if filename.lower().find(search) == -1:
                continue
        i += 1
        if n >= 10:
            break
        if i < 0:
            continue

        try:
            filePath = (path + '/' + filename).encode('utf8')
            link = ''
            if os.path.islink(filePath):
                filePath = os.readlink(filePath)
                link = ' -> ' + filePath
                if not os.path.exists(filePath):
                    filePath = path + '/' + filePath
                if not os.path.exists(filePath):
                    continue

            stat = os.stat(filePath)
            accept = str(oct(stat.st_mode)[-3:])
            mtime = str(int(stat.st_mtime))
            user = ''
            try:
                user = pwd.getpwuid(stat.st_uid).pw_name
            except:
                user = str(stat.st_uid)
            size = str(stat.st_size)
            if os.path.isdir(filePath):
                dirnames.append(filename + ';' + size + ';' +
                                mtime + ';' + accept + ';' + user + ';' + link)
            else:
                filenames.append(filename + ';' + size + ';' +
                                 mtime + ';' + accept + ';' + user + ';' + link)
            n += 1
        except:
            continue
    data['DIR'] = sorted(dirnames)
    data['FILES'] = sorted(filenames)
    data['PATH'] = ""
    return public.getJson(data)
