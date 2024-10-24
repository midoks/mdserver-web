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
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True, comment="ID")
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.String(256), nullable=False)

class Option(db.Model):
    """定义类型"""
    __tablename__ = 'option'
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True, comment="ID")
    name = db.Column(db.String(128), unique=True, nullable=False, comment="配置名称")
    value = db.Column(db.TEXT, unique=False, nullable=False, comment="内容")

class User(db.Model):
    """定义登录用户"""
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True, comment="ID")
    name = db.Column(db.String(128), unique=True, nullable=False, comment="用户名")
    password = db.Column(db.String(128), unique=False, nullable=False, comment="密码")
    login_ip = db.Column(db.String(128), unique=False, nullable=True, comment="登录IP")
    login_time = db.Column(db.String(128), unique=False, nullable=True, comment="登录时间")
    phone = db.Column(db.String(20), unique=False, nullable=False,comment="手机")
    email = db.Column(db.String(320), nullable=False, comment="邮件")

class Crontab(db.Model):
    """定义计划任务"""
    __tablename__ = 'crontab'
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True, comment="ID")
    name = db.Column(db.TEXT, unique=True, nullable=False, comment="任务名称")
    type = db.Column(db.String(128), unique=False, nullable=False, comment="计划类型")
    where1 = db.Column(db.TEXT, unique=False, nullable=True, comment="执行条件")
    where_hour = db.Column(db.TEXT, unique=False, nullable=True, comment="执行条件/小时")
    where_minute = db.Column(db.TEXT, unique=False, nullable=True, comment="执行条件/分钟")
    echo = db.Column(db.TEXT, unique=False, nullable=True, comment="脚本保存名称")
    sname = db.Column(db.TEXT, unique=False, nullable=True, default='',comment="名称")
    sbody = db.Column(db.TEXT, unique=False, nullable=True, default='',comment="脚本")
    stype = db.Column(db.TEXT, unique=False, nullable=True, default='',comment="脚本类型")
    url_address = db.Column(db.TEXT, unique=False, nullable=True, default='',comment="URL访问地址")
    backup_to = db.Column(db.TEXT, unique=False, nullable=True, comment="备份地址")
    save = db.Column(db.Integer, unique=False, nullable=True, default=3,comment="备份数量")
    status = db.Column(db.Integer, unique=False, nullable=True, default=1, comment="状态")
    add_time = db.Column(db.TEXT, nullable=False, comment="添加时间")
    update_time = db.Column(db.TEXT, nullable=False, comment="添加时间")

class Logs(db.Model):
    """定义日志"""
    __tablename__ = 'logs'
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True, comment="ID")
    uid = db.Column(db.Integer(), unique=True, nullable=False, comment="用户ID")
    type = db.Column(db.String(128), unique=False, nullable=False, comment="日志类型")
    log = db.Column(db.TEXT, unique=False, nullable=True, comment="日志内容")
    add_time = db.Column(db.TEXT, nullable=False, comment="添加时间")

class Firewall(db.Model):
    """定义防火墙"""
    __tablename__ = 'firewall'
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True, comment="ID")
    port = db.Column(db.Integer(), unique=True, nullable=False, comment="端口")
    protocol = db.Column(db.Integer(), unique=True, nullable=False, comment="协议/tcp/udp")
    ps = db.Column(db.TEXT, unique=False, nullable=False, comment="备注")
    add_time = db.Column(db.TEXT, nullable=False, comment="添加时间")
    update_time = db.Column(db.TEXT, nullable=False, comment="更新时间")


class Backup(db.Model):
    """定义备份"""
    __tablename__ = 'backup'
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True, comment="ID")
    pid = db.Column(db.Integer(), unique=False, nullable=False, comment="父级ID")
    type = db.Column(db.String(128), unique=False, nullable=False, comment="备份类型")
    name = db.Column(db.TEXT, unique=False, nullable=False, comment="名称")
    filename = db.Column(db.TEXT, unique=False, nullable=False, comment="文件绝对位置")
    size = db.Column(db.Integer(), unique=False, nullable=False, comment="大小")
    add_time = db.Column(db.TEXT, nullable=False, comment="添加时间")






