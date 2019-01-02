# coding: utf-8

import psutil
import time
import os
import sys
import public
import re
import json
import pwd


class config_api:

    def __init__(self):
        pass

    ##### ----- start ----- ###
    def get(self):

        data = {}

        data['site_path'] = public.getWwwDir()
        data['backup_path'] = public.getBackupDir()
        data['systemdate'] = public.execShell(
            'date +"%Y-%m-%d %H:%M:%S %Z %z"')[0].strip()

        if os.path.exists('data/port.pl'):
            data['port'] = public.readFile('data/port.pl').strip()
        else:
            data['port'] = '7200'

        if os.path.exists('data/iplist.txt'):
            data['ip'] = public.readFile('data/iplist.txt').strip()
        else:
            data['ip'] = '127.0.0.1'

        return data
    ##### ----- end ----- ###
