# coding:utf-8

import sys
import io
import os
import time
import subprocess
import json

sys.path.append(os.getcwd() + "/class/core")
import mw


app_debug = False
if mw.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'op_waf'


def getPluginDir():
    return mw.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return mw.getServerDir() + '/' + getPluginName()


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


def checkArgs(data, ck=[]):
    for i in range(len(ck)):
        if not ck[i] in data:
            return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, mw.returnJson(True, 'ok'))


def getConf():
    path = mw.getServerDir() + "/openresty/nginx/conf/nginx.conf"
    return path


def initDomainInfo():
    data = []
    path_domains = getJsonPath('domains')

    _list = mw.M('sites').field('id,name,path').where(
        'status=?', ('1',)).order('id desc').select()

    for i in range(len(_list)):
        tmp = {}
        tmp['name'] = _list[i]['name']
        tmp['path'] = _list[i]['path']

        _list_domain = mw.M('domain').field('name').where(
            'pid=?', (_list[i]['id'],)).order('id desc').select()

        tmp_j = []
        for j in range(len(_list_domain)):
            tmp_j.append(_list_domain[j]['name'])

        tmp['domains'] = tmp_j
        data.append(tmp)
    cjson = mw.getJson(data)
    mw.writeFile(path_domains, cjson)


def initSiteInfo():
    data = []
    path_domains = getJsonPath('domains')
    path_config = getJsonPath('config')
    path_site = getJsonPath('site')

    config_contents = mw.readFile(path_config)
    config_contents = json.loads(config_contents)

    domain_contents = mw.readFile(path_domains)
    domain_contents = json.loads(domain_contents)

    try:
        site_contents = mw.readFile(path_site)
    except Exception as e:
        site_contents = "{}"

    site_contents = json.loads(site_contents)
    site_contents_new = {}
    for x in range(len(domain_contents)):
        name = domain_contents[x]['name']
        if name in site_contents:
            site_contents_new[name] = site_contents[name]
        else:
            tmp = {}
            tmp['cdn'] = False
            tmp['log'] = True
            tmp['get'] = True
            tmp['post'] = True
            tmp['open'] = False

            tmp['cc'] = config_contents['cc']
            tmp['retry'] = config_contents['retry']
            tmp['get'] = config_contents['get']
            tmp['post'] = config_contents['post']
            tmp['user-agent'] = config_contents['user-agent']
            tmp['cookie'] = config_contents['cookie']
            tmp['scan'] = config_contents['scan']

            cdn_header = ['x-forwarded-for',
                          'x-real-ip', 'HTTP_CF_CONNECTING_IP']
            tmp['cdn_header'] = cdn_header

            disable_upload_ext = ["php", "jsp"]
            tmp['disable_upload_ext'] = disable_upload_ext

            disable_path = ['sql']
            tmp['disable_ext'] = disable_path

            site_contents_new[name] = tmp

    cjson = mw.getJson(site_contents_new)
    mw.writeFile(path_site, cjson)


def initTotalInfo():
    data = []
    path_domains = getJsonPath('domains')
    path_total = getJsonPath('total')

    domain_contents = mw.readFile(path_domains)
    domain_contents = json.loads(domain_contents)

    try:
        total_contents = mw.readFile(path_total)
    except Exception as e:
        total_contents = "{}"

    total_contents = json.loads(total_contents)
    total_contents_new = {}
    for x in range(len(domain_contents)):
        name = domain_contents[x]['name']
        if 'sites' in total_contents and name in total_contents['sites']:
            pass
        else:
            tmp = {}
            tmp['cdn'] = 0
            tmp['log'] = 0
            tmp['get'] = 0
            tmp['post'] = 0
            tmp['total'] = 0
            _name = {}
            _name[name] = tmp
            total_contents['sites'] = _name

    cjson = mw.getJson(total_contents)
    mw.writeFile(path_total, cjson)


def status():
    path = getConf()
    if not os.path.exists(path):
        return 'stop'

    conf = mw.readFile(path)
    if conf.find("#include luawaf.conf;") != -1:
        return 'stop'
    if conf.find("luawaf.conf;") == -1:
        return 'stop'
    return 'start'


