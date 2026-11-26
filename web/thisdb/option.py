# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------

import os
import json
import time
import core.mw as mw

# 进程内配置缓存: {key: (raw_value, expire_ts)}
# raw_value 存 DB 原始字符串, getOptionByJson 取时现 json.loads
_OPTION_CACHE = {}
_OPTION_CACHE_TTL = 5  # 5 秒, 配置修改后 5 秒内生效


def _cache_key(name, type):
    return '%s:%s' % (type, name)


def _get_cached(name, type):
    """返回 (raw_value, hit). raw_value 为 None 表示 DB 里没这条配置."""
    key = _cache_key(name, type)
    if key in _OPTION_CACHE:
        value, expire = _OPTION_CACHE[key]
        if time.time() < expire:
            return value, True
        del _OPTION_CACHE[key]
    return None, False


def _set_cached(name, type, raw_value):
    key = _cache_key(name, type)
    _OPTION_CACHE[key] = (raw_value, time.time() + _OPTION_CACHE_TTL)


def _invalidate(name=None, type='common'):
    """清缓存. name=None 时全清."""
    if name is None:
        _OPTION_CACHE.clear()
    else:
        _OPTION_CACHE.pop(_cache_key(name, type), None)


def getOption(name, type='common', default=None) -> str:
    '''
    获取配置的值
    :name -> str 名称 (必填)
    :type -> str 类型 (可选|默认common)
    :default -> str 默认值 (可选)
    '''
    cached, hit = _get_cached(name, type)
    if hit:
        return default if cached is None else cached

    data = mw.M('option').field('name').where('name=? and type=?', (name, type,)).getField('value')
    _set_cached(name, type, data)
    if data is None:
        return default
    return data


def getOptionByJson(name, type='common', default=None) -> object:
    '''
    获取配置的值,返回对象类型
    :name -> str 名称 (必填)
    :type -> str 类型 (可选|默认common)
    :default -> str 默认值 (可选)
    '''
    cached, hit = _get_cached(name, type)
    if hit:
        if cached is None:
            return default
        try:
            return json.loads(cached)
        except Exception:
            return default

    data = mw.M('option').field('name').where('name=? and type=?', (name, type,)).getField('value')
    _set_cached(name, type, data)
    if data is None:
        return default
    try:
        return json.loads(data)
    except Exception:
        return default


def setOption(name, value, type='common') -> bool:
    '''
    设置配置的值
    :name -> str 名称 (必填)
    :value -> object值 (必填)
    :type -> str 类型 (可选|默认common)
    '''
    # 先清缓存, 再写 DB, 保证下一次读取拿到新值
    _invalidate(name, type)

    data = mw.M('option').field('name,type,value').where('name=? and type=?', (name, type,)).find()
    if data is not None:
        mw.M('option').field('name').where('name=? and type=?', (name, type,)).setField('value', value)
        return True
    add_option = {
        'name': name,
        'type': type,
        'value': value
    }
    return mw.M('option').insert(add_option)
