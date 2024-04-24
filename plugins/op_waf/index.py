# coding:utf-8

'''
cd /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/op_waf && bash install.sh install 0.3.2
python3 /Users/midoks/Desktop/mwdev/server/mdserver-web/plugins/op_waf/index.py reload
'''
import sys
import io
import os
import time
import subprocess
import json
import re

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
        t = t.split(':', 1)
        tmp[t[0]] = t[1]
    elif args_len > 1:
        for i in range(len(args)):
            t = args[i].split(':', 1)
            tmp[t[0]] = t[1]

    return tmp


def checkArgs(data, ck=[]):
    for i in range(len(ck)):
        if not ck[i] in data:
            return (False, mw.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, mw.returnJson(True, 'ok'))


sys.path.append(getPluginDir() + "/class")
from luamaker import luamaker


def listToLuaFile(path, lists):
    content = luamaker.makeLuaTable(lists)
    content = "return " + content
    mw.writeFile(path, content)


def htmlToLuaFile(path, content):
    content = "return [[" + content + "]]"
    mw.writeFile(path, content)


def getConf():
    path = mw.getServerDir() + "/openresty/nginx/conf/nginx.conf"
    return path


def dstWafConfPath():
    return mw.getServerDir() + "/web_conf/nginx/vhost/opwaf.conf"


def pSqliteDb(dbname='logs'):
    name = "waf"
    db_dir = getServerDir() + '/logs/'

    if not os.path.exists(db_dir):
        mw.execShell('mkdir -p ' + db_dir)

    file = db_dir + name + '.db'
    if not os.path.exists(file):
        conn = mw.M(dbname).dbPos(db_dir, name)
        sql = mw.readFile(getPluginDir() + '/conf/init.sql')
        sql_list = sql.split(';')
        for index in range(len(sql_list)):
            conn.execute(sql_list[index])
    else:
        conn = mw.M(dbname).dbPos(db_dir, name)

    conn.execute("PRAGMA synchronous = 0")
    conn.execute("PRAGMA page_size = 4096")
    conn.execute("PRAGMA journal_mode = wal")
    conn.execute("PRAGMA journal_size_limit = 1073741824")
    return conn


def initDomainInfo(conf_reload=False):
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


def initSiteInfo(conf_reload=False):
    data = []

    path_site = getJsonPath('site')
    path_domains = getJsonPath('domains')
    path_config = getJsonPath('config')

    config_contents = mw.readFile(path_config)
    config_contents = json.loads(config_contents)

    domain_contents = mw.readFile(path_domains)
    domain_contents = json.loads(domain_contents)

    try:
        site_contents = mw.readFile(path_site)
        if not site_contents:
            site_contents = "{}"
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
            tmp['cdn'] = True
            tmp['log'] = True
            tmp['get'] = True
            tmp['post'] = True
            tmp['open'] = True

            tmp['cc'] = config_contents['cc']
            tmp['retry'] = config_contents['retry']
            tmp['get'] = config_contents['get']
            tmp['post'] = config_contents['post']
            tmp['user-agent'] = config_contents['user-agent']
            tmp['cookie'] = config_contents['cookie']
            tmp['scan'] = config_contents['scan']
            tmp['safe_verify'] = config_contents['safe_verify']

            cdn_header = ['x-forwarded-for',
                          'x-real-ip',
                          'x-forwarded',
                          'forwarded-for',
                          'forwarded',
                          'true-client-ip',
                          'client-ip',
                          'ali-cdn-real-ip',
                          'cdn-src-ip',
                          'cdn-real-ip',
                          'cf-connecting-ip',
                          'x-cluster-client-ip',
                          'wl-proxy-client-ip',
                          'proxy-client-ip',
                          'true-client-ip',
                          'HTTP_CF_CONNECTING_IP']
            tmp['cdn_header'] = cdn_header

            disable_upload_ext = ["php", "jsp"]
            tmp['disable_upload_ext'] = disable_upload_ext

            disable_path = ['sql']
            tmp['disable_ext'] = disable_path

            site_contents_new[name] = tmp

    cjson = mw.getJson(site_contents_new)
    mw.writeFile(path_site, cjson)


