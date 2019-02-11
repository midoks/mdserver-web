# coding: utf-8

import psutil
import time
import os
import sys
import public
import re
import json
import pwd

from flask import session
from flask import request


class ssl_api:

    def __init__(self):
        pass

    ##### ----- start ----- ###
    # 获取证书列表
    def getCertListApi(self):
        try:
            vpath = public.getServerDir() + '/ssl'
            if not os.path.exists(vpath):
                os.system('mkdir -p ' + vpath)
            data = []
            for d in os.listdir(vpath):
                mpath = vpath + '/' + d + '/info.json'
                if not os.path.exists(mpath):
                    continue
                tmp = public.readFile(mpath)
                if not tmp:
                    continue
                tmp1 = json.loads(tmp)
                data.append(tmp1)
            return public.returnJson(True, 'OK', data)
        except:
            return public.returnJson(True, 'OK', [])
    ##### ----- end ----- ###
