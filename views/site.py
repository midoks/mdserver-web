# coding:utf-8

from flask import Flask
from flask import Blueprint, render_template


site = Blueprint('site', __name__, template_folder='templates')


@site.route("/")
def index():
    return render_template('default/site.html')


# @site.route("/list")
# def list():
#     SQL = public.M('site')
