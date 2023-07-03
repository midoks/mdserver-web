# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------
# 证书申请
# ---------------------------------------------------------------------------------

import re
import fcntl
import datetime
import binascii
import hashlib
import base64
import json
import time
import os
import sys
import argparse

if os.path.exists('/www/server/mdserver-web'):
    os.chdir('/www/server/mdserver-web')

import mw

try:
    import OpenSSL
except:
    mw.execShell("pip install pyopenssl")
    import OpenSSL

# import http_requests as requests
# requests.DEFAULT_TYPE = 'curl'
import requests
requests.packages.urllib3.disable_warnings()


def echoErr(msg):
    writeLog("\033[31m=" * 65)
    writeLog("|-错误：{}\033[0m".format(msg))
    exit()


def writeLog(log_str, mode="ab+"):
    # 写日志
    if __name__ == "__main__":
        print(log_str)
        return
    _log_file = 'logs/letsencrypt.log'
    f = open(_log_file, mode)
    log_str += "\n"
    f.write(log_str.encode('utf-8'))
    f.close()
    return True


class cert_request:
    __debug = False
    __user_agent = "MW-Panel"
    __apis = None
    __url = None
    __replay_nonce = None
    __acme_timeout = 30
    __max_check_num = 5
    __wait_time = 5
    __bits = 2048
    __digest = "sha256"
    __verify = False
    __config = {}
    __dns_class = None
    __auto_wildcard = False
    __mod_index = {True: "Staging", False: "Production"}
    __save_path = 'data/letsencrypt'
    __cfg_file = 'data/letsencrypt.json'

    def __init__(self):
        self.__save_path = mw.getServerDir() + '/web_conf/letsencrypt'
        if not os.path.exists(self.__save_path):
            os.makedirs(self.__save_path)
        if self.__debug:
            self.__url = 'https://acme-staging-v02.api.letsencrypt.org/directory'
        else:
            self.__url = 'https://acme-v02.api.letsencrypt.org/directory'
        self.__config = self.readConfig()

    def D(self, name, val):
        if self.__debug:
            print('---------{} start--------'.format(name))
            print(val)
            print('---------{} end--------'.format(name))

    # 读配置文件
    def readConfig(self):
        if not os.path.exists(self.__cfg_file):
            self.__config['orders'] = {}
            self.__config['account'] = {}
            self.__config['apis'] = {}
            self.__config['email'] = mw.M('users').where(
                'id=?', (1,)).getField('email')
            if self.__config['email'] in ['midoks@163.com']:
                self.__config['email'] = None
            self.saveConfig()
            return self.__config
        tmp_config = mw.readFile(self.__cfg_file)
        if not tmp_config:
            return self.__config
        try:
            self.__config = json.loads(tmp_config)
        except:
            self.saveConfig()
            return self.__config
        return self.__config

    # 写配置文件
    def saveConfig(self):
        fp = open(self.__cfg_file, 'w+')
        fcntl.flock(fp, fcntl.LOCK_EX)  # 加锁
        fp.write(json.dumps(self.__config))
        fcntl.flock(fp, fcntl.LOCK_UN)  # 解锁
        fp.close()
        return True

    def getApis(self):
        if not self.__apis:
                # 尝试从配置文件中获取
            api_index = self.__mod_index[self.__debug]
            if not 'apis' in self.__config:
                self.__config['apis'] = {}

            if api_index in self.__config['apis']:
                if 'expires' in self.__config['apis'][api_index] and 'directory' in self.__config['apis'][api_index]:
                    if time.time() < self.__config['apis'][api_index]['expires']:
                        self.__apis = self.__config[
                            'apis'][api_index]['directory']
                        return self.__apis

            # 尝试从官方获取获取
            try:
                res = mw.httpGet(self.__url)
                result = json.loads(res)
                self.__apis = {}
                self.__apis['newAccount'] = result['newAccount']
                self.__apis['newNonce'] = result['newNonce']
                self.__apis['newOrder'] = result['newOrder']
                self.__apis['revokeCert'] = result['revokeCert']
                self.__apis['keyChange'] = result['keyChange']

                # 保存到配置文件
                self.__config['apis'][api_index] = {}
                self.__config['apis'][api_index]['directory'] = self.__apis
                self.__config['apis'][api_index]['expires'] = time.time() + \
                    86400  # 24小时后过期
                self.saveConfig()
            except Exception as e:
                raise Exception(
                    '服务因维护而关闭或发生内部错误，查看 <a href="https://letsencrypt.status.io/" target="_blank" class="btlink">https://letsencrypt.status.io/</a> 了解更多详细信息。')
        return self.__apis

    # 系列化payload
    def stringfyItems(self, payload):
        if isinstance(payload, str):
            return payload

        for k, v in payload.items():
            if isinstance(k, bytes):
                k = k.decode("utf-8")
            if isinstance(v, bytes):
                v = v.decode("utf-8")
            payload[k] = v
        return payload

    # 构造域名列表
    def formatDomains(self, domains):
        if type(domains) != list:
            return []
        # 是否自动构造通配符
        if self.__auto_wildcard:
            domains = self.autoWildcard(domains)
        wildcard = []
        tmp_domains = []
        for domain in domains:
            domain = domain.strip()
            if domain in tmp_domains:
                continue
            # 将通配符域名转为验证正则表达式
            f_index = domain.find("*.")
            if f_index not in [-1, 0]:
                continue
            if f_index == 0:
                wildcard.append(domain.replace(
                    "*", r"^[\w-]+").replace(".", r"\."))
            # 添加到申请列表
            tmp_domains.append(domain)

        # 处理通配符包含
        apply_domains = tmp_domains[:]
        for domain in tmp_domains:
            for w in wildcard:
                if re.match(w, domain):
                    apply_domains.pop(domain)

        return apply_domains

    # 转为无填充的Base64
    def calculateSafeBase64(self, un_encoded_data):
        if sys.version_info[0] == 3:
            if isinstance(un_encoded_data, str):
                un_encoded_data = un_encoded_data.encode("utf8")
        r = base64.urlsafe_b64encode(un_encoded_data).rstrip(b"=")
        return r.decode("utf8")

    # 创建Key
    def createKey(self, key_type=OpenSSL.crypto.TYPE_RSA):
        key = OpenSSL.crypto.PKey()
        key.generate_key(key_type, self.__bits)
        private_key = OpenSSL.crypto.dump_privatekey(
            OpenSSL.crypto.FILETYPE_PEM, key)
        return private_key

       # 获用户取密钥对
    def getAccountKey(self):
        if not 'account' in self.__config:
            self.__config['account'] = {}
        k = self.__mod_index[self.__debug]
        if not k in self.__config['account']:
            self.__config['account'][k] = {}

        if not 'key' in self.__config['account'][k]:
            self.__config['account'][k]['key'] = self.createKey()
            if type(self.__config['account'][k]['key']) == bytes:
                self.__config['account'][k]['key'] = self.__config[
                    'account'][k]['key'].decode()
            self.saveConfig()
        return self.__config['account'][k]['key']

    # 注册acme帐户
    def register(self, existing=False):
        if not 'email' in self.__config:
            self.__config['email'] = 'mdioks@163.com'
        if existing:
            payload = {"onlyReturnExisting": True}
        elif self.__config['email']:
            payload = {
                "termsOfServiceAgreed": True,
                "contact": ["mailto:{0}".format(self.__config['email'])],
            }
        else:
            payload = {"termsOfServiceAgreed": True}

        res = self.acmeRequest(url=self.__apis['newAccount'], payload=payload)

        if res.status_code not in [201, 200, 409]:
            raise Exception("注册ACME帐户失败: {}".format(res.json()))
        kid = res.headers["Location"]
        return kid

    # 获取kid
    def getKid(self, force=False):
        # 如果配置文件中不存在kid或force = True时则重新注册新的acme帐户
        if not 'account' in self.__config:
            self.__config['account'] = {}
        k = self.__mod_index[self.__debug]
        if not k in self.__config['account']:
            self.__config['account'][k] = {}

        if not 'kid' in self.__config['account'][k]:
            self.__config['account'][k]['kid'] = self.register()
            self.saveConfig()
            time.sleep(3)
            self.__config = self.readConfig()
        return self.__config['account'][k]['kid']

    # 获取随机数
    def getNonce(self, force=False):
        return '1AADXO5Sdc3EzuOS8ViYj-MVdhgx3DRE2kSDSwrObJ1jG_w'
        # 如果没有保存上一次的随机数或force=True时则重新获取新的随机数
        if not self.__replay_nonce or force:
            try:

                import urllib.request
                try:
                    response = urllib.request.urlopen(self.__apis['newNonce'],
                                                      timeout=self.__acme_timeout,
                                                      headers=headers,
                                                      verify=self.__verify)
                    self.__replay_nonce = response.headers["replay-nonce"]
                    return self.__replay_nonce
                except Exception as e:
                    pass

                headers = {"User-Agent": self.__user_agent}
                response = requests.get(self.__apis['newNonce'],
                                        timeout=self.__acme_timeout,
                                        headers=headers,
                                        verify=self.__verify)

                self.__replay_nonce = response.headers["replay-nonce"]
            except Exception as e:
                raise Exception("获取随机数失败: {}".format(str(e)))

        return self.__replay_nonce

    # 获请ACME请求头
    def getAcmeHeader(self, url):
        nonce = self.getNonce()

        header = {"alg": "RS256", "nonce": nonce, "url": url}
        if url in [self.__apis['newAccount'], 'GET_THUMBPRINT']:
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import serialization
            private_key = serialization.load_pem_private_key(
                self.getAccountKey().encode(),
                password=None,
                backend=default_backend(),
            )
            public_key_public_numbers = private_key.public_key().public_numbers()

            exponent = "{0:x}".format(public_key_public_numbers.e)
            exponent = "0{0}".format(exponent) if len(
                exponent) % 2 else exponent
            modulus = "{0:x}".format(public_key_public_numbers.n)
            jwk = {
                "kty": "RSA",
                "e": self.calculateSafeBase64(binascii.unhexlify(exponent)),
                "n": self.calculateSafeBase64(binascii.unhexlify(modulus)),
            }
            header["jwk"] = jwk
        else:
            header["kid"] = self.getKid()
        return header

    # 计算signature
    def signMessage(self, message):
        pk = OpenSSL.crypto.load_privatekey(
            OpenSSL.crypto.FILETYPE_PEM, self.getAccountKey().encode())
        return OpenSSL.crypto.sign(pk, message.encode("utf8"), self.__digest)

    def getSiteRunPathByid(self, site_id):
        if mw.M('sites').where('id=?', (site_id,)).count() >= 1:
            site_path = mw.M('sites').where('id=?', site_id).getField('path')
            if not site_path:
                return None
            if not os.path.exists(site_path):
                return None
            args = mw.dict_obj()
            args.id = site_id
            import panelSite
            run_path = panelSite.panelSite().GetRunPath(args)
            if run_path in ['/']:
                run_path = ''
            if run_path:
                if run_path[0] == '/':
                    run_path = run_path[1:]
            site_run_path = os.path.join(site_path, run_path)
            if not os.path.exists(site_run_path):
                return site_path
            return site_run_path
        else:
            return False

    def getSiteRunPath(self, domains):
        site_id = 0
        for domain in domains:
            site_id = mw.M('domain').where("name=?", domain).getField('pid')
            if site_id:
                break

        if not site_id:
            return None
        return self.getSiteRunPathByid(site_id)

    # 清理验证文件
    def claerAuthFile(self, index):
        if not self.__config['orders'][index]['auth_type'] in ['http', 'tls']:
            return True
        acme_path = '{}/.well-known/acme-challenge'.format(
            self.__config['orders'][index]['auth_to'])
        writeLog("|-验证目录：{}".format(acme_path))
        if os.path.exists(acme_path):
            mw.execShell("rm -f {}/*".format(acme_path))

        acme_path = mw.getServerDir() + '/stop/.well-known/acme-challenge'
        if os.path.exists(acme_path):
            mw.execShell("rm -f {}/*".format(acme_path))

    # 获取域名验证方式
    def getAuthType(self, index):
        if not index in self.__config['orders']:
            raise Exception('指定订单不存在!')
        s_type = 'http-01'
        if 'auth_type' in self.__config['orders'][index]:
            if self.__config['orders'][index]['auth_type'] == 'dns':
                s_type = 'dns-01'
            elif self.__config['orders'][index]['auth_type'] == 'tls':
                s_type = 'tls-alpn-01'
            else:
                s_type = 'http-01'
        return s_type

    # 构造验证信息
    def getIdentifierAuth(self, index, url, auth_info):
        s_type = self.getAuthType(index)
        writeLog("|-验证类型：{}".format(s_type))
        domain = auth_info['identifier']['value']
        wildcard = False
        # 处理通配符
        if 'wildcard' in auth_info:
            wildcard = auth_info['wildcard']
        if wildcard:
            domain = "*." + domain

        for auth in auth_info['challenges']:
            if auth['type'] != s_type:
                continue
            identifier_auth = {
                "domain": domain,
                "url": url,
                "wildcard": wildcard,
                "token": auth['token'],
                "dns_challenge_url": auth['url'],
            }
            return identifier_auth
        return None

    # 构造域名验证头和验证值
    def getKeyauthorization(self, token):
        acme_header_jwk_json = json.dumps(
            self.getAcmeHeader("GET_THUMBPRINT")["jwk"], sort_keys=True, separators=(",", ":")
        )
        acme_thumbprint = self.calculateSafeBase64(
            hashlib.sha256(acme_header_jwk_json.encode("utf8")).digest()
        )
        acme_keyauthorization = "{0}.{1}".format(token, acme_thumbprint)
        base64_of_acme_keyauthorization = self.calculateSafeBase64(
            hashlib.sha256(acme_keyauthorization.encode("utf8")).digest()
        )

        return acme_keyauthorization, base64_of_acme_keyauthorization

    # 写验证文件
    def writeAuthFile(self, auth_to, token, acme_keyauthorization):
        try:
            # self.D('writeAuthFile', auth_to)
            acme_path = '{}/.well-known/acme-challenge'.format(auth_to)
            if not os.path.exists(acme_path):
                os.makedirs(acme_path)
                mw.setOwn(acme_path, 'www')
            wellknown_path = '{}/{}'.format(acme_path, token)
            mw.writeFile(wellknown_path, acme_keyauthorization)
            mw.setOwn(wellknown_path, 'www')

            acme_path = mw.getServerDir() + '/stop/.well-known/acme-challenge'
            if not os.path.exists(acme_path):
                os.makedirs(acme_path)
                mw.setOwn(acme_path, 'www')
            wellknown_path = '{}/{}'.format(acme_path, token)
            mw.writeFile(wellknown_path, acme_keyauthorization)
            mw.setOwn(wellknown_path, 'www')
            return True
        except:
            err = mw.getTracebackInfo()
            raise Exception("写入验证文件失败: {}".format(err))

    # 设置验证信息
    def setAuthInfo(self, identifier_auth):

        # 是否手动验证DNS
        if identifier_auth['auth_to'] == 'dns':
            return None

        # 是否文件验证
        if identifier_auth['type'] in ['http', 'tls']:
            self.writeAuthFile(identifier_auth['auth_to'], identifier_auth[
                               'token'], identifier_auth['acme_keyauthorization'])

    # 获取验证信息
    def getAuths(self, index):
        if not index in self.__config['orders']:
            raise Exception('指定订单不存在!')

        # 检查是否已经获取过授权信息
        if 'auths' in self.__config['orders'][index]:
            # 检查授权信息是否过期
            if time.time() < self.__config['orders'][index]['auths'][0]['expires']:
                return self.__config['orders'][index]['auths']
        if self.__config['orders'][index]['auth_type'] != 'dns':
            site_run_path = self.getSiteRunPath(
                self.__config['orders'][index]['domains'])
            if site_run_path:
                self.__config['orders'][index]['auth_to'] = site_run_path

        # 清理旧验证
        self.claerAuthFile(index)

        auths = []
        for auth_url in self.__config['orders'][index]['authorizations']:
            res = self.acmeRequest(auth_url, "")
            if res.status_code not in [200, 201]:
                raise Exception("获取授权失败: {}".format(res.json()))

            s_body = res.json()
            if 'status' in s_body:
                if s_body['status'] in ['invalid']:
                    raise Exception("无效订单，此订单当前为验证失败状态!")
                if s_body['status'] in ['valid']:  # 跳过无需验证的域名
                    continue

            s_body['expires'] = self.utcToTime(s_body['expires'])
            identifier_auth = self.getIdentifierAuth(index, auth_url, s_body)
            if not identifier_auth:
                raise Exception("验证信息构造失败!{}")

            acme_keyauthorization, auth_value = self.getKeyauthorization(identifier_auth[
                                                                         'token'])
            identifier_auth['acme_keyauthorization'] = acme_keyauthorization
            identifier_auth['auth_value'] = auth_value
            identifier_auth['expires'] = s_body['expires']
            identifier_auth['auth_to'] = self.__config[
                'orders'][index]['auth_to']
            identifier_auth['type'] = self.__config[
                'orders'][index]['auth_type']

            # print(identifier_auth)
            # 设置验证信息
            self.setAuthInfo(identifier_auth)
            auths.append(identifier_auth)
        self.__config['orders'][index]['auths'] = auths
        self.saveConfig()
        return auths

    # 更新随机数
    def updateReplayNonce(self, res):
        replay_nonce = res.headers.get('replay-nonce')
        if replay_nonce:
            self.__replay_nonce = replay_nonce

    # 请求到ACME接口
    def acmeRequest(self, url, payload):
        headers = {"User-Agent": self.__user_agent}
        payload = self.stringfyItems(payload)

        if payload == "":
            payload64 = payload
        else:
            payload64 = self.calculateSafeBase64(json.dumps(payload))
        protected = self.getAcmeHeader(url)
        protected64 = self.calculateSafeBase64(json.dumps(protected))
        signature = self.signMessage(
            message="{0}.{1}".format(protected64, payload64))  # bytes
        signature64 = self.calculateSafeBase64(signature)  # str
        data = json.dumps(
            {"protected": protected64, "payload": payload64, "signature": signature64})
        headers.update({"Content-Type": "application/jose+json"})
        response = requests.post(
            url,
            data=data.encode("utf8"),
            timeout=self.__acme_timeout,
            headers=headers,
            verify=self.__verify
        )
        # 更新随机数
        self.updateReplayNonce(response)
        return response

    # UTC时间转时间戳
    def utcToTime(self, utc_string):
        try:
            utc_string = utc_string.split('.')[0]
            utc_date = datetime.datetime.strptime(
                utc_string, "%Y-%m-%dT%H:%M:%S")
            # 按北京时间返回
            return int(time.mktime(utc_date.timetuple())) + (3600 * 8)
        except:
            return int(time.time() + 86400 * 7)

    # 保存订单
    def saveOrder(self, order_object, index):
        if not 'orders' in self.__config:
            self.__config['orders'] = {}
        renew = False
        if not index:
            index = mw.md5(json.dumps(order_object['identifiers']))
        else:
            renew = True
            order_object['certificate_url'] = self.__config[
                'orders'][index]['certificate_url']
            order_object['save_path'] = self.__config[
                'orders'][index]['save_path']

        order_object['expires'] = self.utcToTime(order_object['expires'])
        self.__config['orders'][index] = order_object
        self.__config['orders'][index]['index'] = index
        if not renew:
            self.__config['orders'][index]['create_time'] = int(time.time())
            self.__config['orders'][index]['renew_time'] = 0
        self.saveConfig()
        return index

    def getError(self, error):
        # 格式化错误输出
        if error.find("Max checks allowed") >= 0:
            return "CA无法验证您的域名，请检查域名解析是否正确，或等待5-10分钟后重试."
        elif error.find("Max retries exceeded with") >= 0 or error.find('status_code=0 ') != -1:
            return "CA服务器连接超时，请稍候重试."
        elif error.find("The domain name belongs") >= 0:
            return "域名不属于此DNS服务商，请确保域名填写正确."
        elif error.find('login token ID is invalid') >= 0:
            return 'DNS服务器连接失败，请检查密钥是否正确.'
        elif error.find('Error getting validation data') != -1:
            return '数据验证失败，CA无法从验证连接中获到正确的验证码.'
        elif "too many certificates already issued for exact set of domains" in error:
            return '签发失败,该域名%s超出了每周的重复签发次数限制!' % re.findall("exact set of domains: (.+):", error)
        elif "Error creating new account :: too many registrations for this IP" in error:
            return '签发失败,当前服务器IP已达到每3小时最多创建10个帐户的限制.'
        elif "DNS problem: NXDOMAIN looking up A for" in error:
            return '验证失败,没有解析域名,或解析未生效!'
        elif "Invalid response from" in error:
            return '验证失败,域名解析错误或验证URL无法被访问!'
        elif error.find('TLS Web Server Authentication') != -1:
            return "连接CA服务器失败，请稍候重试."
        elif error.find('Name does not end in a public suffix') != -1:
            return "不支持的域名%s，请检查域名是否正确!" % re.findall("Cannot issue for \"(.+)\":", error)
        elif error.find('No valid IP addresses found for') != -1:
            return "域名%s没有找到解析记录，请检查域名是否解析生效!" % re.findall("No valid IP addresses found for (.+)", error)
        elif error.find('No TXT record found at') != -1:
            return "没有在域名%s中找到有效的TXT解析记录,请检查是否正确解析TXT记录,如果是DNSAPI方式申请的,请10分钟后重试!" % re.findall("No TXT record found at (.+)", error)
        elif error.find('Incorrect TXT record') != -1:
            return "在%s上发现错误的TXT记录:%s,请检查TXT解析是否正确,如果是DNSAPI方式申请的,请10分钟后重试!" % (re.findall("found at (.+)", error), re.findall("Incorrect TXT record \"(.+)\"", error))
        elif error.find('Domain not under you or your user') != -1:
            return "这个dnspod账户下面不存在这个域名，添加解析失败!"
        elif error.find('SERVFAIL looking up TXT for') != -1:
            return "没有在域名%s中找到有效的TXT解析记录,请检查是否正确解析TXT记录,如果是DNSAPI方式申请的,请10分钟后重试!" % re.findall("looking up TXT for (.+)", error)
        elif error.find('Timeout during connect') != -1:
            return "连接超时,CA服务器无法访问您的网站!"
        elif error.find("DNS problem: SERVFAIL looking up CAA for") != -1:
            return "域名%s当前被要求验证CAA记录，请手动解析CAA记录，或1小时后重新尝试申请!" % re.findall("looking up CAA for (.+)", error)
        elif error.find("Read timed out.") != -1:
            return "验证超时,请检查域名是否正确解析，若已正确解析，可能服务器与Let'sEncrypt连接异常，请稍候再重试!"
        elif error.find('Cannot issue for') != -1:
            return "无法为{}颁发证书，不能直接用域名后缀申请通配符证书!".format(re.findall(r'for\s+"(.+)"', error))
        elif error.find('too many failed authorizations recently'):
            return '该帐户1小时内失败的订单次数超过5次，请等待1小时再重试!'
        elif error.find("Error creating new order") != -1:
            return "订单创建失败，请稍候重试!"
        elif error.find("Too Many Requests") != -1:
            return "1小时内超过5次验证失败，暂时禁止申请，请稍候重试!"
        elif error.find('HTTP Error 400: Bad Request') != -1:
            return "CA服务器拒绝访问，请稍候重试!"
        elif error.find('Temporary failure in name resolution') != -1:
            return '服务器DNS故障，无法解析域名，请使用Linux工具箱检查dns配置'
        elif error.find('Too Many Requests') != -1:
            return '该域名请求申请次数过多，请3小时后重试'
        else:
            return error

    # 创建订单
    def createOrder(self, domains, auth_type, auth_to, index=None):
        domains = self.formatDomains(domains)
        if not domains:
            raise Exception("至少需要有一个域名")
        # 构造标识
        identifiers = []
        for domain_name in domains:
            identifiers.append({"type": 'dns', "value": domain_name})
        payload = {"identifiers": identifiers}

        # 请求创建订单
        res = self.acmeRequest(self.__apis['newOrder'], payload)
        if not res.status_code in [201]:  # 如果创建失败
            e_body = res.json()
            if 'type' in e_body:
                # 如果随机数失效
                if e_body['type'].find('error:badNonce') != -1:
                    self.getNonce(force=True)
                    res = self.acmeRequest(self.__apis['newOrder'], payload)

                # 如果帐户失效
                if e_body['detail'].find('KeyID header contained an invalid account URL') != -1:
                    k = self._mod_index[self.__debug]
                    del(self.__config['account'][k])
                    self.getKid()
                    self.getNonce(force=True)
                    res = self.acmeRequest(self.__apis['newOrder'], payload)
            if not res.status_code in [201]:
                a_auth = res.json()

                ret_title = self.getError(str(a_auth))
                raise StopIteration("{0} >>>> {1}".format(
                    ret_title, json.dumps(a_auth)))

        # 返回验证地址和验证
        s_json = res.json()
        s_json['auth_type'] = auth_type
        s_json['domains'] = domains
        s_json['auth_to'] = auth_to
        index = self.saveOrder(s_json, index)
        return index

    # 检查验证状态
    def checkAuthStatus(self, url, desired_status=None):
        desired_status = desired_status or ["pending", "valid", "invalid"]
        number_of_checks = 0
        while True:
            if desired_status == ['valid', 'invalid']:
                writeLog("|-第{}次查询验证结果..".format(number_of_checks + 1))
                time.sleep(self.__wait_time)
            check_authorization_status_response = self.acmeRequest(url, "")
            a_auth = check_authorization_status_response.json()
            authorization_status = a_auth["status"]
            number_of_checks += 1
            if authorization_status in desired_status:
                if authorization_status == "invalid":
                    writeLog("|-验证失败!")
                    try:
                        if 'error' in a_auth['challenges'][0]:
                            ret_title = a_auth['challenges'][
                                0]['error']['detail']
                        elif 'error' in a_auth['challenges'][1]:
                            ret_title = a_auth['challenges'][
                                1]['error']['detail']
                        elif 'error' in a_auth['challenges'][2]:
                            ret_title = a_auth['challenges'][
                                2]['error']['detail']
                        else:
                            ret_title = str(a_auth)
                        ret_title = self.getError(ret_title)
                    except:
                        ret_title = str(a_auth)
                    raise StopIteration("{0} >>>> {1}".format(
                        ret_title, json.dumps(a_auth)))
                break

            if number_of_checks == self.__max_check_num:
                raise StopIteration(
                    "错误：已尝试验证{0}次. 最大验证次数为{1}. 验证时间间隔为{2}秒.".format(
                        number_of_checks,
                        self.__max_check_num,
                        self.__wait_time
                    )
                )
        if desired_status == ['valid', 'invalid']:
            writeLog("|-验证成功!")
        return check_authorization_status_response

    # 发送验证请求
    def respondToChallenge(self, auth):
        payload = {"keyAuthorization": "{0}".format(
            auth['acme_keyauthorization'])}
        respond_to_challenge_response = self.acmeRequest(
            auth['dns_challenge_url'], payload)
        return respond_to_challenge_response

    # 检查DNS记录
    def checkDns(self, domain, value, s_type='TXT'):
        writeLog(
            "|-尝试本地验证DNS记录,域名: {} , 类型: {} 记录值: {}".format(domain, s_type, value))
        time.sleep(10)
        n = 0
        while n < 20:
            n += 1
            try:
                import dns.resolver
                ns = dns.resolver.query(domain, s_type)
                for j in ns.response.answer:
                    for i in j.items:
                        txt_value = i.to_text().replace('"', '').strip()
                        writeLog("|-第 {} 次验证值: {}".format(n, txt_value))
                        if txt_value == value:
                            write_log("|-本地验证成功!")
                            return True
            except:
                try:
                    import dns.resolver
                except:
                    return False
            time.sleep(3)
        writeLog("|-本地验证失败!")
        return True

    def authDomain(self, index):
        if not index in self.__config['orders']:
            raise Exception('指定订单不存在!')

        # 开始验证
        for auth in self.__config['orders'][index]['auths']:
            res = self.checkAuthStatus(auth['url'])  # 检查是否需要验证
            if res.json()['status'] == 'pending':
                if auth['type'] == 'dns':  # 尝试提前验证dns解析
                    self.checkDns(
                        "_acme-challenge.{}".format(
                            auth['domain'].replace('*.', '')),
                        auth['auth_value'],
                        "TXT"
                    )
                self.respondToChallenge(auth)

        # 检查验证结果
        for i in range(len(self.__config['orders'][index]['auths'])):
            self.checkAuthStatus(self.__config['orders'][index]['auths'][i]['url'], [
                'valid', 'invalid'])
            self.__config['orders'][index]['status'] = 'valid'

    # 构造可选名称
    def getAltNames(self, index):
        domain_name = self.__config['orders'][index]['domains'][0]
        domain_alt_names = []
        if len(self.__config['orders'][index]['domains']) > 1:
            domain_alt_names = self.__config['orders'][index]['domains'][1:]
        return domain_name, domain_alt_names

    # 创建CSR
    def createCsr(self, index):
        if 'csr' in self.__config['orders'][index]:
            return self.__config['orders']['csr']
        domain_name, domain_alt_names = self.getAltNames(index)
        X509Req = OpenSSL.crypto.X509Req()
        X509Req.get_subject().CN = domain_name
        if domain_alt_names:
            SAN = "DNS:{0}, ".format(domain_name).encode("utf8") + ", ".join(
                "DNS:" + i for i in domain_alt_names
            ).encode("utf8")
        else:
            SAN = "DNS:{0}".format(domain_name).encode("utf8")

        X509Req.add_extensions(
            [
                OpenSSL.crypto.X509Extension(
                    "subjectAltName".encode("utf8"), critical=False, value=SAN
                )
            ]
        )
        pk = OpenSSL.crypto.load_privatekey(
            OpenSSL.crypto.FILETYPE_PEM, self.createCertificateKey(
                index).encode()
        )
        X509Req.set_pubkey(pk)
        # X509Req.set_version(2)
        X509Req.set_version(0)
        X509Req.sign(pk, self.__digest)
        return OpenSSL.crypto.dump_certificate_request(OpenSSL.crypto.FILETYPE_ASN1, X509Req)

    # 获取证书密钥对
    def createCertificateKey(self, index):
        # 判断是否已经创建private_key
        if 'private_key' in self.__config['orders'][index]:
            return self.__config['orders'][index]['private_key']
        # 创建新的私钥
        private_key = self.createKey()
        if type(private_key) == bytes:
            private_key = private_key.decode()
        # 保存私钥到订单配置文件
        self.__config['orders'][index]['private_key'] = private_key
        self.saveConfig()
        return private_key

    # 发送CSR
    def sendCsr(self, index):
        csr = self.createCsr(index)
        payload = {"csr": self.calculateSafeBase64(csr)}
        send_csr_response = self.acmeRequest(
            url=self.__config['orders'][index]['finalize'], payload=payload)
        if send_csr_response.status_code not in [200, 201]:
            raise ValueError(
                "错误： 发送CSR: 响应状态{status_code} 响应值:{response}".format(
                    status_code=send_csr_response.status_code,
                    response=send_csr_response.json(),
                )
            )
        send_csr_response_json = send_csr_response.json()
        certificate_url = send_csr_response_json["certificate"]
        self.__config['orders'][index]['certificate_url'] = certificate_url
        self.saveConfig()
        return certificate_url

    # 转换时间
    def strfDate(self, sdate):
        return time.strftime('%Y-%m-%d', time.strptime(sdate, '%Y%m%d%H%M%S'))

    # 证书转为DER
    def dumpDer(self, cert_path):
        cert = OpenSSL.crypto.load_certificate(
            OpenSSL.crypto.FILETYPE_PEM, mw.readFile(cert_path + '/cert.csr'))
        return OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert)

    # 证书转为pkcs12
    def dumpPkcs12(self, key_pem=None, cert_pem=None, ca_pem=None, friendly_name=None):
        p12 = OpenSSL.crypto.PKCS12()
        if cert_pem:
            p12.set_certificate(OpenSSL.crypto.load_certificate(
                OpenSSL.crypto.FILETYPE_PEM, cert_pem.encode()))
        if key_pem:
            p12.set_privatekey(OpenSSL.crypto.load_privatekey(
                OpenSSL.crypto.FILETYPE_PEM, key_pem.encode()))
        if ca_pem:
            p12.set_ca_certificates((OpenSSL.crypto.load_certificate(
                OpenSSL.crypto.FILETYPE_PEM, ca_pem.encode()),))
        if friendly_name:
            p12.set_friendlyname(friendly_name.encode())
        return p12.export()

    # 拆分根证书
    def splitCaData(self, cert):
        sp_key = '-----END CERTIFICATE-----\n'
        datas = cert.split(sp_key)
        return {"cert": datas[0] + sp_key, "root": sp_key.join(datas[1:])}

    # 获取指定证书基本信息
    def getCertInit(self, pem_file):
        if not os.path.exists(pem_file):
            return None
        try:
            result = {}
            x509 = OpenSSL.crypto.load_certificate(
                OpenSSL.crypto.FILETYPE_PEM, mw.readFile(pem_file))
            # 取产品名称
            issuer = x509.get_issuer()
            result['issuer'] = ''
            if hasattr(issuer, 'CN'):
                result['issuer'] = issuer.CN
            if not result['issuer']:
                is_key = [b'0', '0']
                issue_comp = issuer.get_components()
                if len(issue_comp) == 1:
                    is_key = [b'CN', 'CN']
                for iss in issue_comp:
                    if iss[0] in is_key:
                        result['issuer'] = iss[1].decode()
                        break
            # 取到期时间
            result['notAfter'] = self.strfDate(
                bytes.decode(x509.get_notAfter())[:-1])
            # 取申请时间
            result['notBefore'] = self.strfDate(
                bytes.decode(x509.get_notBefore())[:-1])
            # 取可选名称
            result['dns'] = []
            for i in range(x509.get_extension_count()):
                s_name = x509.get_extension(i)
                if s_name.get_short_name() in [b'subjectAltName', 'subjectAltName']:
                    s_dns = str(s_name).split(',')
                    for d in s_dns:
                        result['dns'].append(d.split(':')[1])
            subject = x509.get_subject().get_components()
            # 取主要认证名称
            if len(subject) == 1:
                result['subject'] = subject[0][1].decode()
            else:
                result['subject'] = result['dns'][0]
            return result
        except:
            return None

    # 替换服务器上的同域名同品牌证书
    def subAllCert(self, key_file, pem_file):
        cert_init = self.getCertInit(pem_file)  # 获取新证书的基本信息
        paths = ['/www/server/mdserver-web/data/letsencrypt']
        is_panel = False
        for path in paths:
            if not os.path.exists(path):
                continue
            for p_name in os.listdir(path):
                to_path = path + '/' + p_name
                to_pem_file = to_path + '/fullchain.pem'
                to_key_file = to_path + '/privkey.pem'
                to_info = to_path + '/info.json'
                # 判断目标证书是否存在
                if not os.path.exists(to_pem_file):
                    if not p_name in ['ssl']:
                        continue
                    to_pem_file = to_path + '/certificate.pem'
                    to_key_file = to_path + '/privateKey.pem'
                    if not os.path.exists(to_pem_file):
                        continue
                    if path == paths[-1]:
                        is_panel = True
                # 获取目标证书的基本信息
                to_cert_init = self.getCertInit(to_pem_file)
                # 判断证书品牌是否一致
                try:
                    if to_cert_init['issuer'] != cert_init['issuer'] and to_cert_init['issuer'].find("Let's Encrypt") == -1 and to_cert_init['issuer'] != 'R3':
                        continue
                except:
                    continue
                # 判断目标证书的到期时间是否较早
                if to_cert_init['notAfter'] > cert_init['notAfter']:
                    continue
                # 判断认识名称是否一致
                if len(to_cert_init['dns']) != len(cert_init['dns']):
                    continue
                is_copy = True
                for domain in to_cert_init['dns']:
                    if not domain in cert_init['dns']:
                        is_copy = False
                if not is_copy:
                    continue

                # 替换新的证书文件和基本信息
                mw.writeFile(to_pem_file, mw.readFile(pem_file, 'rb'), 'wb')
                mw.writeFile(to_key_file, mw.readFile(key_file, 'rb'), 'wb')
                mw.writeFile(to_info, json.dumps(cert_init))
                writeLog("|-检测到{}下的证书与本次申请的证书重叠，且到期时间较早，已替换为新证书!".format(to_path))
        # 重载web服务
        mw.restartWeb()

    # 保存证书到文件
    def saveCert(self, cert, index):
        try:
            domain_name = self.__config['orders'][index]['domains'][0]
            path = self.__config['orders'][index]['save_path']
            if not os.path.exists(path):
                os.makedirs(path, 384)

            # 存储证书
            key_file = path + "/privkey.pem"
            pem_file = path + "/fullchain.pem"
            mw.writeFile(key_file, cert['private_key'])
            mw.writeFile(pem_file, cert['cert'] + cert['root'])
            mw.writeFile(path + "/cert.csr", cert['cert'])
            mw.writeFile(path + "/root_cert.csr", cert['root'])

            # 转为IIS证书
            pfx_buffer = self.dumpPkcs12(
                cert['private_key'], cert['cert'] + cert['root'], cert['root'], domain_name)
            mw.writeFile(path + "/fullchain.pfx", pfx_buffer, 'wb+')

            ps = '''文件说明：
privkey.pem     证书私钥
fullchain.pem   包含证书链的PEM格式证书(nginx/apache)
root_cert.csr   根证书
cert.csr        域名证书
fullchain.pfx   用于IIS的证书格式

如何在MW面板使用：
privkey.pem         粘贴到密钥输入框
fullchain.pem       粘贴到证书输入框
'''
            mw.writeFile(path + '/readme.txt', ps)
            self.subAllCert(key_file, pem_file)
        except:
            writeLog(mw.getTracebackInfo())

    # 获取证书到期时间
    def getCertTimeout(self, cret_data):
        try:
            x509 = OpenSSL.crypto.load_certificate(
                OpenSSL.crypto.FILETYPE_PEM, cret_data)
            cert_timeout = bytes.decode(x509.get_notAfter())[:-1]
            return int(time.mktime(time.strptime(cert_timeout, '%Y%m%d%H%M%S')))
        except:
            return int(time.time() + (86400 * 90))

    # 下载证书
    def downloadCert(self, index):
        res = self.acmeRequest(
            self.__config['orders'][index]['certificate_url'], "")
        if res.status_code not in [200, 201]:
            raise Exception("下载证书失败: {}".format(res.json()))

        pem_certificate = res.content
        if type(pem_certificate) == bytes:
            pem_certificate = pem_certificate.decode('utf-8')
        cert = self.splitCaData(pem_certificate)
        cert['cert_timeout'] = self.getCertTimeout(cert['cert'])
        cert['private_key'] = self.__config['orders'][index]['private_key']
        cert['domains'] = self.__config['orders'][index]['domains']
        del(self.__config['orders'][index]['private_key'])
        del(self.__config['orders'][index]['auths'])
        del(self.__config['orders'][index]['expires'])
        del(self.__config['orders'][index]['authorizations'])
        del(self.__config['orders'][index]['finalize'])
        del(self.__config['orders'][index]['identifiers'])
        if 'cert' in self.__config['orders'][index]:
            del(self.__config['orders'][index]['cert'])
        self.__config['orders'][index]['status'] = 'valid'
        self.__config['orders'][index]['cert_timeout'] = cert['cert_timeout']
        domain_name = self.__config['orders'][index]['domains'][0]
        self.__config['orders'][index]['save_path'] = '{}/{}'.format(
            self.__save_path, domain_name)
        cert['save_path'] = self.__config['orders'][index]['save_path']
        self.saveConfig()
        self.saveCert(cert, index)
        return cert

    def applyCert(self, domains, auth_type='http', auth_to='Dns_com|None|None', args={}):
        writeLog("", "wb+")
        try:
            self.getApis()
            index = None
            if 'index' in args and args.index:
                index = args.index
            if not index:
                # 判断是否只想验证域名
                writeLog("|-正在创建订单..")
                index = self.createOrder(domains, auth_type, auth_to)
                writeLog("|-正在获取验证信息..")
                self.getAuths(index)
                if auth_to == 'dns' and len(self.__config['orders'][index]['auths']) > 0:
                    return self.__config['orders'][index]
            writeLog("|-正在验证域名..")
            self.authDomain(index)

            writeLog("|-正在发送CSR..")
            self.sendCsr(index)

            writeLog("|-正在下载证书..")
            cert = self.downloadCert(index)

            # 保存证书配置
            self.saveConfig()
            cert['status'] = True
            cert['msg'] = '申请成功!'
            writeLog("|-申请成功，正在部署到站点..")
            return cert
        except Exception as ex:
            ex = str(ex)
            if ex.find(">>>>") != -1:
                msg = ex.split(">>>>")
                msg[1] = json.loads(msg[1])
            else:
                msg = ex
                writeLog(mw.getTracebackInfo())

            cert = {}
            cert['status'] = False
            cert['msg'] = msg
            return cert

    # 取根域名和记录值
    def extractZone(self, domain_name):
        top_domain_list = ['.ac.cn', '.ah.cn', '.bj.cn', '.com.cn', '.cq.cn', '.fj.cn', '.gd.cn', '.gov.cn', '.gs.cn',
                           '.gx.cn', '.gz.cn', '.ha.cn', '.hb.cn', '.he.cn', '.hi.cn', '.hk.cn', '.hl.cn', '.hn.cn',
                           '.jl.cn', '.js.cn', '.jx.cn', '.ln.cn', '.mo.cn', '.net.cn', '.nm.cn', '.nx.cn', '.org.cn',
                           '.my.id', '.com.ac', '.com.ad', '.com.ae', '.com.af', '.com.ag', '.com.ai', '.com.al', '.com.am',
                           '.com.an', '.com.ao', '.com.aq', '.com.ar', '.com.as', '.com.as', '.com.at', '.com.au', '.com.aw',
                           '.com.az', '.com.ba', '.com.bb', '.com.bd', '.com.be', '.com.bf', '.com.bg', '.com.bh', '.com.bi',
                           '.com.bj', '.com.bm', '.com.bn', '.com.bo', '.com.br', '.com.bs', '.com.bt', '.com.bv', '.com.bw',
                           '.com.by', '.com.bz', '.com.ca', '.com.ca', '.com.cc', '.com.cd', '.com.cf', '.com.cg', '.com.ch',
                           '.com.ci', '.com.ck', '.com.cl', '.com.cm', '.com.cn', '.com.co', '.com.cq', '.com.cr', '.com.cu',
                           '.com.cv', '.com.cx', '.com.cy', '.com.cz', '.com.de', '.com.dj', '.com.dk', '.com.dm', '.com.do',
                           '.com.dz', '.com.ec', '.com.ee', '.com.eg', '.com.eh', '.com.es', '.com.et', '.com.eu', '.com.ev',
                           '.com.fi', '.com.fj', '.com.fk', '.com.fm', '.com.fo', '.com.fr', '.com.ga', '.com.gb', '.com.gd',
                           '.com.ge', '.com.gf', '.com.gh', '.com.gi', '.com.gl', '.com.gm', '.com.gn', '.com.gp', '.com.gr',
                           '.com.gt', '.com.gu', '.com.gw', '.com.gy', '.com.hm', '.com.hn', '.com.hr', '.com.ht', '.com.hu',
                           '.com.id', '.com.id', '.com.ie', '.com.il', '.com.il', '.com.in', '.com.io', '.com.iq', '.com.ir',
                           '.com.is', '.com.it', '.com.jm', '.com.jo', '.com.jp', '.com.ke', '.com.kg', '.com.kh', '.com.ki',
                           '.com.km', '.com.kn', '.com.kp', '.com.kr', '.com.kw', '.com.ky', '.com.kz', '.com.la', '.com.lb',
                           '.com.lc', '.com.li', '.com.lk', '.com.lr', '.com.ls', '.com.lt', '.com.lu', '.com.lv', '.com.ly',
                           '.com.ma', '.com.mc', '.com.md', '.com.me', '.com.mg', '.com.mh', '.com.ml', '.com.mm', '.com.mn',
                           '.com.mo', '.com.mp', '.com.mq', '.com.mr', '.com.ms', '.com.mt', '.com.mv', '.com.mw', '.com.mx',
                           '.com.my', '.com.mz', '.com.na', '.com.nc', '.com.ne', '.com.nf', '.com.ng', '.com.ni', '.com.nl',
                           '.com.no', '.com.np', '.com.nr', '.com.nr', '.com.nt', '.com.nu', '.com.nz', '.com.om', '.com.pa',
                           '.com.pe', '.com.pf', '.com.pg', '.com.ph', '.com.pk', '.com.pl', '.com.pm', '.com.pn', '.com.pr',
                           '.com.pt', '.com.pw', '.com.py', '.com.qa', '.com.re', '.com.ro', '.com.rs', '.com.ru', '.com.rw',
                           '.com.sa', '.com.sb', '.com.sc', '.com.sd', '.com.se', '.com.sg', '.com.sh', '.com.si', '.com.sj',
                           '.com.sk', '.com.sl', '.com.sm', '.com.sn', '.com.so', '.com.sr', '.com.st', '.com.su', '.com.sy',
                           '.com.sz', '.com.tc', '.com.td', '.com.tf', '.com.tg', '.com.th', '.com.tj', '.com.tk', '.com.tl',
                           '.com.tm', '.com.tn', '.com.to', '.com.tp', '.com.tr', '.com.tt', '.com.tv', '.com.tw', '.com.tz',
                           '.com.ua', '.com.ug', '.com.uk', '.com.uk', '.com.us', '.com.uy', '.com.uz', '.com.va', '.com.vc',
                           '.com.ve', '.com.vg', '.com.vn', '.com.vu', '.com.wf', '.com.ws', '.com.ye', '.com.za', '.com.zm',
                           '.com.zw', '.mil.cn', '.qh.cn', '.sc.cn', '.sd.cn', '.sh.cn', '.sx.cn', '.tj.cn', '.tw.cn', '.tw.cn',
                           '.xj.cn', '.xz.cn', '.yn.cn', '.zj.cn', '.bj.cn', '.edu.kg'
                           ]
        old_domain_name = domain_name
        top_domain = "." + ".".join(domain_name.rsplit('.')[-2:])
        new_top_domain = "." + top_domain.replace(".", "")
        is_tow_top = False
        if top_domain in top_domain_list:
            is_tow_top = True
            domain_name = domain_name[:-len(top_domain)] + new_top_domain

        if domain_name.count(".") > 1:
            zone, middle, last = domain_name.rsplit(".", 2)
            if is_tow_top:
                last = top_domain[1:]
            root = ".".join([middle, last])
        else:
            zone = ""
            root = old_domain_name
        return root, zone

    # 获取当前正在使用此证书的网站目录
    def getSslUsedSite(self, save_path):
        pkey_file = '{}/privkey.pem'.format(save_path)
        pkey = mw.readFile(pkey_file)
        if not pkey:
            return False
        cert_paths = 'vhost/cert'
        import panelSite
        args = mw.dict_obj()
        args.siteName = ''
        for c_name in os.listdir(cert_paths):
            skey_file = '{}/{}/privkey.pem'.format(cert_paths, c_name)
            skey = mw.readFile(skey_file)
            if not skey:
                continue
            if skey == pkey:
                args.siteName = c_name
                run_path = panelSite.panelSite().GetRunPath(args)
                if not run_path:
                    continue
                sitePath = mw.M('sites').where(
                    'name=?', c_name).getField('path')
                if not sitePath:
                    continue
                to_path = "{}/{}".format(sitePath, run_path)
                return to_path
        return False

    def renewCertOther(self):
        cert_path = "{}/vhost/cert".format(mw.getRunDir())
        if not os.path.exists(cert_path):
            return
        new_time = time.time() + (86400 * 30)
        n = 0
        if not 'orders' in self.__config:
            self.__config['orders'] = {}
        import panelSite
        siteObj = panelSite.panelSite()
        args = mw.dict_obj()
        for siteName in os.listdir(cert_path):
            try:
                cert_file = '{}/{}/fullchain.pem'.format(cert_path, siteName)
                if not os.path.exists(cert_file):
                    continue  # 无证书文件
                siteInfo = mw.M('sites').where('name=?', siteName).find()
                if not siteInfo:
                    continue  # 无网站信息
                cert_init = self.getCertInit(cert_file)
                if not cert_init:
                    continue  # 无法获取证书
                end_time = time.mktime(time.strptime(
                    cert_init['notAfter'], '%Y-%m-%d'))
                if end_time > new_time:
                    continue  # 未到期
                try:
                    if not cert_init['issuer'] in ['R3', "Let's Encrypt"] and cert_init['issuer'].find("Let's Encrypt") == -1:
                        continue  # 非同品牌证书
                except:
                    continue

                if isinstance(cert_init['dns'], str):
                    cert_init['dns'] = [cert_init['dns']]
                index = self.getIndex(cert_init['dns'])
                if index in self.__config['orders'].keys():
                    continue  # 已在订单列表

                n += 1
                writeLog(
                    "|-正在续签第 {} 张其它证书，域名: {}..".format(n, cert_init['subject']))
                writeLog("|-正在创建订单..")
                args.id = siteInfo['id']
                runPath = siteObj.GetRunPath(args)
                if runPath and not runPath in ['/']:
                    path = siteInfo['path'] + '/' + runPath
                else:
                    path = siteInfo['path']
            except:
                write_log("|-[{}]续签失败".format(siteName))

    # 外部API - START ----------------------------------------------------------
    def applyCertApi(self, args):
        '''
        申请证书 - api
        '''
        return self.applyCert(args['domains'], args['auth_type'], args['auth_to'])
    # 外部API - END ----------------------------------------------------------

    def renewCert(self, index):
        writeLog("", "wb+")
        # self.D('renew_cert', index)
        try:
            order_index = []
            if index:
                if type(index) != str:
                    index = index.index
                if not index in self.__config['orders']:
                    raise Exception("指定订单号不存在，无法续签!")
                order_index.append(index)
            else:
                start_time = time.time() + (30 * 86400)
                # print(self.__config)
                if not 'orders' in self.__config:
                    self.__config['orders'] = {}

                for i in self.__config['orders'].keys():
                    # print(self.__config['orders'][i])
                    if not 'save_path' in self.__config['orders'][i]:
                        continue

                    if 'cert' in self.__config['orders'][i]:
                        self.__config['orders'][i]['cert_timeout'] = self.__config[
                            'orders'][i]['cert']['cert_timeout']

                    if not 'cert_timeout' in self.__config['orders'][i]:
                        self.__config['orders'][i][
                            'cert_timeout'] = int(time.time())

                    if self.__config['orders'][i]['cert_timeout'] > start_time:
                        writeLog(
                            "|-本次跳过域名: {}，未过期!".format(self.__config['orders'][i]['domains'][0]))
                        continue

                    # 已删除的网站直接跳过续签
                    if self.__config['orders'][i]['auth_to'].find('|') == -1 and self.__config['orders'][i]['auth_to'].find('/') != -1:
                        if not os.path.exists(self.__config['orders'][i]['auth_to']):
                            auth_to = self.getSslUsedSite(
                                self.__config['orders'][i]['save_path'])
                            if not auth_to:
                                continue

                            # 域名不存在？
                            for domain in self.__config['orders'][i]['domains']:
                                if domain.find('*') != -1:
                                    break
                                if not mw.M('domain').where("name=?", (domain,)).count() and not mw.M('binding').where("domain=?", domain).count():
                                    auth_to = None
                                    writeLog(
                                        "|-跳过被删除的域名: {}".format(self.__config['orders'][i]['domains']))
                            if not auth_to:
                                continue

                            self.__config['orders'][i]['auth_to'] = auth_to

                    # 是否到了允许重试的时间
                    if 'next_retry_time' in self._config['orders'][i]:
                        timeout = self.__config['orders'][i][
                            'next_retry_time'] - int(time.time())
                        if timeout > 0:
                            writeLog('|-本次跳过域名:{}，因第上次续签失败，还需要等待{}小时后再重试'.format(
                                self.__config['orders'][i]['domains'], int(timeout / 60 / 60)))
                            continue

                    # 是否到了最大重试次数
                    if 'retry_count' in self.__config['orders'][i]:
                        if self.__config['orders'][i]['retry_count'] >= 5:
                            writeLog('|-本次跳过域名:{}，因连续5次续签失败，不再续签此证书(可尝试手动续签此证书，成功后错误次数将被重置)'.format(
                                self.__config['orders'][i]['domains']))
                            continue

                    # 加入到续签订单
                    order_index.append(i)
                if not order_index:
                    writeLog("|-没有找到30天内到期的SSL证书，正在尝试去寻找其它可续签证书!")
                    self.getApis()
                    # self.renewCertOther()
                    writeLog("|-所有任务已处理完成!")
                    return
            writeLog("|-共需要续签 {} 张证书".format(len(order_index)))
        except Exception as ex:
            ex = str(ex)
            if ex.find(">>>>") != -1:
                msg = ex.split(">>>>")
                msg[1] = json.loads(msg[1])
            else:
                msg = ex
                writeLog(mw.getTracebackInfo())
            return mw.returnJson(False, msg)

    def revokeOrder(self, index):
        if not index in self.__config['orders']:
            raise Exception("指定订单不存在!")
        cert_path = self.__config['orders'][index]['save_path']
        if not os.path.exists(cert_path):
            raise Exception("指定订单没有找到可用的证书!")
        cert = self.dumpDer(cert_path)
        if not cert:
            raise Exception("证书读取失败!")
        payload = {
            "certificate": self.calculateSafeBase64(cert),
            "reason": 4
        }

        self.getApis()
        res = self.acmeRequest(self.__apis['revokeCert'], payload)
        if res.status_code in [200, 201]:
            if os.path.exists(cert_path):
                mw.execShell("rm -rf {}".format(cert_path))
            del(self.__config['orders'][index])
            self.saveConfig()
            return mw.returnJson(True, "证书吊销成功!")
        return res.json()

    def do(self, args):
        cert = None
        try:
            if not args.index:
                if not args.domains:
                    echoErr("请在--domain参数中指定要申请证书的域名，多个以逗号(,)隔开")
                if not args.auth_type in ['http', 'tls']:
                    echoErr("请在--type参数中指定正确的验证类型，http")

                auth_to = ''
                if args.auth_type in ['http', 'tls']:
                    if not args.path:
                        echoErr("请在--path参数中指定网站根目录!")
                    if not os.path.exists(args.path):
                        echoErr("指定网站根目录不存在，请检查：{}".format(args.path))
                    auth_to = args.path
                else:
                    echoErr("仅支持文件验证!")
                    exit()

                domains = args.domains.strip().split(',')
                cert = self.applyCert(
                    domains, auth_type=args.auth_type, auth_to=auth_to, args=args)
            else:
                # 重新验证
                cert = self.applyCert([], auth_type='dns',
                                      auth_to='dns', index=args.index)
        except Exception as e:
            writeLog("|-{}".format(mw.getTracebackInfo()))
            exit()

        if not cert:
            exit()

        # print(cert)
        if not cert['status']:
            writeLog('|-' + cert['msg'][0])
            exit()
        writeLog("=" * 65)
        writeLog("|-证书获取成功!")
        writeLog("=" * 65)
        writeLog("证书到期时间: {}".format(
            mw.formatDate(times=cert['cert_timeout'])))
        writeLog("证书已保存在: {}/".format(cert['save_path']))


