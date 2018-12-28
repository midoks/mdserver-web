#!/usr/bin/env python
# encoding: utf-8
"""
磁力搜索meta信息入库程序
xiaoxia@xiaoxia.org
2015.6 Forked CreateChen's Project: https://github.com/CreateChen/simDownloader
2016.12！冰剑 ！新增功能：过滤恶意推广网址的无效磁力链接
"""

import hashlib
import os
import SimpleXMLRPCServer
import time
import datetime
import traceback
import sys
import json
import socket
import threading
from hashlib import sha1
from random import randint
from struct import unpack
from socket import inet_ntoa
from threading import Timer, Thread
from time import sleep
from collections import deque
from Queue import Queue

import pygeoip
import MySQLdb as mdb
try:
    raise
    import libtorrent as lt
    import ltMetadata
except:
    lt = None
    print sys.exc_info()[1]

import metautils
import simMetadata
from bencode import bencode, bdecode
from metadata import save_metadata

DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PORT = 3306
DB_PASS = ''
DB_NAME = 'ssbc'
BLACK_FILE = 'black_list.txt'

BOOTSTRAP_NODES = (
    ("router.bittorrent.com", 6881),
    ("dht.transmissionbt.com", 6881),
    ("router.utorrent.com", 6881)
)
TID_LENGTH = 2
RE_JOIN_DHT_INTERVAL = 3
TOKEN_LENGTH = 2

MAX_QUEUE_LT = 30
MAX_QUEUE_PT = 200

geoip = pygeoip.GeoIP('GeoIP.dat')

def load_res_blacklist(black_list_path):
    black_list = []
    file_path = os.path.join(os.path.dirname(__file__), black_list_path)
    f = open(file_path, 'r')
    while True:
        line = f.readline()
        if not(line):
            break
        black_list.append(line)
    f.close()
    return black_list

def is_ip_allowed(ip):
    return geoip.country_code_by_addr(ip) not in ('CN','TW','HK')

def entropy(length):
    return "".join(chr(randint(0, 255)) for _ in xrange(length))


def random_id():
    h = sha1()
    h.update(entropy(20))
    return h.digest()


def decode_nodes(nodes):
    n = []
    length = len(nodes)
    if (length % 26) != 0:
        return n

    for i in range(0, length, 26):
        nid = nodes[i:i+20]
        ip = inet_ntoa(nodes[i+20:i+24])
        port = unpack("!H", nodes[i+24:i+26])[0]
        n.append((nid, ip, port))

    return n


def timer(t, f):
    Timer(t, f).start()


def get_neighbor(target, nid, end=10):
    return target[:end]+nid[end:]


class KNode(object):

    def __init__(self, nid, ip, port):
        self.nid = nid
        self.ip = ip
        self.port = port


class DHTClient(Thread):

    def __init__(self, max_node_qsize):
        Thread.__init__(self)
        self.setDaemon(True)
        self.max_node_qsize = max_node_qsize
        self.nid = random_id()
        self.nodes = deque(maxlen=max_node_qsize)

    def send_krpc(self, msg, address):
        try:
            self.ufd.sendto(bencode(msg), address)
        except Exception:
            pass

    def send_find_node(self, address, nid=None):
        nid = get_neighbor(nid, self.nid) if nid else self.nid
        tid = entropy(TID_LENGTH)
        msg = {
            "t": tid,
            "y": "q",
            "q": "find_node",
            "a": {
                "id": nid,
                "target": random_id()
            }
        }
        self.send_krpc(msg, address)

    def join_DHT(self):
        for address in BOOTSTRAP_NODES:
            self.send_find_node(address)

    def re_join_DHT(self):
        if len(self.nodes) == 0:
            self.join_DHT()
        timer(RE_JOIN_DHT_INTERVAL, self.re_join_DHT)

    def auto_send_find_node(self):
        wait = 1.0 / self.max_node_qsize
        while True:
            try:
                node = self.nodes.popleft()
                self.send_find_node((node.ip, node.port), node.nid)
            except IndexError:
                pass
            try:
                sleep(wait)
            except KeyboardInterrupt:
                os._exit(0)

    def process_find_node_response(self, msg, address):
        nodes = decode_nodes(msg["r"]["nodes"])
        for node in nodes:
            (nid, ip, port) = node
            if len(nid) != 20: continue
            if ip == self.bind_ip: continue
            n = KNode(nid, ip, port)
            self.nodes.append(n)


