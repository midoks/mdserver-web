# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------


import json

from admin.model import db, Option
import core.mw as mw

def getOption(name, type='common') -> str:
    data = Option.query.filter_by(name=name, type=type).first()
    if data is not None:
        return data.value
    return ''

def getOptionByJson(name, type='common') -> object:
    data = Option.query.filter_by(name=name, type=type).first()
    if data is not None:
        return json.loads(data.value)
    return []

def setOption(name, value, type='common') -> bool:
    data = Option.query.filter_by(name=name, type=type).first()
    if data is None:
        add_option = Option(
            name=name, 
            type=type,
            value=value)
        db.session.add(add_option)
        db.session.commit()
        db.session.close()
        return True
    
    db.session.query(Option).filter_by(name=name, type=type).update({"value":value})
    db.session.commit()
    db.session.close()
    return True