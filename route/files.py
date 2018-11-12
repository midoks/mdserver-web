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