def contentReplace(content):
    service_path = mw.getServerDir()
    waf_path = getServerDir() + "/waf"
    content = content.replace('{$ROOT_PATH}', mw.getRootDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$WAF_PATH}', waf_path)
    return content


def initDreplace():

    path = getServerDir()
    if not os.path.exists(path + '/waf'):
        sdir = getPluginDir() + '/waf'
        cmd = 'cp -rf ' + sdir + ' ' + path
        mw.execShell(cmd)

    config = path + '/waf/config.json'
    content = mw.readFile(config)
    content = json.loads(content)

    wfDir = path + "/waf/html"
    content['reqfile_path'] = wfDir
    mw.writeFile(config, mw.getJson(content))

    config = path + "/waf/lua/init.lua"
    content = mw.readFile(config)
    content = contentReplace(content)
    mw.writeFile(config, content)

    waf_conf = mw.getServerDir() + "/openresty/nginx/conf/luawaf.conf"
    waf_tpl = getPluginDir() + "/conf/luawaf.conf"
    content = mw.readFile(waf_tpl)
    content = contentReplace(content)
    mw.writeFile(waf_conf, content)

    initDomainInfo()
    initSiteInfo()
    initTotalInfo()


def start():
    initDreplace()

    path = getConf()
    conf = mw.readFile(path)
    conf = conf.replace('#include luawaf.conf;', "include luawaf.conf;")
    mw.writeFile(path, conf)

    mw.restartWeb()
    return 'ok'


def stop():
    path = getConf()
    conf = mw.readFile(path)
    conf = conf.replace('include luawaf.conf;', "#include luawaf.conf;")

    mw.writeFile(path, conf)
    mw.restartWeb()
    return 'ok'


def restart():
    mw.restartWeb()
    return 'ok'


def reload():
    stop()
    mw.execShell('rm -rf ' + mw.getServerDir() +
                 "/openresty/nginx/logs/error.log")
    start()
    return 'ok'


def getJsonPath(name):
    path = getServerDir() + "/waf/" + name + ".json"
    return path


def getRuleJsonPath(name):
    path = getServerDir() + "/waf/rule/" + name + ".json"
    return path


def getRule():
    args = getArgs()
    data = checkArgs(args, ['rule_name'])
    if not data[0]:
        return data[1]

    rule_name = args['rule_name']
    fpath = getRuleJsonPath(rule_name)
    content = mw.readFile(fpath)
    return mw.returnJson(True, 'ok', content)


def addRule():
    args = getArgs()
    data = checkArgs(args, ['ruleName', 'ruleValue', 'ps'])
    if not data[0]:
        return data[1]

    ruleValue = args['ruleValue']
    ruleName = args['ruleName']
    ps = args['ps']

    fpath = getRuleJsonPath(ruleName)
    content = mw.readFile(fpath)
    content = json.loads(content)

    tmp_k = []
    tmp_k.append(1)
    tmp_k.append(ruleValue)
    tmp_k.append(ps)
    tmp_k.append(1)

    content.append(tmp_k)

    cjson = mw.getJson(content)
    mw.writeFile(fpath, cjson)

    return mw.returnJson(True, '设置成功!', content)


def removeRule():
    args = getArgs()
    data = checkArgs(args, ['ruleName', 'index'])
    if not data[0]:
        return data[1]

    index = int(args['index'])
    ruleName = args['ruleName']

    fpath = getRuleJsonPath(ruleName)
    content = mw.readFile(fpath)
    content = json.loads(content)

    k = content[index]
    content.remove(k)

    cjson = mw.getJson(content)
    mw.writeFile(fpath, cjson)

    return mw.returnJson(True, '设置成功!', content)


def setRuleState():
    args = getArgs()
    data = checkArgs(args, ['ruleName', 'index'])
    if not data[0]:
        return data[1]

    index = int(args['index'])
    ruleName = args['ruleName']

    fpath = getRuleJsonPath(ruleName)
    content = mw.readFile(fpath)
    content = json.loads(content)

    b = content[index][0]
    if b == 1:
        content[index][0] = 0
    else:
        content[index][0] = 1

    cjson = mw.getJson(content)
    mw.writeFile(fpath, cjson)

    return mw.returnJson(True, '设置成功!', content)


