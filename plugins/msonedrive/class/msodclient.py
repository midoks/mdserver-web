# coding:utf-8

import sys
import io
import os
import time
import re
import json
import io

sys.path.append(os.getcwd() + "/class/core")
import mw

import oauthlib
import requests
import datetime
from requests_oauthlib import OAuth2Session

DEBUG = False


def setDebug(d=False):
    DEBUG = d


class UnauthorizedError(Exception):
    pass


class ObjectNotFoundError(Exception):
    pass


class msodclient:

    plugin_dir = ''
    server_dir = ''
    credential_file = 'credentials.json'
    user_conf = "user.conf"
    token_file = 'token.pickle'

    def __init__(self, plugin_dir, server_dir):
        self.plugin_dir = plugin_dir
        self.server_dir = server_dir
        self.load()

    def setDebug(self, d=False):
        DEBUG = d

    def load(self):
        credential_path = os.path.join(self.plugin_dir, self.credential_file)
        credential = json.loads(mw.readFile(credential_path))
        # print(credential)
        self.credential = credential["onedrive-international"]

        self.authorize_url = '{0}{1}'.format(
            self.credential['authority'],
            self.credential['authorize_endpoint'])
        self.token_url = '{0}{1}'.format(
            self.credential['authority'],
            self.credential['token_endpoint'])

        self.token_path = os.path.join(self.server_dir, self.token_file)
        self.root_uri = self.credential["api_uri"] + "/me/drive/root"

        self.backup_path = 'backup'

    def store_token(self, token):
        """存储token"""
        enstr = mw.enDoubleCrypt('msodc', json.dumps(token))
        mw.writeFile(self.token_path, enstr)
        return True

    def get_store_token(self):
        rdata = mw.readFile(self.token_path)
        destr = mw.deDoubleCrypt('msodc', rdata)
        return json.loads(destr)

    def clear_token(self):
        """清除token记录"""
        try:
            if os.path.isfile(self.token_path):
                os.remove(self.token_path)
        except:
            if DEBUG:
                print("清除token失败。")

    def refresh_token(self, origin_token):
        """刷新token"""

        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
        os.environ['OAUTHLIB_IGNORE_SCOPE_CHANGE'] = '1'
        refresh_token = origin_token["refresh_token"]
        aad_auth = OAuth2Session(
            self.credential["client_id"],
            scope=self.credential["scopes"],
            redirect_uri=self.credential["redirect_uri"])

        new_token = aad_auth.refresh_token(
            self.token_url,
            refresh_token=refresh_token,
            client_id=self.credential["client_id"],
            client_secret=self.credential["client_secret"])
        return new_token

    def get_token_from_authorized_url(self, authorized_url, expected_state=None):
        """通过授权编码获取访问token"""

        # 忽略token scope与已请求的scope不一致
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
        os.environ['OAUTHLIB_IGNORE_SCOPE_CHANGE'] = '1'
        aad_auth = OAuth2Session(self.credential["client_id"],
                                 state=expected_state,
                                 scope=self.credential['scopes'],
                                 redirect_uri=self.credential['redirect_uri'])

        token = aad_auth.fetch_token(
            self.token_url,
            client_secret=self.credential["client_secret"],
            authorization_response=authorized_url)

        return token

    def get_token(self):
        token = self.get_store_token()
        now = time.time()

        expire_time = token["expires_at"] - 300
        if now >= expire_time:
            new_token = self.refresh_token(token)
            self.store_token(new_token)
            return new_token

        return token

    def get_sign_in_url(self):
        """生成签名地址"""

        # Initialize the OAuth client
        aad_auth = OAuth2Session(self.credential["client_id"],
                                 scope=self.credential['scopes'],
                                 redirect_uri=self.credential['redirect_uri'])

        sign_in_url, state = aad_auth.authorization_url(self.authorize_url,
                                                        prompt='login')

        return sign_in_url, state

    def get_authorized_header(self):
        token_obj = self.get_token()
        token = token_obj["access_token"]
        header = {
            "Authorization": "Bearer " + token,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/67.0.3396.99 Safari/537.36'
        }
        return header

    def get_user_from_ms(self):
        """查询用户信息"""
        try:
            headers = self.get_authorized_header()
            user_api_base = self.credential["api_uri"] + "/me"
            # select_user_info_uri = self.build_uri(base=user_api_base)
            response = requests.get(user_api_base, headers=headers)
            if DEBUG:
                print("Debug get user:")
                print(response.status_code)
                print(response.text)
            if response.status_code == 200:
                response_data = response.json()
                user_principal_name = response_data["userPrincipalName"]
                return user_principal_name
        except oauthlib.oauth2.rfc6749.errors.InvalidGrantError:
            self.clear_auth()
            if DEBUG:
                print("用户授权已过期。")
        return None

    def clear_auth(self):
        self.clear_token()
        self.clear_user()

    def clear_user(self):
        try:
            # 清空user
            path = os.path.join(self.server_dir, self.user_conf)
            if os.path.isfile(path):
                os.remove(path)
        except:
            if DEBUG:
                print("清除user失败。")

    def store_user(self):
        """更新并存储用户信息"""
        user = self.get_user_from_ms()
        if user:
            path = os.path.join(self.server_dir, self.user_conf)
            mw.writeFile(path, user)
        else:
            raise RuntimeError("无法获取用户信息。")

    # --------------------- 文件操作功能 ----------------------

    # 取目录路径
    def get_path(self, path):
        sep = ":"
        if path == '/':
            path = ''
        if path[-1:] == '/':
            path = path[:-1]
        if path[:1] != "/" and path[:1] != sep:
            path = "/" + path
        if path == '/':
            path = ''
        # if path[:1] != sep:
        #     path = sep + path
        try:
            from urllib.parse import quote
        except:
            from urllib import quote
        # path = quote(path)

        return path.replace('//', '/')

    def build_uri(self, path="", operate=None, base=None):
        """构建请求URL

        API请求URI格式参考:
            https://graph.microsoft.com/v1.0/me/drive/root:/bt_backup/:content
            ---------------------------------------------  ---------- --------
                                  base                        path    operate
        各部分之间用“：”连接。
        :param path 子资源路径
        :param operate 对文件进行的操作，比如content,children
        :return 请求url
        """

        if base is None:
            base = self.root_uri
        path = self.get_path(path)
        sep = ":"
        if operate:
            if operate[:1] != "/":
                operate = "/" + operate

        if path:
            uri = base + sep + path
            if operate:
                uri += sep + operate
        else:
            uri = base
            if operate:
                uri += operate

        return uri

    def get_list(self, path="/"):
        """获取存储空间中的所有文件对象"""

        list_uri = self.build_uri(path, operate="/children")
        if DEBUG:
            print("List uri:")
            print(list_uri)

        data = []
        response = requests.get(list_uri, headers=self.get_authorized_header())
        status_code = response.status_code
        if status_code == 200:
            if DEBUG:
                print("DEBUG:")
                print(response.json())
            response_data = response.json()
            drive_items = response_data["value"]

            for item in drive_items:
                tmp = {}
                tmp['name'] = item["name"]
                tmp['size'] = item["size"]
                if "folder" in item:
                    # print("{} is folder:".format(item["name"]))
                    # print(item["folder"])
                    tmp["type"] = None
                    tmp['download'] = ""
                if "file" in item:
                    tmp["type"] = "File"
                    tmp['download'] = item["@microsoft.graph.downloadUrl"]
                    # print("{} is file:".format(item["name"]))
                    # print(item["file"])

                formats = ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"]
                t = None
                for time_format in formats:
                    try:
                        t = datetime.datetime.strptime(
                            item["lastModifiedDateTime"], time_format)
                        break
                    except:
                        continue
                t += datetime.timedelta(hours=8)
                ts = int(
                    (time.mktime(t.timetuple()) + t.microsecond / 1000000.0))
                tmp['time'] = ts
                data.append(tmp)

        mlist = {'path': path, 'list': data}
        return mlist

    def get_object(self, object_name):
        """查询对象信息"""
        try:
            get_uri = self.build_uri(path=object_name)
            if DEBUG:
                print("Get uri:")
                print(get_uri)
            response = requests.get(get_uri,
                                    headers=self.get_authorized_header())
            if response.status_code in [200]:
                response_data = response.json()
                if DEBUG:
                    print("Object info:")
                    print(response_data)
                return response_data
            if response.status_code == 404:
                if DEBUG:
                    print("对象不存在。")
            if DEBUG:
                print("Get Object debug:")
                print(response.status_code)
                print(response.text)
        except Exception as e:
            if DEBUG:
                print("Get object has excepiton:")
                print(e)
        return None

    def is_folder(self, obj):
        if "folder" in obj:
            return True
        return False

    def delete_object_by_os(self, object_name):
        """删除对象

        :param object_name:
        :return: True 删除成功
                其他 删除失败
        """
        obj = self.get_object(object_name)
        if obj is None:
            if DEBUG:
                print("对象不存在，删除操作未执行。")
            return True
        if self.is_folder(obj):
            child_count = obj["folder"]["childCount"]
            if child_count > 0:
                if DEBUG:
                    print("文件夹不是空文件夹无法删除。")
                return False

        headers = self.get_authorized_header()
        delete_uri = self.build_uri(object_name)
        response = requests.delete(delete_uri, headers=headers)
        if response.status_code == 204:
            if DEBUG:
                print("对象: {} 已被删除。".format(object_name))
            return True
        return False

    def delete_object(self, object_name, retries=2):
        """删除对象

        :param object_name:
        :param retries: 重试次数，默认2次
        :return: True 删除成功
                其他 删除失败
        """

        try:
            return self.delete_object_by_os(object_name)
        except Exception as e:
            print("删除文件异常：")
            print(e)

        # 重试
        if retries > 0:
            print("重新尝试删除文件{}...".format(object_name))
            return self.delete_object(
                object_name,
                retries=retries - 1)
        return False

    def build_object_name(self, data_type, file_name):
        """根据数据类型构建对象存储名称

        :param data_type:
        :param file_name:
        :return:
        """

        import re

        prefix_dict = {
            "site": "web",
            "database": "db",
            "path": "path",
        }

        if not prefix_dict.get(data_type):
            print("data_type 类型错误!!!")
            exit(1)

        file_regx = prefix_dict.get(data_type) + "_(.+)_20\d+_\d+(?:\.|_)"
        sub_search = re.search(file_regx, file_name)
        sub_path_name = ""
        if sub_search:
            sub_path_name = sub_search.groups()[0]
            sub_path_name += '/'

        # 构建OS存储路径
        object_name = self.backup_path + '/' + \
            data_type + '/' + \
            sub_path_name + \
            file_name

        if object_name[:1] == "/":
            object_name = object_name[1:]

        return object_name

    def delete_file(self, file_name, data_type=None):
        """删除文件

        根据传入的文件名称和文件数据类型构建对象名称，再删除
        :param file_name:
        :param data_type: 数据类型 site/database/path
        :return: True 删除成功
                其他 删除失败
        """

        object_name = self.build_object_name(data_type, file_name)
        return self.delete_object(object_name)

    def create_dir_by_step(self, parent_folder, sub_folder):
        create_uri = self.build_uri(path=parent_folder, operate="/children")

        if DEBUG:
            print("Create dir uri:")
            print(create_uri)
        post_data = {
            "name": sub_folder,
            "folder": {"@odata.type": "microsoft.graph.folder"},
            "@microsoft.graph.conflictBehavior": "fail"
        }

        headers = self.get_authorized_header()
        headers.update({"Content-type": "application/json"})
        response = requests.post(create_uri, headers=headers, json=post_data)
        if response.status_code in [201, 409]:
            if DEBUG:
                if response.status_code == 409:
                    print("目录：{} 已经存在。".format(sub_folder))
            return True
        else:
            if DEBUG:
                print("目录：{} 创建失败：".format(sub_folder))
                print(response.status_code)
                print(response.text)
        return False

    def create_dir(self, dir_name):
        """创建远程目录

        # API 请求结构
        # POST /me/drive/root/children
        # or 
        # POST /me/drive/root:/bt_backup/:/children
        # Content - Type: application / json

        # {
        #     "name": "New Folder",
        #     "folder": {},
        #     "@microsoft.graph.conflictBehavior": "rename"
        # }

        # Response: status code == 201 新创建/ 409 已存在
        # @microsoft.graph.conflictBehavior: fail/rename/replace

        :param dir_name: 目录名称
        :param parent_id: 父目录ID
        :return: True/False
        """

        dir_name = self.get_path(dir_name.strip())
        onedrive_business_reserved = r"[\*<>?:|#%]"
        if re.search(onedrive_business_reserved, dir_name) \
                or dir_name[-1] == "." or dir_name[:1] == "~":
            if DEBUG:
                print("文件夹名称包含非法字符。")
            return False

        parent_folder = self.get_path(os.path.split(dir_name)[0])
        sub_folder = os.path.split(dir_name)[1]

        # print("create_dir:", dir_name)
        obj = self.get_object(dir_name)
        # 判断对象是否存在
        if obj is None:
            if not self.create_dir_by_step(parent_folder, sub_folder):

                # 兼容OneDrive 商业版文件夹创建
                folder_array = dir_name.split("/")
                parent_folder = self.get_path(folder_array[0])
                for i in range(1, len(folder_array)):
                    sub_folder = folder_array[i]
                    if DEBUG:
                        print("Parent folder: {}".format(parent_folder))
                        print("Sub folder: {}".format(sub_folder))
                    if self.create_dir_by_step(parent_folder, sub_folder):
                        parent_folder += "/" + folder_array[i]
                    else:
                        return False
            return True
        else:
            if self.is_folder(obj):
                if DEBUG:
                    print("文件夹已存在。")
                return True

    def resumable_upload(self,
                         local_file_name,
                         object_name=None,
                         progress_callback=None,
                         progress_file_name=None,
                         multipart_threshold=1024 * 1024 * 2,
                         part_size=1024 * 1024 * 5,
                         store_dir="/tmp",
                         auto_cancel=True,
                         retries=5,
                         ):
        """断点续传

        :param local_file_name: 本地文件名称
        :param object_name: 指定OS中存储的对象名称
        :param part_size: 指定分片上传的每个分片的大小。必须是320*1024的整数倍。
        :param multipart_threshold: 文件长度大于该值时，则用分片上传。
        :param progress_callback: 进度回调函数，默认是把进度信息输出到标准输出。
        :param progress_file_name: 进度信息保存文件，进度格式参见[report_progress]
        :param store_dir: 上传分片存储目录, 默认/tmp。
        :param auto_cancel: 当备份失败是否自动取消上传记录
        :param retries: 上传重试次数
        :return: True上传成功/False or None上传失败
        """

        try:
            file_size_separation_value = 4 * 1024 * 1024
            if part_size % 320 != 0:
                if DEBUG:
                    print("Part size 必须是320的整数倍。")
                return False

            if object_name is None:
                temp_file_name = os.path.split(local_file_name)[1]
                object_name = os.path.join(self.backup_path, temp_file_name)

            # if progress_file_name:
            #     os.environ[PROGRESS_FILE_NAME] = progress_file_name
            #     progress_callback = report_progress

            print("|-正在上传到 {}...".format(object_name))
            dir_name = os.path.split(object_name)[0]
            if not self.create_dir(dir_name):
                if DEBUG:
                    print("目录创建失败！")
                return False

            local_file_size = os.path.getsize(local_file_name)
            # if local_file_size < file_size_separation_value:
            if False:
                # 小文件上传
                upload_uri = self.build_uri(path=object_name,
                                            operate="/content")
                if DEBUG:
                    print("Upload uri:")
                    print(upload_uri)
                headers = self.get_authorized_header()
                # headers.update({
                #     "Content-Type": "application/octet-stream"
                # })
                # files = {"file": (object_name, open(local_file_name, "rb"))}
                file_data = open(local_file_name, "rb")
                response = requests.put(upload_uri,
                                        headers=headers,
                                        data=file_data)
                if DEBUG:
                    print("status code:")
                    print(response.status_code)
                    # print(response.text)
                if response.status_code in [201, 200]:
                    if DEBUG:
                        print("文件上传成功！")
                    return True
            else:
                # 大文件上传

                # 1. 创建上传session
                create_session_uri = self.build_uri(
                    path=object_name,
                    operate="createUploadSession")
                headers = self.get_authorized_header()
                response = requests.post(create_session_uri, headers=headers)
                if response.status_code == 200:
                    response_data = response.json()
                    upload_url = response_data["uploadUrl"]
                    expiration_date_time = response_data["expirationDateTime"]

                    if DEBUG:
                        print("上传session已建立。")
                        print("Upload url: {}".format(upload_url))
                        print("Expiration datetime: {}".format(
                            expiration_date_time))

                    # 2. 分片上传文件
                    requests.adapters.DEFAULT_RETRIES = 1
                    session = requests.session()
                    session.keep_alive = False

                    # 开始分片上传
                    import math
                    parts = int(math.ceil(local_file_size / part_size))
                    for i in range(parts):
                        if DEBUG:
                            if i == parts - 1:
                                num = "最后"
                            else:
                                num = "第{}".format(i + 1)
                            print("正在上传{}部分...".format(num))

                        upload_range_start = i * part_size
                        upload_range_end = min(upload_range_start + part_size,
                                               local_file_size)
                        content_length = upload_range_end - upload_range_start

                        headers = {
                            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                                          'Chrome/67.0.3396.99 Safari/537.36'
                        }
                        # 开发记录
                        # Content-Range和标准的http请求头中的Range作用有所不同
                        # Content-Range是OneDrive自定义的分片上传标识，格式也不一样
                        headers.update({
                            "Content-Length": repr(content_length),
                            "Content-Range": "bytes {}-{}/{}".format(
                                upload_range_start,
                                upload_range_end - 1,
                                local_file_size),
                            "Content-Type": "application/octet-stream"
                        })

                        if DEBUG:
                            print("Headers:")
                            print(headers)

                        '''# TODO 优化read的读取占用内存'''
                        f = io.open(local_file_name, "rb")
                        f.seek(upload_range_start)
                        upload_data = f.read(content_length)
                        sub_response = session.put(upload_url,
                                                   headers=headers,
                                                   data=upload_data)

                        expected_status_code = [200, 201, 202]
                        if sub_response.status_code in expected_status_code:
                            if DEBUG:
                                print("Response status code: {}, "
                                      "bytes {}-{} 已上传成功。".format(
                                          sub_response.status_code,
                                          upload_range_start,
                                          upload_range_end - 1)
                                      )
                                print(sub_response.text)
                            if sub_response.status_code in [200, 201]:
                                if DEBUG:
                                    print("文件 {} 上传成功。".format(object_name))
                                return True
                        else:
                            print(sub_response.status_code)
                            print(sub_response.text)
                            _error_msg = "Bytes {}-{} 分片上传失败。".format(
                                upload_range_start,
                                upload_range_end
                            )
                            if self.error_msg:
                                self.error_msg += r"\n"
                            self.error_msg += _error_msg
                            raise RuntimeError(_error_msg)

                        time.sleep(0.5)
                else:
                    raise RuntimeError("session创建失败。")

        except UnauthorizedError as e:
            _error_msg = str(e)
            if self.error_msg:
                self.error_msg += r"\n"
            self.error_msg += _error_msg
            print(_error_msg)
            return False
        except Exception as e:
            print("文件上传出现错误：")
            print(e)

            if self.error_msg:
                self.error_msg += r"\n"
            self.error_msg += "文件{}上传出现错误：{}".format(object_name, str(e))

            try:
                if upload_url:
                    if DEBUG:
                        print("正在清理上传session.")
                    session.delete(upload_url)
            except:
                pass
        finally:
            try:
                f.close()
            except:
                pass
            try:
                session.close()
            except:
                pass

        # 重试断点续传
        if retries > 0:
            print("重试上传文件....")
            return self.resumable_upload(
                local_file_name,
                object_name=object_name,
                store_dir=store_dir,
                part_size=part_size,
                multipart_threshold=multipart_threshold,
                progress_callback=progress_callback,
                progress_file_name=progress_file_name,
                retries=retries - 1,
            )
        else:
            if self.error_msg:
                self.error_msg += r"\n"
            self.error_msg += "文件{}上传失败。".format(object_name)
        return False

    def upload_abs_file(self, file_name, remote_dir, *args, **kwargs):
        """按照数据类型上传文件

        :param file_name: 上传文件名称
        :param data_type: 数据类型 site/database/path
        :return: True/False
        """
        try:
            import re
            # 根据数据类型提取子分类名称
            # 比如data_type=database，子分类名称是数据库的名称。
            # 提取方式是从file_name中利用正则规则去提取。
            self.error_msg = ""

            file_name = os.path.abspath(file_name)
            temp_name = os.path.split(file_name)[1]
            object_name = 'backup/' + temp_name

            print(file_name)
            print(object_name)

            return self.resumable_upload(file_name,
                                         object_name=object_name,
                                         *args,
                                         **kwargs)
        except Exception as e:
            if self.error_msg:
                self.error_msg += r"\n"
            self.error_msg += "文件上传出现错误：{}".format(str(e))
            return False

    def upload_file(self, file_name, data_type, *args, **kwargs):
        """按照数据类型上传文件

        :param file_name: 上传文件名称
        :param data_type: 数据类型 site/database/path
        :return: True/False
        """
        try:
            import re
            # 根据数据类型提取子分类名称
            # 比如data_type=database，子分类名称是数据库的名称。
            # 提取方式是从file_name中利用正则规则去提取。
            self.error_msg = ""

            if not file_name or not data_type:
                _error_msg = "文件参数错误。"
                print(_error_msg)
                self.error_msg = _error_msg
                return False

            file_name = os.path.abspath(file_name)
            temp_name = os.path.split(file_name)[1]
            object_name = self.build_object_name(data_type, temp_name)

            # dir_name = os.path.dirname(object_name)
            # self.create_dir(dir_name)
            if DEBUG:
                print(file_name)
                print(object_name)
                print(dir_name)

            return self.resumable_upload(file_name,
                                         object_name=object_name,
                                         *args,
                                         **kwargs)
        except Exception as e:
            if self.error_msg:
                self.error_msg += r"\n"
            self.error_msg += "文件上传出现错误：{}".format(str(e))
            return False
