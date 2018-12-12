# coding:utf-8

import sys
import io
import os
import time
import shutil

from flask import Flask
from datetime import timedelta

sys.path.append(os.getcwd() + "/class/core")
sys.setdefaultencoding('utf-8')
import db
import public


class config:
    __version = '0.0.1'
    __app = None

    def __init__(self):
        pass

    def makeApp(self, name):
        app = Flask(name)

        app.config.version = self.__version
        app.config['SECRET_KEY'] = os.urandom(24)
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

        # app.debug = True
        # app.config.version = self.__version + str(time.time())

        __app = app

        self.initDB()

        self.initInitD()
        return app

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
