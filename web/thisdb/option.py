# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------


import core.mw as mw

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
    data = mw.M('option').field('name').where('name=? and type=?',(name, type,)).getField('value')

    if len(data) == 0:
        return default
    return data