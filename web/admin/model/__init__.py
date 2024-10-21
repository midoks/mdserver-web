# coding:utf-8

# ---------------------------------------------------------------------------------
# MW-Linux面板
# ---------------------------------------------------------------------------------
# copyright (c) 2018-∞(https://github.com/midoks/mdserver-web) All rights reserved.
# ---------------------------------------------------------------------------------
# Author: midoks <midoks@163.com>
# ---------------------------------------------------------------------------------


from flask_sqlalchemy import SQLAlchemy
# from flask_security import UserMixin, RoleMixin
import setting

SCHEMA_VERSION = 1


db = SQLAlchemy(
        engine_options={
            'pool_size': setting.CONFIG_DATABASE_CONNECTION_POOL_SIZE,
            'max_overflow': setting.CONFIG_DATABASE_CONNECTION_MAX_OVERFLOW
        }
    )


class Version(db.Model):
    """用于参考/升级的版本号"""
    __tablename__ = 'version'
    name = db.Column(db.String(32), primary_key=True)
    value = db.Column(db.Integer(), nullable=False)

class Role(db.Model):
    """定义安全角色"""
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.String(256), nullable=False)