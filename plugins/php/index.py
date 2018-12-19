# coding:utf-8

import sys
import io
import os
import time
import re
import json
import shutil

reload(sys)
sys.setdefaultencoding('utf8')

sys.path.append(os.getcwd() + "/class/core")
import public

app_debug = False
if public.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'php'


def getPluginDir():
    return public.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return public.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getArgs():
    args = sys.argv[3:]
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


def getConf(version):
    path = getServerDir() + '/' + version + '/etc/php.ini'
    return path


def status(version):
    cmd = "ps -ef|grep 'php/" + version + \
        "' |grep -v grep | grep -v python | awk '{print $2}'"
    data = public.execShell(cmd)
    if data[0] == '':
        return 'stop'
    return 'start'


def contentReplace(content, version):
    service_path = public.getServerDir()
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$PHP_VERSION}', version)

    if public.isAppleSystem():
        # user = public.execShell(
        #     "who | sed -n '2, 1p' |awk '{print $1}'")[0].strip()
        content = content.replace('{$PHP_USER}', 'nobody')
        content = content.replace('{$PHP_GROUP}', 'nobody')

        rep = 'user\s*=\s*(.+)\r?\n'
        val = ';user = nobody\n'
        content = re.sub(rep, val, content)

        rep = 'group\s*=\s*(.+)\r?\n'
        val = ';group = nobody\n'
        content = re.sub(rep, val, content)
    else:
        content = content.replace('{$PHP_USER}', 'www')
        content = content.replace('{$PHP_GROUP}', 'www')
    return content


def makeOpenrestyConf():
    if public.isInstalledWeb():
        d_pathinfo = public.getServerDir() + '/openresty/nginx/conf/pathinfo.conf'
        if not os.path.exists(d_pathinfo):
            s_pathinfo = getPluginDir() + '/conf/pathinfo.conf'
            shutil.copyfile(s_pathinfo, d_pathinfo)

        info = getPluginDir() + '/info.json'
        content = public.readFile(info)
        content = json.loads(content)
        versions = content['versions']
        tpl = getPluginDir() + '/conf/enable-php.conf'
        tpl_content = public.readFile(tpl)
        for x in range(len(versions)):
            desc_file = public.getServerDir() + '/openresty/nginx/conf/enable-php-' + \
                versions[x] + '.conf'
            if not os.path.exists(desc_file):
                w_content = contentReplace(tpl_content, versions[x])
                public.writeFile(desc_file, w_content)


def phpFpmReplace(version):
    desc_php_fpm = getServerDir() + '/' + version + '/etc/php-fpm.conf'
    if not os.path.exists(desc_php_fpm):
        tpl_php_fpm = getPluginDir() + '/conf/php-fpm.conf'
        content = public.readFile(tpl_php_fpm)
        content = contentReplace(content, version)
        public.writeFile(desc_php_fpm, content)


def phpFpmWwwReplace(version):
    service_php_fpm_dir = getServerDir() + '/' + version + '/etc/php-fpm.d/'

    if not os.path.exists(service_php_fpm_dir):
        os.mkdir(service_php_fpm_dir)

    service_php_fpmwww = service_php_fpm_dir + '/www.conf'
    if not os.path.exists(service_php_fpmwww):
        tpl_php_fpmwww = getPluginDir() + '/conf/www.conf'
        content = public.readFile(tpl_php_fpmwww)
        content = contentReplace(content, version)
        public.writeFile(service_php_fpmwww, content)


def makePhpIni(version):
    d_ini = public.getServerDir() + '/php/' + version + '/etc/php.ini'
    if not os.path.exists(d_ini):
        s_ini = getPluginDir() + '/conf/php.ini'
        shutil.copyfile(s_ini, d_ini)


def initReplace(version):
    makeOpenrestyConf()
    makePhpIni(version)

    initD_path = getServerDir() + '/init.d'
    file_bin = initD_path + '/php' + version
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)
        file_tpl = getPluginDir() + '/init.d/php.tpl'

        content = public.readFile(file_tpl)
        content = contentReplace(content, version)

        public.writeFile(file_bin, content)
        public.execShell('chmod +x ' + file_bin)

    phpFpmWwwReplace(version)
    phpFpmReplace(version)

    return file_bin


