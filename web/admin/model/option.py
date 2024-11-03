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

def getOption(name,
    type: str | None = 'common',
    default : str | None = None
) -> str:
    '''
    获取配置的值
    :name -> str 名称 (必填)
    :type -> str 类型 (可选|默认common)
    :default -> str 默认值 (可选)
    '''
    data = Option.query.filter_by(name=name, type=type).first()
    if data is not None:
        return data.value

    if default is not None:
        return default
    return ''

def getOptionByJson(name,
    type: str | None = 'common',
    default : object | None = None
) -> object:
    '''
    获取配置的值,返回对象类型
    :name -> str 名称 (必填)
    :type -> str 类型 (可选|默认common)
    :default -> str 默认值 (可选)
    '''
    data = Option.query.filter_by(name=name, type=type).first()
    if data is not None:
        return json.loads(data.value)

    if default is not None:
        return default
    return []

def setOption(name, value,
    type: str | None = 'common'
) -> bool:
    '''
    设置配置的值
    :name -> str 名称 (必填)
    :value -> object值 (必填)
    :type -> str 类型 (可选|默认common)
    '''
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
    return True