def modifyRule():
    args = getArgs()
    data = checkArgs(args, ['index', 'ruleName', 'ruleBody', 'rulePs'])
    if not data[0]:
        return data[1]

    index = int(args['index'])
    ruleName = args['ruleName']
    ruleBody = args['ruleBody']
    rulePs = args['rulePs']

    fpath = getRuleJsonPath(ruleName)
    content = mw.readFile(fpath)
    content = json.loads(content)

    tmp = content[index]

    tmp_k = []
    tmp_k.append(tmp[0])
    tmp_k.append(ruleBody)
    tmp_k.append(rulePs)
    tmp_k.append(tmp[3])

    content[index] = tmp_k

    cjson = mw.getJson(content)
    mw.writeFile(fpath, cjson)

    return mw.returnJson(True, '设置成功!', content)


def getSiteRule():
    args = getArgs()
    data = checkArgs(args, ['siteName', 'ruleName'])
    if not data[0]:
        return data[1]

    siteName = args['siteName']
    siteRule = args['ruleName']

    path = getJsonPath('site')
    content = mw.readFile(path)
    content = json.loads(content)

    r = content[siteName][siteRule]

    cjson = mw.getJson(r)
    return mw.returnJson(True, 'ok!', cjson)


def addSiteRule():
    args = getArgs()
    data = checkArgs(args, ['siteName', 'ruleName', 'ruleValue'])
    if not data[0]:
        return data[1]

    siteName = args['siteName']
    siteRule = args['ruleName']
    ruleValue = args['ruleValue']

    path = getJsonPath('site')
    content = mw.readFile(path)
    content = json.loads(content)

    content[siteName][siteRule].append(ruleValue)

    cjson = mw.getJson(content)
    mw.writeFile(path, cjson)
    return mw.returnJson(True, '设置成功!')


def addIpWhite():
    args = getArgs()
    data = checkArgs(args, ['start_ip', 'end_ip'])
    if not data[0]:
        return data[1]

    start_ip = args['start_ip']
    end_ip = args['end_ip']

    path = getRuleJsonPath('ip_white')
    content = mw.readFile(path)
    content = json.loads(content)

    data = []

    start_ip_list = start_ip.split('.')
    tmp = []
    for x in range(len(start_ip_list)):
        tmp.append(int(start_ip_list[x]))

    end_ip_list = end_ip.split('.')
    tmp2 = []
    for x in range(len(end_ip_list)):
        tmp2.append(int(end_ip_list[x]))

    data.append(tmp)
    data.append(tmp2)

    content.append(data)

    cjson = mw.getJson(content)
    mw.writeFile(path, cjson)
    return mw.returnJson(True, '设置成功!')


def removeIpWhite():
    args = getArgs()
    data = checkArgs(args, ['index'])
    if not data[0]:
        return data[1]

    index = args['index']

    path = getRuleJsonPath('ip_white')
    content = mw.readFile(path)
    content = json.loads(content)

    k = content[int(index)]
    content.remove(k)

    cjson = mw.getJson(content)
    mw.writeFile(path, cjson)
    return mw.returnJson(True, '设置成功!')


def addIpBlack():
    args = getArgs()
    data = checkArgs(args, ['start_ip', 'end_ip'])
    if not data[0]:
        return data[1]

    start_ip = args['start_ip']
    end_ip = args['end_ip']

    path = getRuleJsonPath('ip_black')
    content = mw.readFile(path)
    content = json.loads(content)

    data = []

    start_ip_list = start_ip.split('.')
    tmp = []
    for x in range(len(start_ip_list)):
        tmp.append(int(start_ip_list[x]))

    end_ip_list = end_ip.split('.')
    tmp2 = []
    for x in range(len(end_ip_list)):
        tmp2.append(int(end_ip_list[x]))

    data.append(tmp)
    data.append(tmp2)

    content.append(data)

    cjson = mw.getJson(content)
    mw.writeFile(path, cjson)
    return mw.returnJson(True, '设置成功!')