def initTotalInfo(conf_reload=False):
    data = []

    path_total = getJsonPath('total')
    path_domains = getJsonPath('domains')

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
            tmp['path'] = 0
            tmp['php_path'] = 0
            tmp['upload_ext'] = 0
            _name = {}
            _name[name] = tmp
            total_contents['sites'] = _name

    total_contents['start_time'] = str(time.time())
    cjson = mw.getJson(total_contents)
    mw.writeFile(path_total, cjson)


def contentReplace(content):
    service_path = mw.getServerDir()
    waf_root = getServerDir()
    waf_path = waf_root + "/waf"
    content = content.replace('{$ROOT_PATH}', mw.getRootDir())
    content = content.replace('{$SERVER_PATH}', service_path)
    content = content.replace('{$WAF_PATH}', waf_path)
    content = content.replace('{$WAF_ROOT}', waf_root)

    if mw.isAppleSystem():
        content = content.replace('{$MMDB_FILE_SUFFIX}', 'dylib')
    else:
        content = content.replace('{$MMDB_FILE_SUFFIX}', 'so')

    return content


def autoMakeLuaConfSingle(file, conf_reload=False):
    path = getServerDir() + "/waf/rule/" + file + ".json"
    dst_path = getServerDir() + "/waf/conf/rule_" + file + ".lua"
    if not os.path.exists(dst_path) or conf_reload:
        content = mw.readFile(path)
        # print(content)
        content = json.loads(content)
        listToLuaFile(dst_path, content)


def autoCpImport(file):
    path = getPluginDir() + "/waf/" + file + ".json"
    dst_path = getServerDir() + "/waf/" + file + ".json"
    content = mw.readFile(path)
    mw.writeFile(dst_path, content)


def autoMakeLuaImportSingle(file, conf_reload=False):
    path = getServerDir() + "/waf/" + file + ".json"
    dst_path = getServerDir() + "/waf/conf/waf_" + file + ".lua"
    if not os.path.exists(dst_path) or conf_reload:
        content = mw.readFile(path)
        # print(content)
        content = json.loads(content)
        listToLuaFile(dst_path, content)


def autoMakeLuaHtmlSingle(file, conf_reload=False):
    path = getServerDir() + "/waf/html/" + file + ".html"
    dst_path = getServerDir() + "/waf/html/html_" + file + ".lua"
    if not os.path.exists(dst_path) or conf_reload:
        content = mw.readFile(path)
        htmlToLuaFile(dst_path, content)


def autoCpHtml(file):
    path = getPluginDir() + "/waf/html/" + file + ".html"
    dst_path = getServerDir() + "/waf/html/" + file + ".html"
    content = mw.readFile(path)
    mw.writeFile(dst_path, content)


def autoMakeLuaConf(conf_reload=False, cp_reload=False):
    conf_list = ['args', 'cookie', 'ip_black', 'ip_white',
                 'ipv6_black', 'post', 'scan_black', 'url',
                 'url_white', 'user_agent']
    for x in conf_list:
        autoMakeLuaConfSingle(x, conf_reload)

    import_list = ['config', 'site', 'domains', 'area_limit']
    for x in import_list:
        autoMakeLuaImportSingle(x, conf_reload)

    html_list = ['get', 'post', 'safe_js', 'user_agent', 'cookie', 'other']
    for x in html_list:
        if cp_reload:
            autoCpHtml(x)
        autoMakeLuaHtmlSingle(x, conf_reload)


def initDefaultInfo(conf_reload=False):
    path = getServerDir()
    dst_path = path + "/waf/default.pl"
    default_site = ''
    if os.path.exists(dst_path):
        return True
    source_path = path + "/waf/domains.json"
    content = mw.readFile(source_path)
    content = json.loads(content)

    ddata = {}
    dlist = []
    for i in content:
        dlist.append(i["name"])

    dlist.append('unset')
    ddata["list"] = dlist
    if len(ddata["list"]) < 1:
        default_site = "unset"
    else:
        default_site = dlist[0]

    mw.writeFile(dst_path, default_site)


def getSiteListData():
    path = getServerDir()
    source_path = path + "/waf/domains.json"
    dst_path = path + "/waf/default.pl"

    content = mw.readFile(source_path)
    content = json.loads(content)
    dlist = []
    for i in content:
        dlist.append(i["name"])
    dlist.append('unset')

    default_site = mw.readFile(dst_path)

    data = {}
    data['list'] = dlist
    data['default'] = default_site
    return data


