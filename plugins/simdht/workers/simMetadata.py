#!/usr/bin/env python
# encoding: utf-8
import socket
import math
from struct import pack, unpack
from socket import inet_ntoa
from threading import Timer, Thread
from time import sleep, time
from hashlib import sha1

from simdht_worker import entropy
from bencode import bencode, bdecode


BT_PROTOCOL = "BitTorrent protocol"
BT_MSG_ID = 20
EXT_HANDSHAKE_ID = 0

def random_id():
    hash = sha1()
    hash.update(entropy(20))
    return hash.digest()

def send_packet(the_socket, msg):
    the_socket.send(msg)

def send_message(the_socket, msg):
    msg_len = pack(">I", len(msg))
    send_packet(the_socket, msg_len + msg)

def send_handshake(the_socket, infohash):
    bt_header = chr(len(BT_PROTOCOL)) + BT_PROTOCOL
    ext_bytes = "\x00\x00\x00\x00\x00\x10\x00\x00"
    peer_id = random_id()
    packet = bt_header + ext_bytes + infohash + peer_id

    send_packet(the_socket, packet)

def check_handshake(packet, self_infohash):
    try:
        bt_header_len, packet = ord(packet[:1]), packet[1:]
        if bt_header_len != len(BT_PROTOCOL):
            return False
    except TypeError:
        return False

    bt_header, packet = packet[:bt_header_len], packet[bt_header_len:]
    if bt_header != BT_PROTOCOL:
        return False

    packet = packet[8:]
    infohash = packet[:20]
    if infohash != self_infohash:
        return False

    return True

def send_ext_handshake(the_socket):
    msg = chr(BT_MSG_ID) + chr(EXT_HANDSHAKE_ID) + bencode({"m":{"ut_metadata": 1}})
    send_message(the_socket, msg)

def request_metadata(the_socket, ut_metadata, piece):
    """bep_0009"""
    msg = chr(BT_MSG_ID) + chr(ut_metadata) + bencode({"msg_type": 0, "piece": piece})
    send_message(the_socket, msg)

def get_ut_metadata(data):
    ut_metadata = "_metadata"
    index = data.index(ut_metadata)+len(ut_metadata) + 1
    return int(data[index])

def get_metadata_size(data):
    metadata_size = "metadata_size"
    start = data.index(metadata_size) + len(metadata_size) + 1
    data = data[start:]
    return int(data[:data.index("e")])

def recvall(the_socket, timeout=5):
    the_socket.setblocking(0)
    total_data = []
    data = ""
    begin = time()

    while True:
        sleep(0.05)
        if total_data and time()-begin > timeout:
            break
        elif time()-begin > timeout*2:
            break
        try:
            data = the_socket.recv(1024)
            if data:
                total_data.append(data)
                begin = time()
        except Exception:
            pass
    return "".join(total_data)

def download_metadata(address, infohash, metadata_queue, timeout=5):
    metadata = None
    start_time = time()
    try:
        the_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        the_socket.settimeout(timeout)
        the_socket.connect(address)

        # handshake
        send_handshake(the_socket, infohash)
        packet = the_socket.recv(4096)

        # handshake error
        if not check_handshake(packet, infohash):
            return

        # ext handshake
        send_ext_handshake(the_socket)
        packet = the_socket.recv(4096)

        # get ut_metadata and metadata_size
        ut_metadata, metadata_size = get_ut_metadata(packet), get_metadata_size(packet)
        #print 'ut_metadata_size: ', metadata_size

        # request each piece of metadata
        metadata = []
        for piece in range(int(math.ceil(metadata_size/(16.0*1024)))):
            request_metadata(the_socket, ut_metadata, piece)
            packet = recvall(the_socket, timeout) #the_socket.recv(1024*17) #
            metadata.append(packet[packet.index("ee")+2:])

        metadata = "".join(metadata)
        #print 'Fetched', bdecode(metadata)["name"], "size: ", len(metadata)

    except socket.timeout:
        pass
    except Exception, e:
        pass #print e

    finally:
        the_socket.close()
        metadata_queue.put((infohash, address, metadata, 'pt', start_time))

