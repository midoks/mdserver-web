# coding:utf-8

import sys
import io
import os
import time
import subprocess

sys.path.append(os.getcwd() + "/class/core")
import public


app_debug = False
if public.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'op_firewall'


def getPluginDir():
    return public.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return public.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getArgs():
    args = sys.argv[2:]
    tmp = {}
    args_len = len(args)

    if args_len == 1:
        t = args[0].strip('{').strip('}')
        t = t.split(':')
        tmp[t[0]] = t[1]
    elif args_len > 1:
        for i in range(len(args)):
            t = args[i].split(':')
            tmp[t[0]] = t[1]

    return tmp


def getConf():
    path = public.getServerDir() + "/openresty/nginx/conf/nginx.conf"
    return path


def status():
    path = getConf()
    if not os.path.exists(path):
        return 'stop'

    conf = public.readFile(path)
    if conf.find("#include luawaf.conf;") != -1:
        return 'stop'
    if conf.find("luawaf.conf;") == -1:
        return 'stop'
    return 'start'


def contentReplace(content):
    service_path = public.getServerDir()
    waf_path = public.getServerDir() + "/openresty/nginx/conf/waf"
    content = content.replace('{$ROOT_PATH}', public.getRootDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$WAF_PATH}', waf_path)
    return content


def initDreplace():
    path = public.getServerDir() + "/openresty/nginx/conf"
    if not os.path.exists(path + '/waf'):
        sdir = getPluginDir() + '/waf'
        cmd = 'cp -rf ' + sdir + ' ' + path
        public.execShell(cmd)

    config = public.getServerDir() + "/openresty/nginx/conf/waf/config.lua"
    content = public.readFile(config)
    content = contentReplace(content)
    public.writeFile(config, content)

    waf_conf = public.getServerDir() + "/openresty/nginx/conf/luawaf.conf"
    waf_tpl = getPluginDir() + "/conf/luawaf.conf"
    content = public.readFile(waf_tpl)
    content = contentReplace(content)
    public.writeFile(waf_conf, content)


def start():
    initDreplace()

    path = getConf()
    conf = public.readFile(path)
    conf = conf.replace('#include luawaf.conf;', "include luawaf.conf;")

    public.writeFile(path, conf)
    public.restartWeb()
    return 'ok'


def stop():
    initDreplace()

    path = getConf()
    conf = public.readFile(path)
    conf = conf.replace('include luawaf.conf;', "#include luawaf.conf;")

    public.writeFile(path, conf)
    public.restartWeb()
    return 'ok'


def restart():
    return 'ok'


def reload():
    return 'ok'


if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print status()
    elif func == 'start':
        print start()
    elif func == 'stop':
        print stop()
    elif func == 'restart':
        print restart()
    elif func == 'reload':
        print reload()
    elif func == 'conf':
        print getConf()
    else:
        print 'error'