def setDefaultSite(name):
    path = getServerDir()
    dst_path = path + "/waf/default.pl"
    mw.writeFile(dst_path, name)
    return mw.returnJson(True, 'OK')


def getDefaultSite():
    data = getSiteListData()
    return mw.returnJson(True, 'OK', data)


def getCountry():
    data = ['中国大陆以外的地区(包括[中国特别行政区:港,澳,台])', '中国大陆(不包括[中国特别行政区:港,澳,台])', '中国香港', '中国澳门', '中国台湾',
            '美国', '日本', '英国', '德国', '韩国', '法国', '巴西', '加拿大', '意大利', '澳大利亚', '荷兰', '俄罗斯', '印度', '瑞典', '西班牙', '墨西哥',
            '比利时', '南非', '波兰', '瑞士', '阿根廷', '印度尼西亚', '埃及', '哥伦比亚', '土耳其', '越南', '挪威', '芬兰', '丹麦', '乌克兰', '奥地利',
            '伊朗', '智利', '罗马尼亚', '捷克', '泰国', '沙特阿拉伯', '以色列', '新西兰', '委内瑞拉', '摩洛哥', '马来西亚', '葡萄牙', '爱尔兰', '新加坡',
            '欧洲联盟', '匈牙利', '希腊', '菲律宾', '巴基斯坦', '保加利亚', '肯尼亚', '阿拉伯联合酋长国', '阿尔及利亚', '塞舌尔', '突尼斯', '秘鲁', '哈萨克斯坦',
            '斯洛伐克', '斯洛文尼亚', '厄瓜多尔', '哥斯达黎加', '乌拉圭', '立陶宛', '塞尔维亚', '尼日利亚', '克罗地亚', '科威特', '巴拿马', '毛里求斯', '白俄罗斯',
            '拉脱维亚', '多米尼加', '卢森堡', '爱沙尼亚', '苏丹', '格鲁吉亚', '安哥拉', '玻利维亚', '赞比亚', '孟加拉国', '巴拉圭', '波多黎各', '坦桑尼亚',
            '塞浦路斯', '摩尔多瓦', '阿曼', '冰岛', '叙利亚', '卡塔尔', '波黑', '加纳', '阿塞拜疆', '马其顿', '约旦', '萨尔瓦多', '伊拉克', '亚美尼亚', '马耳他',
            '危地马拉', '巴勒斯坦', '斯里兰卡', '特立尼达和多巴哥', '黎巴嫩', '尼泊尔', '纳米比亚', '巴林', '洪都拉斯', '莫桑比克', '尼加拉瓜', '卢旺达', '加蓬',
            '阿尔巴尼亚', '利比亚', '吉尔吉斯坦', '柬埔寨', '古巴', '喀麦隆', '乌干达', '塞内加尔', '乌兹别克斯坦', '黑山', '关岛', '牙买加', '蒙古', '文莱',
            '英属维尔京群岛', '留尼旺', '库拉索岛', '科特迪瓦', '开曼群岛', '巴巴多斯', '马达加斯加', '伯利兹', '新喀里多尼亚', '海地', '马拉维', '斐济', '巴哈马',
            '博茨瓦纳', '扎伊尔', '阿富汗', '莱索托', '百慕大', '埃塞俄比亚', '美属维尔京群岛', '列支敦士登', '津巴布韦', '直布罗陀', '苏里南', '马里', '也门',
            '老挝', '塔吉克斯坦', '安提瓜和巴布达', '贝宁', '法属玻利尼西亚', '圣基茨和尼维斯', '圭亚那', '布基纳法索', '马尔代夫', '泽西岛', '摩纳哥', '巴布亚新几内亚',
            '刚果', '塞拉利昂', '吉布提', '斯威士兰', '缅甸', '毛里塔尼亚', '法罗群岛', '尼日尔', '安道尔', '阿鲁巴', '布隆迪', '圣马力诺', '利比里亚',
            '冈比亚', '不丹', '几内亚', '圣文森特岛', '荷兰加勒比区', '圣马丁', '多哥', '格陵兰', '佛得角', '马恩岛', '索马里', '法属圭亚那', '西萨摩亚',
            '土库曼斯坦', '瓜德罗普', '马里亚那群岛', '瓦努阿图', '马提尼克', '赤道几内亚', '南苏丹', '梵蒂冈', '格林纳达', '所罗门群岛', '特克斯和凯科斯群岛', '多米尼克',
            '乍得', '汤加', '瑙鲁', '圣多美和普林西比', '安圭拉岛', '法属圣马丁', '图瓦卢', '库克群岛', '密克罗尼西亚联邦', '根西岛', '东帝汶', '中非',
            '几内亚比绍', '帕劳', '美属萨摩亚', '厄立特里亚', '科摩罗', '圣皮埃尔和密克隆', '瓦利斯和富图纳', '英属印度洋领地', '托克劳', '马绍尔群岛', '基里巴斯',
            '纽埃', '诺福克岛', '蒙特塞拉特岛', '朝鲜', '马约特', '圣卢西亚', '圣巴泰勒米岛']
    return mw.returnJson(True, 'ok', data)


