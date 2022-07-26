# coding:utf-8

import sys
import io
import os
import time
import json

sys.path.append(os.getcwd() + "/class/core")
import mw


app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'webstats'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


def getTaskConf():
    conf = getServerDir() + "/task_config.json"
    return conf


def migrateSiteHotLogs(site_name, query_date):
    print(site_name, query_date)
    return mw.returnMsg(True, "{} 日志合并成功！".format(site_name))


def migrateHotLogs(query_date="today"):
    print("begin migrate hot logs")
    sites = mw.M('sites').field('name').order("addtime").select()
    # print(sites)

    unset_site = {"name": "unset"}
    sites.append(unset_site)

    for site_info in sites:
        # print(site_info['name'])
        site_name = site_info["name"]
        migrate_res = migrateSiteHotLogs(site_name, query_date)
        if not migrate_res["status"]:
            print(migrate_res["msg"])
    print("end migrate hot logs")
