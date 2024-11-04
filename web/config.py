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

import core.mw as mw

from branding import APP_NAME, APP_ICON, APP_COPYRIGHT, APP_LOG_NAME, APP_SQLITE_NAME
from version import APP_VERSION, APP_RELEASE, APP_REVISION, APP_SUFFIX

DEBUG = False

# 配置数据库连接池大小。将其设置为0将删除任何限制
CONFIG_DATABASE_CONNECTION_POOL_SIZE = 20
# 允许溢出超过连接池大小的连接数
CONFIG_DATABASE_CONNECTION_MAX_OVERFLOW = 100

# 应用程序日志级别-其中之一:
#   CRITICAL 50
#   ERROR    40
#   WARNING  30
#   SQL      25
#   INFO     20
#   DEBUG    10
#   NOTSET    0
CONSOLE_LOG_LEVEL = logging.WARNING
FILE_LOG_LEVEL = logging.WARNING

DATA_DIR = mw.getPanelDataDir()

# 日志文件名。这将进入数据目录，服务器模式下的非Windows平台除外。
LOG_FILE = os.path.join(mw.getMWLogs(), APP_LOG_NAME + '.log')

# 日志旋转设置日志文件将根据LOG_ROTATION_SIZE和LOG_ROTATION_AGE的值进行切换。
# 旋转的文件将以格式命名Y-m-d_H-M-S
LOG_ROTATION_SIZE = 10  # MBs
LOG_ROTATION_AGE = 1440  # minutes
LOG_ROTATION_MAX_LOG_FILES = 90  # 要保留的最大备份数

# 用于存储用户帐户和设置的SQLite数据库的默认路径。
# 此默认设置将文件放置在与此相同的目录中 配置文件，但会生成一个在整个应用程序中使用的绝对路径。
SQLITE_PATH = os.path.join(DATA_DIR, APP_SQLITE_NAME + '.db')


DEFAULT_SERVER = '127.0.0.1'
DEFAULT_SERVER_PORT = 7201

# APP启动时间
APP_START_TIME=0