def autoMakeConfig(conf_reload=False, cp_reload=False):
    initDomainInfo(conf_reload)
    initSiteInfo(conf_reload)
    initTotalInfo(conf_reload)
    autoMakeLuaConf(conf_reload, cp_reload)
    initDefaultInfo(conf_reload)


def setConfRestartWeb():
    autoMakeConfig(True, False)
    mw.opWeb('stop')
    mw.opWeb('start')


def restartWeb():
    mw.opWeb('stop')
    mw.opWeb('start')


def makeOpDstRunLua(conf_reload=False):
    root_init_dir = mw.getServerDir() + '/web_conf/nginx/lua/init_by_lua_file'
    root_worker_dir = mw.getServerDir() + '/web_conf/nginx/lua/init_worker_by_lua_file'
    root_access_dir = mw.getServerDir() + '/web_conf/nginx/lua/access_by_lua_file'
    path = getServerDir()
    path_tpl = getPluginDir()

    waf_common_dst = path + "/waf/lua/waf_common.lua"
    if not os.path.exists(waf_common_dst) or conf_reload:
        waf_common_tpl = path_tpl + "/waf/lua/waf_common.lua"
        content = mw.readFile(waf_common_tpl)
        content = contentReplace(content)
        mw.writeFile(waf_common_dst, content)

    waf_init_dst = root_init_dir + "/waf_init_preload.lua"
    if not os.path.exists(waf_init_dst) or conf_reload:
        waf_init_tpl = path_tpl + "/waf/lua/init_preload.lua"
        content = mw.readFile(waf_init_tpl)
        content = contentReplace(content)
        mw.writeFile(waf_init_dst, content)

    init_worker_dst = root_worker_dir + '/opwaf_init_worker.lua'
    if not os.path.exists(init_worker_dst) or conf_reload:
        init_worker_tpl = path_tpl + "/waf/lua/init_worker.lua"
        content = mw.readFile(init_worker_tpl)
        content = contentReplace(content)
        mw.writeFile(init_worker_dst, content)

    access_file_dst = root_access_dir + '/opwaf_init.lua'
    if not os.path.exists(access_file_dst) or conf_reload:
        access_file_tpl = path_tpl + "/waf/lua/init.lua"
        access_file_dst_s = path + "/waf/lua/init.lua"
        content = mw.readFile(access_file_tpl)
        content = contentReplace(content)
        mw.writeFile(access_file_dst, content)
        mw.writeFile(access_file_dst_s, content)

    waf_mmdb_dst = path + "/waf/lua/waf_maxminddb.lua"
    if not os.path.exists(waf_mmdb_dst) or conf_reload:
        waf_mmdb_tpl = path_tpl + "/waf/lua/waf_maxminddb.lua"
        content = mw.readFile(waf_mmdb_tpl)
        content = contentReplace(content)
        mw.writeFile(waf_mmdb_dst, content)

    mw.opLuaMakeAll()
    return True


def makeOpDstStopLua():
    root_init_dir = mw.getServerDir() + '/web_conf/nginx/lua/init_by_lua_file'
    root_worker_dir = mw.getServerDir() + '/web_conf/nginx/lua/init_worker_by_lua_file'
    root_access_dir = mw.getServerDir() + '/web_conf/nginx/lua/access_by_lua_file'

    waf_init_dst = root_init_dir + "/waf_init_preload.lua"
    if os.path.exists(waf_init_dst):
        os.remove(waf_init_dst)

    init_worker_dst = root_worker_dir + '/opwaf_init_worker.lua'
    if os.path.exists(init_worker_dst):
        os.remove(init_worker_dst)

    access_file_dst = root_access_dir + '/opwaf_init.lua'
    if os.path.exists(access_file_dst):
        os.remove(access_file_dst)

    wafconf = dstWafConfPath()
    if os.path.exists(wafconf):
        os.remove(wafconf)

    mw.opLuaMakeAll()
    return True


