#coding: utf8
import requests
import sys
import time
import urlparse
import datetime
import xmlrpclib

from flask import Flask, request, abort
import pygeoip

from bencode import bencode

geoip = pygeoip.GeoIP('GeoIP.dat')

app = Flask(__name__)
app.debug = False
rpc = xmlrpclib.ServerProxy('http://127.0.0.1:8004')

@app.route('/announce.php')
def announce():
    '''/announce.php?info_hash=&peer_id=&ip=&port=&uploaded=&downloaded=&left=&numwant=&key=&compact=1'''
    ip = request.args.get('ip')
    port = request.args.get('port')
    if not ip or not port:
        return abort(404)
    address = (ip, int(port))
    binhash = urlparse.parse_qs(request.query_string)['info_hash'][0]
    country = geoip.country_code_by_addr(ip)
    if country not in ('CN','TW','JP','HK', 'KR'):
        return abort(404)
    rpc.announce(binhash.encode('hex'), address)
    return bencode({'peers': '', 'interval': 86400})


@app.route('/announce/m3u8')
def m3u8():
    url = 'http://tsymq.aliapp.com/baidu/file/index.php?uid=4013230200&uuid=56178f0f05b22&w=100%&h=100%&type=m3u8'
    r = requests.get(url)
    return r.content


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8005)

