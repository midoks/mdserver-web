# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

from admin.model import db, Firewall

import core.mw as mw



def addFirewall(port,
    protocol: str | None = 'tcp',
    ps: str | None = '备注'
) -> bool:
    '''
    设置配置的值
    :port -> str 端口 (必填)
    :protocol -> str 协议 (可选|tcp,udp,tcp/udp)
    :ps -> str 备注 (可选)
    '''
    now_time = mw.formatDate()
    add_data = Firewall(
        port=port, 
        protocol=protocol,
        add_time=now_time,
        update_time=now_time)
    db.session.add(add_data)
    db.session.commit()
    return True


def getFirewallCountByPort(port):
    return Firewall.query.filter(Tasks.port==port).count()


