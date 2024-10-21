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

# 配置数据库连接池大小。将其设置为0将删除任何限制
CONFIG_DATABASE_CONNECTION_POOL_SIZE = 5
# 允许溢出超过连接池大小的连接数
CONFIG_DATABASE_CONNECTION_MAX_OVERFLOW = 100



DEFAULT_SERVER = '127.0.0.1'
DEFAULT_SERVER_PORT = 7201