def phpOp(version, method):
    file = initReplace(version)
    data = public.execShell(file + ' ' + method)
    if data[1] == '':
        return 'ok'
    return data[1]


def start(version):
    return phpOp(version, 'start')


def stop(version):
    return phpOp(version, 'stop')


def restart(version):
    return phpOp(version, 'restart')


def reload(version):
    return phpOp(version, 'reload')


def fpmLog(version):
    return getServerDir() + '/' + version + '/var/log/php-fpm.log'


def fpmSlowLog(version):
    return getServerDir() + '/' + version + '/var/log/php-fpm-slow.log'


def getPhpConf(version):
    gets = [
        {'name': 'short_open_tag', 'type': 1, 'ps': '短标签支持'},
        {'name': 'asp_tags', 'type': 1, 'ps': 'ASP标签支持'},
        {'name': 'max_execution_time', 'type': 2, 'ps': '最大脚本运行时间'},
        {'name': 'max_input_time', 'type': 2, 'ps': '最大输入时间'},
        {'name': 'memory_limit', 'type': 2, 'ps': '脚本内存限制'},
        {'name': 'post_max_size', 'type': 2, 'ps': 'POST数据最大尺寸'},
        {'name': 'file_uploads', 'type': 1, 'ps': '是否允许上传文件'},
        {'name': 'upload_max_filesize', 'type': 2, 'ps': '允许上传文件的最大尺寸'},
        {'name': 'max_file_uploads', 'type': 2, 'ps': '允许同时上传文件的最大数量'},
        {'name': 'default_socket_timeout', 'type': 2, 'ps': 'Socket超时时间'},
        {'name': 'error_reporting', 'type': 3, 'ps': '错误级别'},
        {'name': 'display_errors', 'type': 1, 'ps': '是否输出详细错误信息'},
        {'name': 'cgi.fix_pathinfo', 'type': 0, 'ps': '是否开启pathinfo'},
        {'name': 'date.timezone', 'type': 3, 'ps': '时区'}
    ]
    phpini = public.readFile(getServerDir() + '/' + version + '/etc/php.ini')
    result = []
    for g in gets:
        rep = g['name'] + '\s*=\s*([0-9A-Za-z_& ~]+)(\s*;?|\r?\n)'
        tmp = re.search(rep, phpini)
        if not tmp:
            continue
        g['value'] = tmp.groups()[0]
        result.append(g)
    return public.getJson(result)


def submitPhpConf(version):
    gets = ['display_errors', 'cgi.fix_pathinfo', 'date.timezone', 'short_open_tag',
            'asp_tags', 'max_execution_time', 'max_input_time', 'memory_limit',
            'post_max_size', 'file_uploads', 'upload_max_filesize', 'max_file_uploads',
            'default_socket_timeout', 'error_reporting']
    args = getArgs()
    filename = getServerDir() + '/' + version + '/etc/php.ini'
    phpini = public.readFile(filename)
    for g in gets:
        if g in args:
            rep = g + '\s*=\s*(.+)\r?\n'
            val = g + ' = ' + args[g] + '\n'
            phpini = re.sub(rep, val, phpini)
    public.writeFile(filename, phpini)
    public.execShell(getServerDir() + '/init.d/php' + version + ' reload')
    return public.returnJson(True, '设置成功')


