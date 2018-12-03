# coding:utf-8

import sys
import io
import os


sys.path.append("/class/core")
reload(sys)
sys.setdefaultencoding('utf8')

import route
import config

app = config.config().makeApp(__name__)


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


def setting_modules(app, modules):
    for module, url_prefix in modules:
        app.register_blueprint(module, url_prefix=url_prefix)

setting_modules(app, DEFAULT_MODULES)

try:
    if __name__ == "__main__":
        app.run()
except Exception as ex:
    print ex
