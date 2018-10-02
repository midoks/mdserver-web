#!/usr/bin/python
#coding: utf-8
#-----------------------------
# 宝塔Linux面板网站备份工具 - ALIOSS
#-----------------------------
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
os.chdir('/www/server/panel');
sys.path.append("class/")
import public,web

class btyw_main:
    def GetIndex(self,get):
        try:
            if hasattr(web.ctx.session,'btyw'): return False;
            result = public.httpGet('https://www.bt.cn/lib/btyw.html');
            public.writeFile('/www/server/panel/plugin/btyw/index.html',result);
            web.ctx.session.btyw = True;
            return True;
        except:
            return False;