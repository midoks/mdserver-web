# coding:utf-8

import sys
import io
import os

reload(sys)
sys.setdefaultencoding('utf8')

import route
from flask import Flask
from datetime import timedelta

sys.path.append("class/")

app = Flask(__name__)
app.debug = True


DEFAULT_MODULES = (
    (route.dashboard, "/"),
    (route.site, "/site"),
    (route.files, "/files"),
    (route.soft, "/soft"),
    (route.config, "/config"),
    (route.plugins, "/plugins"),
    (route.task, "/task"),
    (route.system, "/system"),
    (route.database, "/database"),
    (route.crontab, "/crontab"),
    (route.firewall, "/firewall"),
    (route.control, "/control"),
)

import time
# print "time.time(): %f " % time.time()
app.config.version = "0.0.1" + str(time.time())

app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)


def setting_modules(app, modules):
    for module, url_prefix in modules:
        app.register_blueprint(module, url_prefix=url_prefix)

setting_modules(app, DEFAULT_MODULES)

try:
    if __name__ == "__main__":
        app.run()
except Exception as ex:
    return str(ex)