def removeIpBlack():
    args = getArgs()
    data = checkArgs(args, ['index'])
    if not data[0]:
        return data[1]

    index = args['index']

    path = getRuleJsonPath('ip_black')
    content = mw.readFile(path)
    content = json.loads(content)

    k = content[int(index)]
    content.remove(k)

    cjson = mw.getJson(content)
    mw.writeFile(path, cjson)
    return mw.returnJson(True, '设置成功!')


def setIpv6Black():
    args = getArgs()
    data = checkArgs(args, ['addr'])
    if not data[0]:
        return data[1]

    addr = args['addr'].replace('_', ':')
    path = getRuleJsonPath('ipv6_black')

    content = mw.readFile(path)
    content = json.loads(content)
    content.append(addr)

    cjson = mw.getJson(content)
    mw.writeFile(path, cjson)
    return mw.returnJson(True, '设置成功!')


def delIpv6Black():
    args = getArgs()
    data = checkArgs(args, ['addr'])
    if not data[0]:
        return data[1]

    addr = args['addr'].replace('_', ':')
    path = getRuleJsonPath('ipv6_black')

    content = mw.readFile(path)
    content = json.loads(content)

    content.remove(addr)

    cjson = mw.getJson(content)
    mw.writeFile(path, cjson)
    return mw.returnJson(True, '设置成功!')


def removeSiteRule():
    args = getArgs()
    data = checkArgs(args, ['siteName', 'ruleName', 'index'])
    if not data[0]:
        return data[1]

    siteName = args['siteName']
    siteRule = args['ruleName']
    index = args['index']

    path = getJsonPath('site')
    content = mw.readFile(path)
    content = json.loads(content)

    ruleValue = content[siteName][siteRule][int(index)]
    content[siteName][siteRule].remove(ruleValue)

    cjson = mw.getJson(content)
    mw.writeFile(path, cjson)
    return mw.returnJson(True, '设置成功!')


def setObjStatus():
    args = getArgs()
    data = checkArgs(args, ['obj', 'statusCode'])
    if not data[0]:
        return data[1]

    conf = getJsonPath('config')
    content = mw.readFile(conf)
    cobj = json.loads(content)

    o = args['obj']
    status = args['statusCode']
    cobj[o]['status'] = status

    cjson = mw.getJson(cobj)
    mw.writeFile(conf, cjson)
    return mw.returnJson(True, '设置成功!')


def setRetry():
    args = getArgs()
    data = checkArgs(args, ['retry', 'retry_time',
                            'retry_cycle', 'is_open_global'])
    if not data[0]:
        return data[1]

    conf = getJsonPath('config')
    content = mw.readFile(conf)
    cobj = json.loads(content)

    cobj['retry'] = args

    cjson = mw.getJson(cobj)
    mw.writeFile(conf, cjson)

    return mw.returnJson(True, '设置成功!', [])


def setSiteRetry():
    return mw.returnJson(True, '设置成功-?!', [])


def setCcConf():
    args = getArgs()
    data = checkArgs(args, ['siteName', 'cycle', 'limit',
                            'endtime', 'is_open_global', 'increase'])
    if not data[0]:
        return data[1]

    conf = getJsonPath('config')
    content = mw.readFile(conf)
    cobj = json.loads(content)

    tmp = cobj['cc']

    tmp['cycle'] = int(args['cycle'])
    tmp['limit'] = int(args['limit'])
    tmp['endtime'] = int(args['endtime'])
    tmp['is_open_global'] = args['is_open_global']
    tmp['increase'] = args['increase']
    cobj['cc'] = tmp

    cjson = mw.getJson(cobj)
    mw.writeFile(conf, cjson)
    return mw.returnJson(True, '设置成功!', [])


def setSiteCcConf():
    return mw.returnJson(False, '暂未开发!', [])


