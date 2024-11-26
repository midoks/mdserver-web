# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import core.mw as mw

__FIELD = 'id,port,protocol,ps,add_time,update_time'

def getFirewallList(page=1,size=10):
    start = (int(page) - 1) * (int(size))
    limit = str(start) + ',' +str(size)

    firewall_list = mw.M('firewall').field(__FIELD).limit(limit).order('id desc').select()
    count = mw.M('firewall').count()

    data = {}
    data['count'] = count
    data['list'] = firewall_list
    return data

def addFirewall(port, protocol='tcp',ps='备注') -> bool:
    '''
    设置配置的值
    :port -> str 端口 (必填)
    :protocol -> str 协议 (可选|tcp,udp,tcp/udp)
    :ps -> str 备注 (可选)
    '''
    now_time = mw.formatDate()
    insert_data = {
        'port':port,
        'protocol':protocol,
        'ps':ps,
        'add_time':now_time,
        'update_time':now_time,
    }
    mw.M('firewall').insert(insert_data)
    return True


def getFirewallCountByPort(port):
    return mw.M('firewall').where('port=?',(port,)).count()


