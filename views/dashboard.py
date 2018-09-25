# coding:utf-8

from flask import Flask
from flask import Blueprint,render_template
from flask import jsonify
import psutil,time



dashboard = Blueprint('dashboard', __name__, template_folder='templates')

@dashboard.route("/")
def index():
    return render_template('default/index.html')

@dashboard.route("getnetwork")
def getnetwork():
        #取网络流量信息
        networkIo = psutil.net_io_counters()[:4]
        # if not hasattr(web.ctx.session,'otime'):
          	# web.ctx.session.up   =  networkIo[0]
           #  web.ctx.session.down =  networkIo[1]
           #  web.ctx.session.otime = time.time();
        
        ntime = time.time();
        networkInfo = {}
        networkInfo['upTotal']   = networkIo[0]
        networkInfo['downTotal'] = networkIo[1]
        # networkInfo['up']        = round(float(networkIo[0] - web.ctx.session.up) / 1024 / (ntime - web.ctx.session.otime),2)
        # networkInfo['down']      = round(float(networkIo[1] - web.ctx.session.down) / 1024 / (ntime - web.ctx.session.otime),2)
        networkInfo['downPackets'] =networkIo[3]
        networkInfo['upPackets']   =networkIo[2]
        
        # web.ctx.session.up   =  networkIo[0]
        # web.ctx.session.down =  networkIo[1]
        # web.ctx.session.otime = ntime;
        
        # networkInfo['cpu'] = self.GetCpuInfo()
        # networkInfo['load'] = self.GetLoadAverage(get);
        return jsonify(networkInfo) 