def saveScanRule():
    args = getArgs()
    data = checkArgs(args, ['header', 'cookie', 'args'])
    if not data[0]:
        return data[1]

    path = getRuleJsonPath('scan_black')
    cjson = mw.getJson(args)
    mw.writeFile(path, cjson)
    return mw.returnJson(True, '设置成功!', [])


def getSiteConfig():
    path = getJsonPath('site')
    content = mw.readFile(path)

    content = json.loads(content)

    total = getJsonPath('total')
    total_content = mw.readFile(total)
    total_content = json.loads(total_content)

    # print total_content

    for x in content:
        tmp = []
        tmp_v = {}
        if 'sites' in total_content and x in total_content['sites']:
            tmp_v = total_content['sites'][x]

        key_list = ['get', 'post', 'user-agent', 'cookie', 'cdn', 'cc']
        for kx in range(len(key_list)):
            ktmp = {}

            if kx in tmp_v:
                ktmp['value'] = tmp_v[key_list[kx]]
            else:
                ktmp['value'] = ''
            ktmp['key'] = key_list[kx]
            tmp.append(ktmp)

        # print tmp
        content[x]['total'] = tmp

    content = mw.getJson(content)
    return mw.returnJson(True, 'ok!', content)


def getSiteConfigByName():
    args = getArgs()
    data = checkArgs(args, ['siteName'])
    if not data[0]:
        return data[1]
    path = getJsonPath('site')
    content = mw.readFile(path)
    content = json.loads(content)

    siteName = args['siteName']
    retData = {}
    if siteName in content:
        retData = content[siteName]

    return mw.returnJson(True, 'ok!', retData)


def addSiteCdnHeader():
    args = getArgs()
    data = checkArgs(args, ['siteName', 'cdn_header'])
    if not data[0]:
        return data[1]
    path = getJsonPath('site')
    content = mw.readFile(path)
    content = json.loads(content)

    siteName = args['siteName']
    retData = {}
    if siteName in content:
        content[siteName]['cdn_header'].append(args['cdn_header'])

    cjson = mw.getJson(content)
    mw.writeFile(path, cjson)
    return mw.returnJson(True, '添加成功!')


def removeSiteCdnHeader():
    args = getArgs()
    data = checkArgs(args, ['siteName', 'cdn_header'])
    if not data[0]:
        return data[1]
    path = getJsonPath('site')
    content = mw.readFile(path)
    content = json.loads(content)

    siteName = args['siteName']
    retData = {}
    if siteName in content:
        content[siteName]['cdn_header'].remove(args['cdn_header'])

    cjson = mw.getJson(content)
    mw.writeFile(path, cjson)
    return mw.returnJson(True, '删除成功!')


def outputData():
    args = getArgs()
    data = checkArgs(args, ['s_Name'])
    if not data[0]:
        return data[1]

    path = getRuleJsonPath(args['s_Name'])
    content = mw.readFile(path)
    return mw.returnJson(True, 'ok', content)


def importData():
    args = getArgs()
    data = checkArgs(args, ['s_Name', 'pdata'])
    if not data[0]:
        return data[1]

    path = getRuleJsonPath(args['s_Name'])
    mw.writeFile(path, args['pdata'])
    return mw.returnJson(True, '设置成功!')


def getLogsList():
    args = getArgs()
    data = checkArgs(args, ['siteName'])
    if not data[0]:
        return data[1]

    data = []
    path = mw.getLogsDir() + '/waf'

    if not os.path.exists(path):
        return mw.returnJson(False, '还未生成!', [])

    files = os.listdir(path)
    for f in files:
        if f == '.DS_Store':
            continue
        f = f.split('_')
        if f[0] == args['siteName']:
            fl = f[1].split('.')
            data.append(fl[0])

    return mw.returnJson(True, 'ok!', data)


def getSafeLogs():
    args = getArgs()
    data = checkArgs(args, ['siteName', 'toDate', 'p'])
    if not data[0]:
        return data[1]

    path = mw.getLogsDir() + '/waf'
    file = path + '/' + args['siteName'] + '_' + args['toDate'] + '.log'
    if not os.path.exists(file):
        return mw.returnJson(False, "文件不存在!")

    retData = []
    file = open(file)
    while 1:
        lines = file.readlines(100000)
        if not lines:
            break
        for line in lines:

            retData.append(json.loads(line))

    return mw.returnJson(True, '设置成功!', retData)


