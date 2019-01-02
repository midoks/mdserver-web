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

        return data
    ##### ----- end ----- ###
