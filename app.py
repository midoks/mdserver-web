import sys
import io
import os

import views
from flask import Flask
from datetime import timedelta

sys.path.append("class/")

app = Flask(__name__)
app.debug = True


DEFAULT_MODULES = (
    (views.dashboard, "/"),
    (views.site, "/site"),
    (views.files, "/files"),
    (views.soft, "/soft"),
    (views.config, "/config"),
    (views.plugins, "/plugins"),
    (views.task, "/task"),
    (views.system, "/system"),
    (views.database, "/database"),
    (views.crontab, "/crontab"),
    (views.firewall, "/firewall"),
    (views.control, "/control"),
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


if __name__ == "__main__":
    app.run()