def setObjOpen():
    args = getArgs()
    data = checkArgs(args, ['obj'])
    if not data[0]:
        return data[1]

    conf = getJsonPath('config')
    content = mw.readFile(conf)
    cobj = json.loads(content)

    o = args['obj']
    if cobj[o]["open"]:
        cobj[o]["open"] = False
    else:
        cobj[o]["open"] = True

    cjson = mw.getJson(cobj)
    mw.writeFile(conf, cjson)
    return mw.returnJson(True, '设置成功!')


def setSiteObjOpen():
    args = getArgs()
    data = checkArgs(args, ['siteName', 'obj'])
    if not data[0]:
        return data[1]

    siteName = args['siteName']
    obj = args['obj']

    path = getJsonPath('site')
    content = mw.readFile(path)
    content = json.loads(content)

    if type(content[siteName][obj]) == bool:
        if content[siteName][obj]:
            content[siteName][obj] = False
        else:
            content[siteName][obj] = True
    else:
        if content[siteName][obj]['open']:
            content[siteName][obj]['open'] = False
        else:
            content[siteName][obj]['open'] = True

    cjson = mw.getJson(content)
    mw.writeFile(path, cjson)
    return mw.returnJson(True, '设置成功!')


def getWafSrceen():
    conf = getJsonPath('total')
    return mw.readFile(conf)


def getWafConf():
    conf = getJsonPath('config')
    return mw.readFile(conf)


def getWafSite():
    return ''


if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print(status())
    elif func == 'start':
        print(start())
    elif func == 'stop':
        print(stop())
    elif func == 'restart':
        print(restart())
    elif func == 'reload':
        print(reload())
    elif func == 'conf':
        print(getConf())
    elif func == 'get_rule':
        print(getRule())
    elif func == 'add_rule':
        print(addRule())
    elif func == 'remove_rule':
        print(removeRule())
    elif func == 'set_rule_state':
        print(setRuleState())
    elif func == 'modify_rule':
        print(modifyRule())
    elif func == 'get_site_rule':
        print(getSiteRule())
    elif func == 'add_site_rule':
        print(addSiteRule())
    elif func == 'add_ip_white':
        print(addIpWhite())
    elif func == 'remove_ip_white':
        print(removeIpWhite())
    elif func == 'add_ip_black':
        print(addIpBlack())
    elif func == 'remove_ip_black':
        print(removeIpBlack())
    elif func == 'set_ipv6_black':
        print(setIpv6Black())
    elif func == 'del_ipv6_black':
        print(delIpv6Black())
    elif func == 'remove_site_rule':
        print(removeSiteRule())
    elif func == 'set_obj_status':
        print(setObjStatus())
    elif func == 'set_obj_open':
        print(setObjOpen())
    elif func == 'set_site_obj_open':
        print(setSiteObjOpen())
    elif func == 'set_cc_conf':
        print(setCcConf())
    elif func == 'set_site_cc_conf':
        print(setSiteCcConf())
    elif func == 'set_retry':
        print(setRetry())
    elif func == 'set_site_retry':
        print(setSiteRetry())
    elif func == 'save_scan_rule':
        print(saveScanRule())
    elif func == 'get_site_config':
        print(getSiteConfig())
    elif func == 'get_site_config_byname':
        print(getSiteConfigByName())
    elif func == 'add_site_cdn_header':
        print(addSiteCdnHeader())
    elif func == 'remove_site_cdn_header':
        print(removeSiteCdnHeader())
    elif func == 'get_logs_list':
        print(getLogsList())
    elif func == 'get_safe_logs':
        print(getSafeLogs())
    elif func == 'output_data':
        print(outputData())
    elif func == 'import_data':
        print(importData())
    elif func == 'waf_srceen':
        print(getWafSrceen())
    elif func == 'waf_conf':
        print(getWafConf())
    elif func == 'waf_site':
        print(getWafSite())
    else:
        print('error')