class DHTServer(DHTClient):

    def __init__(self, master, bind_ip, bind_port, max_node_qsize):
        DHTClient.__init__(self, max_node_qsize)

        self.master = master
        self.bind_ip = bind_ip
        self.bind_port = bind_port

        self.process_request_actions = {
            "get_peers": self.on_get_peers_request,
            "announce_peer": self.on_announce_peer_request,
        }

        self.ufd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.ufd.bind((self.bind_ip, self.bind_port))

        timer(RE_JOIN_DHT_INTERVAL, self.re_join_DHT)


    def run(self):
        self.re_join_DHT()
        while True:
            try:
                (data, address) = self.ufd.recvfrom(65536)
                msg = bdecode(data)
                self.on_message(msg, address)
            except Exception:
                pass

    def on_message(self, msg, address):
        try:
            if msg["y"] == "r":
                if msg["r"].has_key("nodes"):
                    self.process_find_node_response(msg, address)
            elif msg["y"] == "q":
                try:
                    self.process_request_actions[msg["q"]](msg, address)
                except KeyError:
                    self.play_dead(msg, address)
        except KeyError:
            pass

    def on_get_peers_request(self, msg, address):
        try:
            infohash = msg["a"]["info_hash"]
            tid = msg["t"]
            nid = msg["a"]["id"]
            token = infohash[:TOKEN_LENGTH]
            msg = {
                "t": tid,
                "y": "r",
                "r": {
                    "id": get_neighbor(infohash, self.nid),
                    "nodes": "",
                    "token": token
                }
            }
            self.master.log_hash(infohash, address)
            self.send_krpc(msg, address)
        except KeyError:
            pass

    def on_announce_peer_request(self, msg, address):
        try:
            infohash = msg["a"]["info_hash"]
            token = msg["a"]["token"]
            nid = msg["a"]["id"]
            tid = msg["t"]

            if infohash[:TOKEN_LENGTH] == token:
                if msg["a"].has_key("implied_port ") and msg["a"]["implied_port "] != 0:
                    port = address[1]
                else:
                    port = msg["a"]["port"]
                self.master.log_announce(infohash, (address[0], port))
        except Exception:
            print 'error'
            pass
        finally:
            self.ok(msg, address)

    def play_dead(self, msg, address):
        try:
            tid = msg["t"]
            msg = {
                "t": tid,
                "y": "e",
                "e": [202, "Server Error"]
            }
            self.send_krpc(msg, address)
        except KeyError:
            pass

    def ok(self, msg, address):
        try:
            tid = msg["t"]
            nid = msg["a"]["id"]
            msg = {
                "t": tid,
                "y": "r",
                "r": {
                    "id": get_neighbor(nid, self.nid)
                }
            }
            self.send_krpc(msg, address)
        except KeyError:
            pass


