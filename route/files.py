# coding:utf-8

from flask import Flask
from flask import Blueprint,render_template
from flask import jsonify


files = Blueprint('files', __name__, template_folder='templates')

@files.route("/")
def index():
    return render_template('default/files.html')

@files.route("/GetDiskInfo")
def GetDiskInfo():
	return jsonify({'result':'ok'})