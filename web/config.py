# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------
# 配置信息
# ---------------------------------------------------------------------------------


import builtins
import logging
import os
import sys

from branding import APP_NAME, APP_ICON, APP_COPYRIGHT
from version import APP_VERSION, APP_RELEASE, APP_REVISION, APP_SUFFIX

DEBUG = False

DEFAULT_SERVER = '127.0.0.1'

DEFAULT_SERVER_PORT = 7200