def initDreplace():
    path = getServerDir()
    if not os.path.exists(path + '/waf/lua'):
        sdir = getPluginDir() + '/waf'
        cmd = 'cp -rf ' + sdir + ' ' + path
        mw.execShell(cmd)

    logs_path = path + '/logs'
    if not os.path.exists(logs_path):
        mw.execShell('mkdir -p ' + logs_path)

    debug_log = path + '/debug.log'
    if not os.path.exists(debug_log):
        mw.execShell('echo "" > ' + debug_log)

    config = path + '/waf/config.json'
    content = mw.readFile(config)
    content = json.loads(content)
    content['reqfile_path'] = path + "/waf/html"
    mw.writeFile(config, mw.getJson(content))

    makeOpDstRunLua()

    waf_conf = dstWafConfPath()
    if not os.path.exists(waf_conf):
        waf_tpl = getPluginDir() + "/conf/luawaf.conf"
        content = mw.readFile(waf_tpl)
        content = contentReplace(content)
        mw.writeFile(waf_conf, content)

    autoMakeConfig(True, False)

    pSqliteDb()

    if not mw.isAppleSystem():
        mw.execShell("chown -R www:www " + path)
    return path


def status():
    path = getConf()
    if not os.path.exists(path):
        return 'stop'

    waf_conf = dstWafConfPath()
    if not os.path.exists(waf_conf):
        return 'stop'
    return 'start'


def start():
    initDreplace()

    import tool_task
    tool_task.createBgTask()

    restartWeb()
    return 'ok'


def stop():

    makeOpDstStopLua()

    import tool_task
    tool_task.removeBgTask()

    restartWeb()
    return 'ok'


def restart():
    restartWeb()
    return 'ok'


def reload():
    mw.opWeb('stop')

    makeOpDstRunLua(True)
    autoMakeConfig(True, False)

    elog = mw.getServerDir() + "/openresty/nginx/logs/error.log"
    if os.path.exists(elog):
        mw.execShell('rm -rf ' + elog)

    mw.opWeb('start')
    return 'ok'

def reload_hook():
    s = status()
    if s == 'start':
        return reload()
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

    setConfRestartWeb()
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

    setConfRestartWeb()
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

    setConfRestartWeb()
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

    setConfRestartWeb()
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

    setConfRestartWeb()
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
    setConfRestartWeb()
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

    setConfRestartWeb()
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

    setConfRestartWeb()
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

    setConfRestartWeb()
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
    setConfRestartWeb()
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

    setConfRestartWeb()
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

    setConfRestartWeb()
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
    status = int(args['statusCode'])
    cobj[o]['status'] = status

    cjson = mw.getJson(cobj)
    mw.writeFile(conf, cjson)

    setConfRestartWeb()
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
    
    ## 修复数据类型错误
    tmp = args
    tmp['retry'] = int(tmp['retry'])
    tmp['retry_time'] = int(tmp['retry_time'])
    tmp['retry_cycle'] = int(tmp['retry_cycle'])
    
    cobj['retry'] = tmp
    cjson = mw.getJson(cobj)
    mw.writeFile(conf, cjson)

    setConfRestartWeb()
    return mw.returnJson(True, '设置成功!', [])


def setSafeVerify():
    args = getArgs()
    data = checkArgs(args, ['auto', 'time', 'cpu', 'mode'])
    if not data[0]:
        return data[1]

    conf = getJsonPath('config')
    content = mw.readFile(conf)
    cobj = json.loads(content)

    cobj['safe_verify']['time'] = args['time']
    cobj['safe_verify']['cpu'] = int(args['cpu'])
    cobj['safe_verify']['mode'] = args['mode']

    if args['auto'] == '0':
        cobj['safe_verify']['auto'] = False
    else:
        cobj['safe_verify']['auto'] = True

    cjson = mw.getJson(cobj)
    mw.writeFile(conf, cjson)

    setConfRestartWeb()
    return mw.returnJson(True, '设置成功!', [])


