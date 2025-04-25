# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os
import sys
import re
import json
import time
import threading
import multiprocessing

import core.mw as mw
import thisdb

def parse():

	sdir = mw.getServerDir()
	nginx_conf = sdir + "/web_conf/nginx"
	vhosts = nginx_conf+"/vhost"

	vh_list = os.listdir(vhosts)

	vail_list = []
	for f in vh_list:
		if f.startswith("0."):
			continue
		if f.endswith("_bak"):
			continue
		if f.startswith("phpmyadmin"):
			continue
		if f.startswith("webstats"):
			continue
		vail_list.append(f)

	for vail_f in vail_list:
		print(vail_f)

def parseSite(domain):
	print(domain)

	