class Master(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.setDaemon(True)
        self.queue = Queue()
        self.metadata_queue = Queue()
        self.dbconn = mdb.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME, port=DB_PORT, charset='utf8')
        self.dbconn.autocommit(False)
        self.dbcurr = self.dbconn.cursor()
        self.dbcurr.execute('SET NAMES utf8')
        self.n_reqs = self.n_valid = self.n_new = 0
        self.n_downloading_lt = self.n_downloading_pt = 0
        self.visited = set()
        self.black_list = load_res_blacklist(BLACK_FILE)

    def got_torrent(self):
        binhash, address, data, dtype, start_time = self.metadata_queue.get()
        if dtype == 'pt':
            self.n_downloading_pt -= 1
        elif dtype == 'lt':
            self.n_downloading_lt -= 1
        if not data:
            return
        self.n_valid += 1

        save_metadata(self.dbcurr, binhash, address, start_time, data,self.black_list)
        self.n_new += 1


    def run(self):
        self.name = threading.currentThread().getName()
        print self.name, 'started'
        while True:
            while self.metadata_queue.qsize() > 0:
                self.got_torrent()
            address, binhash, dtype = self.queue.get()
            if binhash in self.visited:
                continue
            if len(self.visited) > 100000:
                self.visited = set()
            self.visited.add(binhash)

            self.n_reqs += 1
            info_hash = binhash.encode('hex')

            utcnow = datetime.datetime.utcnow()
            date = (utcnow + datetime.timedelta(hours=8))
            date = datetime.datetime(date.year, date.month, date.day)

            # Check if we have this info_hash
            self.dbcurr.execute('SELECT id FROM search_hash WHERE info_hash=%s', (info_hash,))
            y = self.dbcurr.fetchone()
            if y:
                self.n_valid += 1
                # 更新最近发现时间，请求数
                self.dbcurr.execute('UPDATE search_hash SET last_seen=%s, requests=requests+1 WHERE info_hash=%s', (utcnow, info_hash))
            else:
                if dtype == 'pt':
                    t = threading.Thread(target=simMetadata.download_metadata, args=(address, binhash, self.metadata_queue))
                    t.setDaemon(True)
                    t.start()
                    self.n_downloading_pt += 1
                elif dtype == 'lt' and self.n_downloading_lt < MAX_QUEUE_LT:
                    t = threading.Thread(target=ltMetadata.download_metadata, args=(address, binhash, self.metadata_queue))
                    t.setDaemon(True)
                    t.start()
                    self.n_downloading_lt += 1

            if self.n_reqs >= 1000:
                self.dbcurr.execute('INSERT INTO search_statusreport(date,new_hashes,total_requests, valid_requests)  VALUES(%s,%s,%s,%s) ON DUPLICATE KEY UPDATE ' +
                    'total_requests=total_requests+%s, valid_requests=valid_requests+%s, new_hashes=new_hashes+%s',
                    (date, self.n_new, self.n_reqs, self.n_valid, self.n_reqs, self.n_valid, self.n_new))
                self.dbconn.commit()
                print '\n', time.ctime(), 'n_reqs', self.n_reqs, 'n_valid', self.n_valid, 'n_new', self.n_new, 'n_queue', self.queue.qsize(), 
                print 'n_d_pt', self.n_downloading_pt, 'n_d_lt', self.n_downloading_lt, 
                self.n_reqs = self.n_valid = self.n_new = 0

    def log_announce(self, binhash, address=None):
        self.queue.put([address, binhash, 'pt'])

    def log_hash(self, binhash, address=None):
        if not lt:
            return
        if is_ip_allowed(address[0]):
            return
        if self.n_downloading_lt < MAX_QUEUE_LT:
            self.queue.put([address, binhash, 'lt'])


def announce(info_hash, address):
    binhash = info_hash.decode('hex')
    master.log_announce(binhash, address)
    return 'ok'


def rpc_server():
    rpcserver = SimpleXMLRPCServer.SimpleXMLRPCServer(('localhost', 8004), logRequests=False)
    rpcserver.register_function(announce, 'announce')
    print 'Starting xml rpc server...'
    rpcserver.serve_forever()

if __name__ == "__main__":
    # max_node_qsize bigger, bandwith bigger, spped higher
    master = Master()
    master.start()

    rpcthread = threading.Thread(target=rpc_server)
    rpcthread.setDaemon(True)
    rpcthread.start()

    dht = DHTServer(master, "0.0.0.0", 6881, max_node_qsize=200)
    dht.start()
    dht.auto_send_find_node()