def setSiteRetry():
    return mw.returnJson(True, '设置成功-?!', [])


def setCcConf():
    args = getArgs()
    data = checkArgs(args, ['siteName', 'cycle', 'limit',
                            'endtime', 'is_open_global'])
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

    setConfRestartWeb()
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

    setConfRestartWeb()
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

    setConfRestartWeb()
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

    setConfRestartWeb()
    return mw.returnJson(True, '删除成功!')


def outputData():
    args = getArgs()
    data = checkArgs(args, ['sname'])
    if not data[0]:
        return data[1]

    path = getRuleJsonPath(args['sname'])
    content = mw.readFile(path)
    return mw.returnJson(True, 'ok', content)


def importData():
    args = getArgs()
    data = checkArgs(args, ['sname', 'pdata'])
    if not data[0]:
        return data[1]

    path = getRuleJsonPath(args['sname'])

    source_data = mw.readFile(path)
    source_data = json.loads(source_data)

    save_data = []
    save_data.append(source_data[0])
    pdata = args['pdata'].strip()
    try:
        pdata = json.loads(pdata)
        mw.writeFile(path, json.dumps(pdata))
    except Exception as e:
        pdata = pdata.split("\\n")
        for x in pdata:
            pval = x.strip()
            if pval != "":
                vv = json.loads(pval)
                save_data.append(vv[0])
        mw.writeFile(path, json.dumps(save_data))
    # restartWeb()
    return mw.returnJson(True, '设置成功!')


def getLogsList():
    args = getArgs()
    data = checkArgs(args, ['site', 'page', 'page_size', 'tojs'])
    if not data[0]:
        return data[1]

    page = int(args['page'])
    page_size = int(args['page_size'])
    domain = args['site']
    tojs = args['tojs']

    setDefaultSite(domain)

    conn = pSqliteDb('logs')

    field = 'time,ip,domain,server_name,method,uri,user_agent,rule_name,reason'
    limit = str(page_size) + ' offset ' + str(page_size * (page - 1))

    condition = ''
    conn = conn.field(field)
    conn = conn.where("1=1", ()).where("domain=?", (domain,))

    clist = conn.limit(limit).order('time desc').inquiry()
    count_key = "count(*) as num"
    count = conn.field(count_key).limit('').order('').inquiry()
    # print(count)
    count = count[0][count_key]

    data = {}
    _page = {}
    _page['count'] = count
    _page['p'] = page
    _page['row'] = page_size
    _page['tojs'] = tojs
    data['page'] = mw.getPage(_page)
    data['data'] = clist

    return mw.returnJson(True, 'ok!', data)


def getSafeLogs():
    args = getArgs()
    data = checkArgs(args, ['siteName', 'toDate', 'p'])
    if not data[0]:
        return data[1]

    path = getServerDir() + '/logs'
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
    setConfRestartWeb()
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
    setConfRestartWeb()
    return mw.returnJson(True, '设置成功!')


def getWafSrceen():
    conf = getJsonPath('total')
    return mw.readFile(conf)


def getWafConf():
    conf = getJsonPath('config')
    return mw.readFile(conf)


def areaLimitSwitch():
    args = getArgs()
    data = checkArgs(args, ['area_limit'])
    if not data[0]:
        return data[1]

    path_config = getJsonPath('config')

    config_contents = mw.readFile(path_config)
    config_contents = json.loads(config_contents)

    msg = '关闭成功!'
    if args['area_limit'] == 'on':
        msg = '开启成功!'
        config_contents['area_limit'] = True
    else:
        config_contents['area_limit'] = False

    mw.writeFile(path_config, json.dumps(config_contents))

    autoMakeConfig(True, True)
    restart()
    return mw.returnJson(True, msg)


def getAreaLimit():
    conf = getJsonPath('area_limit')
    if not os.path.exists(conf):
        mw.writeFile(conf, '[]')

    d = mw.readFile(conf)
    data = json.loads(d)
    return mw.returnJson(True, 'ok!', data)


