# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os

from .user import init_admin_user
from .option import init_option
from .init_db_system import init_db_system
from .init_cmd import init_cmd

from utils.firewall import Firewall as MwFirewall

import thisdb
import config

def init():
	# 检查数据库是否存在。如果没有就创建它。
	if not os.path.isfile(config.SQLITE_PATH):
	    # 初始化用户信息
	    thisdb.initPanelData()
	    init_admin_user()
	    init_option()
	    init_db_system()

	init_cmd()

	# 自动识别防火墙配置
	firewall_port = thisdb.getOption('setpu_auto_identify_firewall_port', default='no')
	if firewall_port == 'no':
		MwFirewall.instance().aIF()
		thisdb.setOption('setpu_auto_identify_firewall_port', 'yes')

