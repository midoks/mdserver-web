# coding:utf-8

import sys
import io
import os
import time

from datetime import datetime

try:
    import dns.resolver
except:
    if os.path.exists(os.getcwd() + '/bin'):
        mw.mw(os.getcwd() + '/bin/pip install dnspython')
    else:
        mw.execShell('pip install dnspython')
    import dns.resolver


sys.path.append(os.getcwd() + "/class/core")

import mw
app_debug = False
if mw.isAppleSystem():
    app_debug = True


class App:
    __setupPath = '/www/server/mail'
    __session_conf = __setupPath + '/session.json'

    _check_time = 86400

    def __init__(self):
        self.__setupPath = self.getServerDir()
        self._session = self.__get_session()

    def getArgs(self):
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

    def __get_session(self):
        session = mw.readFile(self.__session_conf)
        if session:
            session = json.loads(session)
        else:
            session = {}
        return session

    def __get_dkim_value(self, domain):
        '''
        解析/etc/opendkim/keys/domain/default.txt得到域名要设置的dkim记录值
        :param domain:
        :return:
        '''
        if not os.path.exists("/www/server/dkim/{}".format(domain)):
            os.makedirs("/www/server/dkim/{}".format(domain))
        rspamd_pub_file = '/www/server/dkim/{}/default.pub'.format(domain)
        opendkim_pub_file = '/etc/opendkim/keys/{0}/default.txt'.format(domain)
        if os.path.exists(opendkim_pub_file) and not os.path.exists(rspamd_pub_file):
            opendkim_pub = mw.readFile(opendkim_pub_file)
            mw.writeFile(rspamd_pub_file, opendkim_pub)

            rspamd_pri_file = '/www/server/dkim/{}/default.private'.format(
                domain)
            opendkim_pri_file = '/etc/opendkim/keys/{}/default.private'.format(
                domain)
            opendkim_pri = mw.readFile(opendkim_pri_file)
            mw.writeFile(rspamd_pri_file, opendkim_pri)

        if not os.path.exists(rspamd_pub_file):
            return ''
        file_body = mw.readFile(rspamd_pub_file).replace(
            ' ', '').replace('\n', '').split('"')
        value = file_body[1] + file_body[3]
        return value

    def __check_mx(self, domain):
        '''
        检测域名是否有mx记录
        :param domain:
        :return:
        '''
        a_record = self.M('domain').where(
            'domain=?', (domain,)).field('a_record').find()['a_record']
        key = '{0}:{1}'.format(domain, 'MX')
        now = int(time.time())
        try:
            value = ""
            if key in self._session and self._session[key]["status"] != 0:
                v_time = now - int(self._session[key]["v_time"])
                if v_time < self._check_time:
                    value = self._session[key]["value"]
            if '' == value:
                resolver = dns.resolver.Resolver()
                resolver.timeout = 1
                try:
                    result = resolver.resolve(domain, 'MX')
                except:
                    result = resolver.query(domain, 'MX')

                value = str(result[0].exchange).strip('.')
            if not a_record:
                a_record = value
                self.M('domain').where('domain=?', (domain,)).save(
                    'a_record', (a_record,))
            if value == a_record:
                self._session[key] = {"status": 1,
                                      "v_time": now, "value": value}
                return True
            self._session[key] = {"status": 0, "v_time": now, "value": value}
            return False
        except:
            # print(public.get_error_info())
            self._session[key] = {"status": 0, "v_time": now,
                                  "value": "None of DNS query names exist:{}".format(domain)}
            return False

    def __check_spf(self, domain):
        '''
        检测域名是否有spf记录
        :param domain:
        :return:
        '''
        key = '{0}:{1}'.format(domain, 'TXT')
        now = int(time.time())
        try:
            value = ""
            if key in self._session and self._session[key]["status"] != 0:
                v_time = now - int(self._session[key]["v_time"])
                if v_time < self._check_time:
                    value = self._session[key]["value"]
            if '' == value:
                resolver = dns.resolver.Resolver()
                resolver.timeout = 1
                # try:
                result = resolver.resolve(domain, 'TXT')
                # except:
                #     result = resolver.query(domain, 'TXT')

                for i in result.response.answer:
                    for j in i.items:
                        value += str(j).strip()
            if 'v=spf1' in value.lower():
                self._session[key] = {"status": 1,
                                      "v_time": now, "value": value}
                return True
            self._session[key] = {"status": 0, "v_time": now, "value": value}
            return False
        except:
            # print(public.get_error_info())
            self._session[key] = {"status": 0, "v_time": now,
                                  "value": "None of DNS query spf exist:{}".format(domain)}
            return False

    def __check_dkim(self, domain):
        '''
        检测域名是否有dkim记录
        :param domain:
        :return:
        '''
        origin_domain = domain
        domain = 'default._domainkey.{0}'.format(domain)
        key = '{0}:{1}'.format(domain, 'TXT')
        now = int(time.time())
        try:
            value = ""
            if key in self._session and self._session[key]["status"] != 0:
                v_time = now - int(self._session[key]["v_time"])
                if v_time < self._check_time:
                    value = self._session[key]["value"]
            if '' == value:
                resolver = dns.resolver.Resolver()
                resolver.timeout = 1
                result = resolver.resolve(domain, 'TXT')
                for i in result.response.answer:
                    for j in i.items:
                        value += str(j).strip()
            new_v = self._get_dkim_value(origin_domain)
            if new_v and new_v in value:
                self._session[key] = {"status": 1,
                                      "v_time": now, "value": value}
                return True
            self._session[key] = {"status": 0, "v_time": now, "value": value}
            return False
        except:
            # print(public.get_error_info())
            self._session[key] = {"status": 0, "v_time": now,
                                  "value": "None of DNS query names exist:{}".format(domain)}
            return False

    def __check_dmarc(self, domain):
        '''
        检测域名是否有dmarc记录
        :param domain:
        :return:
        '''
        domain = '_dmarc.{0}'.format(domain)
        key = '{0}:{1}'.format(domain, 'TXT')
        now = int(time.time())
        try:
            value = ""
            if key in self._session and self._session[key]["status"] != 0:
                v_time = now - int(self._session[key]["v_time"])
                if v_time < self._check_time:
                    value = self._session[key]["value"]
            if '' == value:
                resolver = dns.resolver.Resolver()
                resolver.timeout = 1

                result = resolver.resolve(domain, 'TXT')

                for i in result.response.answer:
                    for j in i.items:
                        value += str(j).strip()
            if 'v=dmarc1' in value.lower():
                self._session[key] = {"status": 1,
                                      "v_time": now, "value": value}
                return True
            self._session[key] = {"status": 0, "v_time": now, "value": value}
            return False
        except:
            # print(public.get_error_info())
            self._session[key] = {"status": 0, "v_time": now,
                                  "value": "None of DNS query names exist:{}".format(domain)}
            return False

    def __gevent_jobs(self, domain, a_record):
        from gevent import monkey
        # monkey.patch_all()
        import gevent
        gevent.joinall([
            gevent.spawn(self.__check_mx, domain),
            gevent.spawn(self.__check_spf, domain),
            gevent.spawn(self.__check_dkim, domain),
            gevent.spawn(self.__check_dmarc, domain),
            gevent.spawn(self.__check_a, a_record),
        ])

        return True

    def getInitDFile(self):
        if app_debug:
            return '/tmp/' + getPluginName()
        return '/etc/init.d/' + getPluginName()

    def getPluginName(self):
        return 'mail'

    def getPluginDir(self):
        return mw.getPluginDir() + '/' + self.getPluginName()

    def getServerDir(self):
        return mw.getServerDir() + '/' + self.getPluginName()

    def M(self, dbname='domain'):
        file = self.getServerDir() + '/postfixadmin.db'
        name = 'mail'
        if not os.path.exists(file):
            conn = mw.M(dbname).dbPos(self.getServerDir(), name)
            csql = mw.readFile(self.getPluginDir() + '/conf/postfixadmin.sql')
            csql_list = csql.split(';')
            for index in range(len(csql_list)):
                conn.execute(csql_list[index], ())
        else:
            # 现有run
            # conn = mw.M(dbname).dbPos(getServerDir(), name)
            # csql = mw.readFile(getPluginDir() + '/conf/mysql.sql')
            # csql_list = csql.split(';')
            # for index in range(len(csql_list)):
            #     conn.execute(csql_list[index], ())
            conn = mw.M(dbname).dbPos(self.getServerDir(), name)
        return conn

    def status(self):
        return 'start'

    def get_domains(self):
        args = self.getArgs()

        p = int(args['p']) if 'p' in args else 1
        rows = int(args['size']) if 'size' in args else 10
        callback = args['callback'] if 'callback' in args else ''
        count = self.M('domain').count()

        data = {}
        # 获取分页数据
        _page = {}
        _page['count'] = count
        _page['p'] = p
        _page['row'] = rows
        _page['tojs'] = callback
        data['page'] = mw.getPage(_page)

        start_pos = (_page['p'] - 1) * _page['row']

        data_list = self.M('domain').order('created desc').limit(
            str(start_pos) + ',' + str(_page['row'])).field('domain,a_record,created,active').select()

        # print(data)
        # print(data_list)

        return mw.returnJson(True, 'ok', {'data': data_list, 'page': data['page']})

    def runLog(self):
        path = '/var/log/maillog'
        # if "ubuntu" in:
        #     path = '/var/log/mail.log'
        return path

    def add_domain(self):
        args = self.getArgs()

        if 'domain' not in args:
            return mw.returnJson(False, '请传入域名')

        domain = args['domain']
        a_record = args['a_record']

        if not a_record.endswith(domain):
            return mw.returnJson(False, 'A记录 [{}] 不属于该域名'.format(a_record))

        if not mw.isDebugMode():
            check = self.__check_a(a_record)
            if not check[0]:
                return mw.returnJson(False, 'A记录解析失败<br>域名：{}<br>IP：{}'.format(a_record, check[1]['value']))

        if self.M('domain').where("domain=?", (domain,)).count() > 0:
            return mw.returnJson(False, '该域名已存在')

        cur_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            self.M('domain').add('domain,a_record,created',
                                 (domain, a_record, cur_time))
        except:
            return mw.returnJson(False, '邮局没有初始化成功！<br>'
                                 '请尝试重新初始化,<br>'
                                 '如果以下端口没访问将无法初始化 <br>port 25 [outbound direction]<br> '
                                 '你可以尝试执行以下命令测试端口是否开启:<br><br> [ telnet gmail-smtp-in.l.google.com 25 ] <br> ')

        # 在虚拟用户家目录创建对应域名的目录
        if os.path.exists('/www/vmail'):
            if not os.path.exists('/www/vmail/{0}'.format(domain)):
                os.makedirs('/www/vmail/{0}'.format(domain))
            mw.execShell('chown -R vmail:mail /www/vmail/{0}'.format(domain))
        return mw.returnJson(False, 'OK')

    def __check_a(self, hostname):
        key = '{0}:{1}'.format(hostname, 'A')
        now = int(time.time())

        value = ""
        error_ip = ""

        ipaddress = mw.getLocalIp()
        if not ipaddress:
            return False, {"status": 0, "v_time": now, "value": error_ip}

        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 1
            try:
                result = resolver.resolve(hostname, 'A')
            except:
                result = resolver.query(hostname, 'A')

            for i in result.response.answer:
                for j in i.items:
                    error_ip = j
                    if str(j).strip() in ipaddress:
                        value = str(j).strip()

            if value:
                return True, {"status": 1, "v_time": now, "value": value}
            return False, {"status": 0, "v_time": now, "value": error_ip}
        except Exception as e:
            raise e
        return False, {"status": 0, "v_time": now, "value": error_ip}

    def flush_domain_record(self):
        '''
        手动刷新域名记录
        domain all/specify.com
        :param args:
        :return:
        '''
        args = self.getArgs()

        if args['domain'] == 'all':
            data_list = self.M('domain').order('created desc').field(
                'domain,a_record,created,active').select()
            for item in data_list:
                # try:
                #     if os.path.exists("/usr/bin/rspamd"):
                #         self.set_rspamd_dkim_key(item['domain'])
                #     if os.path.exists("/usr/sbin/opendkim"):
                #         self._gen_dkim_key(item['domain'])
                # except:
                #     return mw.returnJson(False, '请检查Rspamd服务器是否已经启动！')
                self.__gevent_jobs(item['domain'], item['a_record'])
        # else:
        #     try:
        #         if os.path.exists("/usr/bin/rspamd"):
        #             self.set_rspamd_dkim_key(args.domain)
        #         if os.path.exists("/usr/sbin/opendkim"):
        #             self._gen_dkim_key(args.domain)
        #     except:
        #         return mw.returnJson(False, '请检查Rspamd服务器是否已经启动！')
        #     self._gevent_jobs(args['domain'], None)  # 不需要验证A记录

        # mw.writeFile(self._session_conf, json.dumps(self._session))

        return mw.returnJson(True, '刷新成功！')


if __name__ == "__main__":
    func = sys.argv[1]
    classApp = App()
    data = eval("classApp." + func + "()")
    print(data)
