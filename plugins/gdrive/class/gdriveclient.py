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

# -----------------------------
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload


class gdriveclient():
    __plugin_dir = ''
    __server_dir = ''

    __credentials = "/root/credentials.json"
    __backup_dir_name = "backup"
    __creds = None
    __exclude = ""
    __scpos = ['https://www.googleapis.com/auth/drive.file']
    _title = 'Google Drive'
    _name = 'Google Drive'
    __debug = False

    _DEFAULT_AUTH_PROMPT_MESSAGE = (
        'Please visit this URL to authorize this application: {url}')
    """str: The message to display when prompting the user for
    authorization."""
    _DEFAULT_AUTH_CODE_MESSAGE = (
        'Enter the authorization code: ')
    """str: The message to display when prompting the user for the
    authorization code. Used only by the console strategy."""

    _DEFAULT_WEB_SUCCESS_MESSAGE = (
        'The authentication flow has completed, you may close this window.')

    def __init__(self, plugin_dir, server_dir):
        self.__plugin_dir = plugin_dir
        self.__server_dir = server_dir
        self.set_creds()

        # self.get_exclode()

    def setDebug(self, d=False):
        self.__debug = d

    def D(self, msg=''):
        if self.__debug:
            print(msg)

    # 检查gdrive连接
    def _check_connect(self):
        try:
            service = build('drive', 'v3', credentials=self.__creds)
            results = service.files().list(
                pageSize=10, fields="nextPageToken, files(id, name)").execute()
            results.get('files', [])
        except:
            return False
        return True

    # 设置creds
    def set_creds(self):
        token_file = self.__server_dir + '/token.json'
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                tmp_data = json.load(token)['credentials']
                self.__creds = google.oauth2.credentials.Credentials(
                    tmp_data['token'],
                    tmp_data['refresh_token'],
                    tmp_data['id_token'],
                    tmp_data['token_uri'],
                    tmp_data['client_id'],
                    tmp_data['client_secret'],
                    tmp_data['scopes'])
            # if not self._check_connect():
            #     return False
            # else:
            #     return True

    def get_sign_in_url(self):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            self.__plugin_dir + '/credentials.json',
            scopes=self.__scpos)
        # flow.redirect_uri = 'https://drive.aapanel.com'
        flow.redirect_uri = 'https://drive.aapanel.com'
        auth_url, state = flow.authorization_url(
            access_type='offline',
            prompt='consent',
            include_granted_scopes='false')
        return auth_url, state

    def set_auth_url(self, url):
        token_file = self.__server_dir + '/token.json'
        if os.path.exists(token_file):
            return mw.returnJson(True, "验证成功")

        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            self.__plugin_dir + '/credentials.json',
            scopes=self.__scpos,
            state=url.split('state=')[1].split('&code=')[0])
        # flow.redirect_uri = 'https://localhost'
        flow.redirect_uri = 'https://drive.aapanel.com'
        flow.fetch_token(authorization_response=url)
        credentials = flow.credentials

        credentials_data = {}
        credentials_data['credentials'] = {
            'token': credentials.token,
            'id_token': credentials.id_token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}
        with open(token_file, 'w') as token:
            json.dump(credentials_data, token)
        if not self.set_creds():
            return mw.returnJson(False, "验证失败，请根据页面1 2 3 步骤完成验证")
        return mw.returnJson(True, "验证成功")

    # 获取token
    def get_token(self, get):
        token_file = self.__server_dir + '/token.json'
        import requests
        try:
            respone = requests.get("https://www.google.com", timeout=2)
        except:
            return mw.returnJson(False, "连接谷歌失败")
        if respone.status_code != 200:
            return mw.returnJson(False, "连接谷歌失败")
        if not self.set_creds():
            return mw.returnJson(False, "验证失败，请根据页面1 2 3 步骤完成验证")
        if not os.path.exists(token_file):
            return mw.returnJson(False, "验证失败，请根据页面1 2 3 步骤完成验证")
        return mw.returnJson(True, "验证成功")

    # 获取auth_url
    def get_auth_url(self, get):
        self.get_sign_in_url()
        if os.path.exists("/tmp/auth_url"):
            return mw.readFile("/tmp/auth_url")

    # 检查连接
    def check_connect(self, get):
        token_file = self.__server_dir + '/token.json'
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                self.set_creds()
        else:
            self.D("Failed to get Google token, please verify before use")
            return mw.returnJson(True, "Failed to get Google token, please verify before use")
        service = build('drive', 'v3', credentials=self.__creds)
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        try:
            results.get('files', [])
            return mw.returnJson(False, "验证失败，请根据页面1 2 3 步骤完成验证")
            return mw.returnJson(True, "验证成功")
        except:
            return mw.returnJson(False, "验证失败，请根据页面1 2 3 步骤完成验证")

    def _get_filename(self, filename):
        l = filename.split("/")
        return l[-1]

    def _create_folder_cycle(self, filepath):
        l = filepath.split("/")
        fid_list = []
        for i in l:
            if not i:
                continue
            fid = self.__get_folder_id(i)
            if fid:
                fid_list.append(fid)
                continue
            if not fid_list:
                fid_list.append("")
            fid_list.append(self.create_folder(i, fid_list[-1]))
        return fid_list[-1]

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

        file_regx = prefix_dict.get(data_type) + "_(.+)_20\d+_\d+\."
        sub_search = re.search(file_regx.lower(), file_name)
        sub_path_name = ""
        if sub_search:
            sub_path_name = sub_search.groups()[0]
            sub_path_name += '/'
        # 构建OS存储路径
        object_name = self.__backup_dir_name + \
            '/{}/{}'.format(data_type, sub_path_name)

        if object_name[:1] == "/":
            object_name = object_name[1:]
        return object_name

    # 上传文件
    def upload_file(self, filename, data_type=None):
        """
        get.filename 上传后的文件名
        get.filepath 上传文件路径
        被面板新版计划任务调用时
        get表示file_name
        :param get:
        :return:
        """
        # filename = filename
        filepath = self.build_object_name(data_type, filename)
        _filename = self._get_filename(filename)
        self.D(filepath)
        self.D(filename)

        parents = self._create_folder_cycle(filepath)
        self.D(parents)
        drive_service = build('drive', 'v3', credentials=self.__creds)
        file_metadata = {'name': _filename, 'parents': [parents]}
        media = MediaFileUpload(filename, resumable=True)
        file = drive_service.files().create(
            body=file_metadata, media_body=media, fields='id').execute()
        self.D('Upload Success ,File ID: %s' % file.get('id'))
        return True

    def _get_file_id(self, filename):
        service = build('drive', 'v3', credentials=self.__creds)
        results = service.files().list(pageSize=10, q="name='{}'".format(
            filename), fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            return []
        else:
            for item in items:
                return item["id"]

    def delete_file(self, filename=None, data_type=None):
        file_id = self._get_file_id(filename)
        self.delete_file_by_id(file_id)
        return True

    def delete_file_by_id(self, file_id):
        self.D("delete id:{}".format(file_id))
        try:
            drive_service = build('drive', 'v3', credentials=self.__creds)
            drive_service.files().delete(fileId=file_id).execute()
            return True
        except Exception as e:
            return False

    # 创建目录
    def create_folder(self, folder_name, parents=""):
        self.D(self.__creds)
        self.D("folder_name: {}".format(folder_name))
        self.D("parents: {}".format(parents))
        service = build('drive', 'v3', credentials=self.__creds)
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parents:
            file_metadata['parents'] = [parents]
        folder = service.files().create(body=file_metadata, fields='id').execute()
        self.D('Create Folder ID: %s' % folder.get('id'))
        return folder.get('id')

    def get_rootdir_id(self, folder_name='backup'):
        service = build('drive', 'v3', credentials=self.__creds)
        results = service.files().list(pageSize=10, q="name='{}' and mimeType='application/vnd.google-apps.folder'".format(folder_name),
                                       fields="nextPageToken, files(id, name,size,parents,webViewLink)").execute()
        items = results.get('files', [])
        if len(items) == 0:
            self.create_folder(folder_name)
            return self.get_rootdir_id(folder_name)

        return items[0]['parents'][0]

    # 获取目录id
    def __get_folder_id(self, floder_name):
        service = build('drive', 'v3', credentials=self.__creds)
        results = service.files().list(pageSize=10, q="name='{}' and mimeType='application/vnd.google-apps.folder'".format(floder_name),
                                       fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            return []
        else:
            for item in items:
                return item["id"]

    def get_res_info(self, rid):
        service = build('drive', 'v3', credentials=self.__creds)
        results = service.files().get(fileId='{}'.format(rid)).execute()
        return results

    def get_id_list(self, driveId=''):
        service = build('drive', 'v3', credentials=self.__creds)
        results = service.files().list(pageSize=10, driveId="{}".format(driveId),
                                       fields="nextPageToken, files(id, name,size,parents)").execute()
        items = results.get('files', [])
        return items

    def get_list(self, dir_id='', next_page_token=''):
        if dir_id == '':
            dir_id = self.get_rootdir_id(self.__backup_dir_name)

        service = build('drive', 'v3', credentials=self.__creds)
        cmd_query = "trashed=false and '{}' in parents".format(dir_id)
        results = service.files().list(pageSize=10, q=cmd_query, orderBy='folder asc',
                                       fields="nextPageToken, files(id, name,size,createdTime,parents,webViewLink)").execute()
        items = results.get('files', [])
        nextPageToken = results.get('nextPageToken', [])
        # print(items)
        # print(nextPageToken)
        return items

    def get_exclode(self, exclude=[]):
        if not exclude:
            tmp_exclude = os.getenv('MW_EXCLUDE')
            if tmp_exclude:
                exclude = tmp_exclude.split(',')
        if not exclude:
            return ""
        for ex in exclude:
            self.__exclude += " --exclude=\"" + ex + "\""
        self.__exclude += " "
        return self.__exclude

    def download_file(self, filename):
        file_id = self._get_file_id(filename)
        service = build('drive', 'v3', credentials=self.__creds)
        request = service.files().get_media(fileId=file_id)
        with open('/tmp/{}'.format(filename), 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100))
