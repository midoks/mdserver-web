# coding:utf-8

import os
import sys

from flask import Flask
from flask import Blueprint, render_template
from flask import jsonify
from flask import request
from flask import send_file, send_from_directory
from flask import make_response


sys.path.append("class/core")
import public
import file_api

files = Blueprint('files', __name__, template_folder='templates')


@files.route("/")
def index():
    return render_template('default/files.html')


@files.route('/get_body', methods=['POST'])
def getBody():
    path = request.form.get('path', '').encode('utf-8')
    return file_api.file_api().getBody(path)


@files.route('/save_body', methods=['POST'])
def saveBody():
    path = request.form.get('path', '').encode('utf-8')
    data = request.form.get('data', '').encode('utf-8')
    encoding = request.form.get('encoding', '').encode('utf-8')
    return file_api.file_api().saveBody(path, data, encoding)


@files.route('/download', methods=['GET'])
def download():
    filename = request.args.get('filename', '').encode('utf-8')
    if not os.path.exists(filename):
        return ''

    response = make_response(send_from_directory(
        os.path.dirname(filename), os.path.basename(filename), as_attachment=True))
    return response


@files.route('/zip', methods=['POST'])
def zip():
    sfile = request.form.get('sfile', '').encode('utf-8')
    dfile = request.form.get('dfile', '').encode('utf-8')
    stype = request.form.get('type', '').encode('utf-8')
    path = request.form.get('path', '').encode('utf-8')
    return file_api.file_api().zip(sfile, dfile, stype, path)


@files.route('/delete', methods=['POST'])
def delete():
    path = request.form.get('path', '').encode('utf-8')
    return file_api.file_api().delete(path)


@files.route('/file_access', methods=['POST'])
def fileAccess():
    filename = request.form.get('filename', '').encode('utf-8')
    data = file_api.file_api().getAccess(filename)
    return public.getJson(data)


@files.route('/get_dir_size', methods=['POST'])
def getDirSize():
    path = request.form.get('path', '').encode('utf-8')
    if public.getOs() == 'darwin':
        tmp = public.execShell('du -sh ' + path)
    else:
        tmp = public.execShell('du -sbh ' + path)
    # print tmp
    return public.returnJson(True, tmp[0].split()[0])


@files.route('/get_dir', methods=['POST'])
def getDir():
    path = request.form.get('path', '').encode('utf-8')
    if not os.path.exists(path):
        path = public.getRootDir() + "/wwwroot"

    search = request.args.get('search', '').strip().lower()
    page = request.args.get('p', '1').strip().lower()
    row = request.args.get('showRow', '10')

    # print path, int(page), int(row), search
    return file_api.file_api().getDir(path, int(page), int(row), search)