def getLimitConf(version):
    fileini = getServerDir() + "/" + version + "/etc/php.ini"
    phpini = public.readFile(fileini)
    filefpm = getServerDir() + "/" + version + "/etc/php-fpm.conf"
    phpfpm = public.readFile(filefpm)

    # print fileini, filefpm
    data = {}
    try:
        rep = "upload_max_filesize\s*=\s*([0-9]+)M"
        tmp = re.search(rep, phpini).groups()
        data['max'] = tmp[0]
    except:
        data['max'] = '50'

    try:
        rep = "request_terminate_timeout\s*=\s*([0-9]+)\n"
        tmp = re.search(rep, phpfpm).groups()
        data['maxTime'] = tmp[0]
    except:
        data['maxTime'] = 0

    try:
        rep = r"\n;*\s*cgi\.fix_pathinfo\s*=\s*([0-9]+)\s*\n"
        tmp = re.search(rep, phpini).groups()

        if tmp[0] == '1':
            data['pathinfo'] = True
        else:
            data['pathinfo'] = False
    except:
        data['pathinfo'] = False

    return public.getJson(data)


def setMaxTime(version):
    args = getArgs()
    if not 'time' in args:
        return 'missing time args!'
    time = args['time']
    if int(time) < 30 or int(time) > 86400:
        return public.returnJson(False, '请填写30-86400间的值!')

    filefpm = getServerDir() + "/" + version + "/etc/php-fpm.conf"
    conf = public.readFile(filefpm)
    rep = "request_terminate_timeout\s*=\s*([0-9]+)\n"
    conf = re.sub(rep, "request_terminate_timeout = " + time + "\n", conf)
    public.writeFile(filefpm, conf)

    fileini = getServerDir() + "/" + version + "/etc/php.ini"
    phpini = public.readFile(fileini)
    rep = "max_execution_time\s*=\s*([0-9]+)\r?\n"
    phpini = re.sub(rep, "max_execution_time = " + time + "\n", phpini)
    rep = "max_input_time\s*=\s*([0-9]+)\r?\n"
    phpini = re.sub(rep, "max_input_time = " + time + "\n", phpini)
    public.writeFile(fileini, phpini)
    return public.returnJson(True, '设置成功!')


def setMaxSize(version):
    args = getArgs()
    if not 'max' in args:
        return 'missing time args!'
    max = args['max']
    if int(max) < 2:
        return public.returnJson(False, '上传大小限制不能小于2MB!')

    path = getServerDir() + '/' + version + '/etc/php.ini'
    conf = public.readFile(path)
    rep = u"\nupload_max_filesize\s*=\s*[0-9]+M"
    conf = re.sub(rep, u'\nupload_max_filesize = ' + max + 'M', conf)
    rep = u"\npost_max_size\s*=\s*[0-9]+M"
    conf = re.sub(rep, u'\npost_max_size = ' + max + 'M', conf)
    public.writeFile(path, conf)

    # if public.get_webserver() == 'nginx':
    #     path = web.ctx.session.setupPath + '/nginx/conf/nginx.conf'
    #     conf = public.readFile(path)
    #     rep = "client_max_body_size\s+([0-9]+)m"
    #     tmp = re.search(rep, conf).groups()
    #     if int(tmp[0]) < int(max):
    #         conf = re.sub(rep, 'client_max_body_size ' + max + 'm', conf)
    #         public.writeFile(path, conf)

    public.writeLog("TYPE_PHP", "PHP_UPLOAD_MAX", (version, max))
    return public.returnJson(True, '设置成功!')


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print 'missing parameters'
        exit(0)

    func = sys.argv[1]
    version = sys.argv[2]

    if func == 'status':
        print status(version)
    elif func == 'start':
        print start(version)
    elif func == 'stop':
        print stop(version)
    elif func == 'restart':
        print restart(version)
    elif func == 'reload':
        print reload(version)
    elif func == 'fpm_log':
        print fpmLog(version)
    elif func == 'fpm_slow_log':
        print fpmSlowLog(version)
    elif func == 'conf':
        print getConf(version)
    elif func == 'get_php_conf':
        print getPhpConf(version)
    elif func == 'submit_php_conf':
        print submitPhpConf(version)
    elif func == 'get_limit_conf':
        print getLimitConf(version)
    elif func == 'set_max_time':
        print setMaxTime(version)
    elif func == 'set_max_size':
        print setMaxSize(version)
    else:
        print "fail"
