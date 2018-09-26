# coding:utf-8

from flask import Flask
from flask import Blueprint,render_template
from views import dashboard,site,files,soft

# app = Flask(__name__)
# app.debug = True
#
# DEFAULT_MODULES = (
#     (dashboard, "/"),
#     (site, "/site"),
#     (files, "/files"),
#     (soft, "/soft"),
# )
#
# def setting_modules(app, modules):
#     for module, url_prefix in modules:
#         app.register_blueprint(module, url_prefix=url_prefix)
#
# setting_modules(app, DEFAULT_MODULES)

#
# if __name__ == "__main__":
#     app.run()
