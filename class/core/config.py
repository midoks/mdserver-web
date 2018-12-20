# coding:utf-8

import sys
import io
import os
import time
import shutil

reload(sys)
sys.setdefaultencoding('utf8')

from flask import Flask
from datetime import timedelta

sys.path.append(os.getcwd() + "/class/core")
import db
import public


class MiddleWare:

    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, *args, **kwargs):
        # print args
        return self.wsgi_app(*args, **kwargs)


class config:
    __version = '0.0.1'
    __app = None
    __modules = None

    def __init__(self):
        pass

    def makeApp(self, name):
        app = Flask(name)
        self.__app = app

        app.config.version = self.__version
        app.config['SECRET_KEY'] = os.urandom(24)
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

        self.initDB()
        self.initInitD()
        self.initRoute()
        app.wsgi_app = MiddleWare(app.wsgi_app)
        return app

    def startDebug(self):
        app.debug = True
        app.config.version = self.__version + str(time.time())

    def initDB(self):
        try:
            sql = db.Sql().dbfile('default')
            csql = public.readFile('data/sql/default.sql')
            csql_list = csql.split(';')
            for index in range(len(csql_list)):
                sql.execute(csql_list[index], ())
        except Exception, ex:
            print str(ex)

    def initUser(self):
        pass

    def initInitD(self):
        script = public.getRunDir() + '/scripts/init.d/mw.tpl'
        script_bin = public.getRunDir() + '/scripts/init.d/mw'
        if os.path.exists(script_bin):
            return

        content = public.readFile(script)
        content = content.replace("{$SERVER_PATH}", public.getRunDir())

        public.writeFile(script_bin, content)
        public.execShell('chmod +x ' + script_bin)

        if public.getOs() != 'darwin':
            initd_bin = '/etc/init.d/mw'
            if not os.path.exists(initd_bin):
                shutil.copyfile(script_bin, initd_bin)
                public.execShell('chmod +x ' + initd_bin)

    def getVersion(self):
        return self.__version

    def getApp(self):
        return self.__app

    def initRoute(self):
        import route
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
            (route.control, "/control")
        )
        self.modules = DEFAULT_MODULES
        self.settingModules(self.__app, DEFAULT_MODULES)

    def settingModules(self, app, modules):
        for module, url_prefix in modules:
            app.register_blueprint(module, url_prefix=url_prefix)
