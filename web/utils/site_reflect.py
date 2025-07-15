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

def getVhostDir():
	sdir = mw.getServerDir()
	nginx_conf = sdir + "/web_conf/nginx"
	vhosts = nginx_conf+"/vhost"
	return vhosts

def getRootDir(content):
	pattern = r'\s*root\s*(.+);'
	match = re.search(pattern, content)
	if match:
		return match.group(1)
	return ''

def getServerName(content):
	pattern = r'\s*server_name\s*(.+);'
	match = re.search(pattern, content)
	if match:
		content = match.group(1)
		clist = content.strip().split(" ");
		return clist
	return []

def addDomain(site_id, site_name, domain):
	# print(site_id, site_name, domain)
	d = domain.split(':')
	port = '80'
	name = d[0]
	if len(d) == 2:
		port = d[1]
	if thisdb.checkSitesDomainIsExist(name, port):
		print('您添加的域名[{}:{}],已使用。请仔细检查!'.format(name, port))
		return True
	thisdb.addDomain(site_id, name, port)
	return True

def parse():
	vhosts = getVhostDir()
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
		if f.startswith("panel"):
			continue
		vail_list.append(f)

	for vail_domain in vail_list:
		parseSite(vail_domain)

def parseSite(d):
	vhosts = getVhostDir()
	domain = d.replace(".conf","")

	dconf = vhosts + '/' + d
	content = mw.readFile(dconf)

	root_dir = getRootDir(content)
	sn_list = getServerName(content)

	if thisdb.isSitesExist(domain):
		print('您添加的站点[%s]已存在!' % domain)
	else:
		thisdb.addSites(domain, root_dir)
	info = thisdb.getSitesByName(domain)
	site_id = info['id']

	for sn in sn_list:
		addDomain(site_id, d, sn)