def delAreaLimit():
    args = getArgs()
    data = checkArgs(args, ['site', 'types', 'region'])
    if not data[0]:
        return data[1]

    type_list = ["refuse", "accept"]
    if not args['types'] in type_list:
        return mw.returnJson(False, '输入的类型错误!')

    region_l = args['region'].split(",")
    site_l = args['site'].split(",")

    paramMode = {}
    for i in region_l:
        if not i:
            continue
        i = i.strip()
        if not i in paramMode:
            paramMode[i] = "1"

    sitesMode = {}
    for i in site_l:
        i = i.strip()
        if not i:
            continue

        if not i in sitesMode:
            sitesMode[i] = "1"

    if len(paramMode) == 0:
        return mw.returnJson(False, '输入的请求类型错误!')
    if len(sitesMode) == 0:
        return mw.returnJson(False, '输入的站点错误!')

    conf = getJsonPath('area_limit')
    t_data = json.loads(mw.readFile(conf))

    data = {"site": sitesMode, "types": args['types'], "region": paramMode}
    if not data in t_data:
        return mw.returnJson(False, '不存在!')

    t_data.remove(data)
    mw.writeFile(conf, json.dumps(t_data))

    setConfRestartWeb()
    return mw.returnJson(True, '删除成功!')


def addAreaLimit():
    args = getArgs()
    data = checkArgs(args, ['site', 'types', 'region'])
    if not data[0]:
        return data[1]

    type_list = ["refuse", "accept"]
    if not args['types'] in type_list:
        return mw.returnJson(False, '输入的类型错误!')

    region_l = args['region'].split(",")
    site_l = args['site'].split(",")

    paramMode = {}
    for i in region_l:
        if not i:
            continue
        i = i.strip()
        if not i in paramMode:
            paramMode[i] = "1"

    if '海外' in paramMode and '中国' in paramMode:
        return mw.returnJson(False, '不允许设置【中国大陆】和【中国大陆以外地区】一同开启地区限制!')

    sitesMode = {}
    for i in site_l:
        i = i.strip()
        if not i:
            continue

        if not i in sitesMode:
            sitesMode[i] = "1"

    if len(paramMode) == 0:
        return mw.returnJson(False, '输入的请求类型错误!')
    if len(sitesMode) == 0:
        return mw.returnJson(False, '输入的站点错误!')

    conf = getJsonPath('area_limit')
    t_data = json.loads(mw.readFile(conf))

    data = {"site": sitesMode, "types": args['types'], "region": paramMode}
    if data in t_data:
        return mw.returnJson(False, '已存在!')

    t_data.insert(0, data)
    mw.writeFile(conf, json.dumps(t_data))

    setConfRestartWeb()
    return mw.returnJson(True, '添加成功!')


def cleanDropIp():
    url = "http://127.0.0.1/clean_waf_drop_ip"
    data = mw.httpGet(url)
    return mw.returnJson(True, 'ok!', data)


def testRun():
    # args = getArgs()
    # data = checkArgs(args, ['siteName'])
    # if not data[0]:
    #     return data[1]

    default_path = getServerDir() + "/waf/default.pl"
    default_site = mw.readFile(default_path)
    url = "http://" + default_site + '/?t=../etc/passwd'
    returnData = mw.httpGet(url, 10)

    # url = "https://" + default_site + '/?t=../etc/passwd'
    # returnData = mw.httpGet(url, 3)
    return mw.returnJson(True, '测试运行成功!', returnData)


def installPreInspection():
    check_op = mw.getServerDir() + "/openresty"
    if not os.path.exists(check_op):
        return "请先安装OpenResty"
    return 'ok'


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
    elif func == 'install_pre_inspection':
        print(installPreInspection())
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
    elif func == 'set_safe_verify':
        print(setSafeVerify())
    elif func == 'set_site_retry':
        print(setSiteRetry())
    elif func == 'save_scan_rule':
        print(saveScanRule())
    elif func == 'get_site_config':
        print(getSiteConfig())
    elif func == 'get_default_site':
        print(getDefaultSite())
    elif func == 'get_country':
        print(getCountry())
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
    elif func == 'area_limit_switch':
        print(areaLimitSwitch())
    elif func == 'get_area_limit':
        print(getAreaLimit())
    elif func == 'add_area_limit':
        print(addAreaLimit())
    elif func == 'del_area_limit':
        print(delAreaLimit())
    elif func == 'clean_drop_ip':
        print(cleanDropIp())
    elif func == 'test_run':
        print(testRun())
    else:
        print('error')