# exp:
'''
// create
python3 class/core/cert_request.py --domain=dev38.cachecha.com --type=http --path=/www/wwwroot/dev38.cachecha.com
// renew
cd /www/server/mdserver-web && python3 class/core/cert_request.py --renew=1
// revoke
cd /www/server/mdserver-web && python3 class/core/cert_request.py --revoke=1 --index=370423ed29481b2caf22e36d90a6894a

python3 class/core/cert_request.py --domain=dev38.cachecha.com --type=http --path=/Users/midoks/Desktop/mwdev/wwwroot/test
python3 class/core/cert_request.py --renew=1
python3 class/core/cert_request.py --revoke=1 --index=370423ed29481b2caf22e36d90a6894a
'''
if __name__ == "__main__":
    p = argparse.ArgumentParser(usage="必要的参数：--domain 域名列表，多个以逗号隔开!")
    p.add_argument('--domain', default=None,
                   help="请指定要申请证书的域名", dest="domains")
    p.add_argument('--type', default=None, help="请指定验证类型", dest="auth_type")
    p.add_argument('--path', default=None, help="请指定网站根目录", dest="path")
    p.add_argument('--index', default=None, help="指定订单索引", dest="index")
    p.add_argument('--renew', default=None, help="续签证书", dest="renew")
    p.add_argument('--revoke', default=None, help="吊销证书", dest="revoke")

    args = p.parse_args()
    cr = cert_request()

    if args.revoke:
        if not args.index:
            echoErr("请在--index参数中传入要被吊销的订单索引")
        result = cr.revokeOrder(args.index)
        writeLog(result)
        exit()

    if args.renew:
        cr.renewCert(args.index)
        exit()

    cr.do(args)
