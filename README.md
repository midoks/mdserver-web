<p align="center">
  <img alt="logo" src="https://cdn.jsdelivr.net/gh/midoks/mdserver-web@latest/route/static/logo.png" height="140" />
  <h3 align="center">mdserver-web</h3>
  <p align="center">一款简单Linux面板服务</p>
</p>

### 简介

简单的Linux面板,感谢BT.CN写出如此好的web管理软件。我一看到，就知道这是我一直想要的页面化管理方式。
复制了后台管理界面，按照自己想要的方式写了一版。


![CentOS](https://img.shields.io/badge/LINUX-CentOS-blue?style=for-the-badge&logo=CentOS)
![Ubuntu](https://img.shields.io/badge/LINUX-Ubuntu-blue?style=for-the-badge&logo=Ubuntu)
![Debian](https://img.shields.io/badge/LINUX-Debian-blue?style=for-the-badge&logo=Debian)
![Fedora](https://img.shields.io/badge/LINUX-Fedora-blue?style=for-the-badge&logo=Fedora)

[![Wiki](https://img.shields.io/badge/MW-Wiki-red?style=for-the-badge&logo=wiki)](https://github.com/midoks/mdserver-web/wiki)
[![](https://data.jsdelivr.com/v1/package/gh/midoks/mdserver-web/badge?style=for-the-badge)](https://www.jsdelivr.com/package/gh/midoks/mdserver-web)

* SSH终端工具
* 面板收藏功能
* 网站子目录绑定
* 网站备份功能
* 插件方式管理

基本上可以使用,后续会继续优化!欢迎提供意见！

- 吹水组 - https://t.me/mdserver_web
- [兼容性测试报告](/compatibility.md)
- [常用命令说明](/cmd.md)

### 主要插件介绍

* OpenResty - 轻量级，占有内存少，并发能力强。
* PHP[52-81] - PHP是世界上最好的编程语言。
* MySQL - 一种关系数据库管理系统。
* MariaDB - 是MySQL的一个重要分支。
* MongoDB - 一种非关系NOSQL数据库管理系统。
* phpMyAdmin - 著名Web端MySQL管理工具。
* Memcached - 一个高性能的分布式内存对象缓存系统。
* Redis - 一个高性能的KV数据库。
* PureFtpd - 一款专注于程序健壮和软件安全的免费FTP服务器软件。
* Gogs - 一款极易搭建的自助Git服务。
* Rsyncd - 通用同步服务。


### 插件开发相关

```
插件文档还不完善，如果有不明白的地方提Issue! 我会尽力完善。
如果你自己写了插件，想分享出来，也可以提Issue。
```

- 简单例子 - https://github.com/mw-plugin/simple-plugin 
- 插件地址 - https://github.com/mw-plugin
- 开发文档 - https://github.com/midoks/mdserver-web/wiki/插件开发


# Note

```
phpMyAdmin[4.4.15]支持MySQL[5.5-5.7]
phpMyAdmin[5.2.0]支持MySQL[8.0]

PHP[53-72]支持phpMyAdmin[4.4.15]
PHP[72-81]支持phpMyAdmin[5.2.0]


```

# 特别赞助

- [找资源 - 阿里云盘资源搜索引擎](https://zhaoziyuan.la/)

# AD - VPS推荐 - 🙏

- [ZZZ评测](https://www.zzzvps.com/)

| 服务商			| 	LOGO   |  推广地址  | 优惠码 |
| ------------- |----------|-----------|-------|
| digitalvirt	|[![digitalvirt](https://digitalvirt.com/templates/BlueWhite/img/logo-dark.svg)](https://digitalvirt.com/aff.php?aff=154) | https://digitalvirt.com/aff.php?aff=154 | 9SYDY7UH0U |
| 搬瓦工	|[![搬瓦工](https://bwh81.net/templates/organicbandwagon/images/logo.png)](https://bwh81.net/aff.php?aff=54161) | https://bwh81.net/aff.php?aff=54161 | BWH3HYATVBJW |

# Docker

- 由[DDSRem](https://github.com/DDSRem)开发维护。
- https://hub.docker.com/r/ddsderek/mw-server

```
docker run -itd --name mw-server --privileged=true -p 7200:7200 -p 80:80 -p 443:443 -p 888:888 ddsderek/mw-server:latest
```


### 版本更新 0.10.2

* 修复上次更新的UI问题。
* `FTP存储空间` 备份数据库修复。
* 修复计划任务执行Python脚本的编码问题。
* 添加，修改计划任务参数强校验。

### JSDelivr安装地址

- 初始安装

```
curl -fsSL https://cdn.jsdelivr.net/gh/midoks/mdserver-web@latest/scripts/install.sh | bash
```

- 直接更新

```
curl -fsSL https://cdn.jsdelivr.net/gh/midoks/mdserver-web@latest/scripts/update.sh | bash
```

- 卸载脚本

```
curl -fsSL https://cdn.jsdelivr.net/gh/midoks/mdserver-web@latest/scripts/uninstall.sh | bash
```

### 备用地址

- 初始安装

```
curl -fsSL  https://raw.githubusercontent.com/midoks/mdserver-web/master/scripts/install.sh | bash

```

- 直接更新

```
curl -fsSL  https://raw.githubusercontent.com/midoks/mdserver-web/master/scripts/update.sh | bash
```

- 卸载脚本

```
curl -fsSL https://raw.githubusercontent.com/midoks/mdserver-web/master/scripts/uninstall.sh | bash
```


### 通用软件安装[命令行安装]

- 需已经安装mdserver-web

```
curl -fsSL  https://raw.githubusercontent.com/midoks/mdserver-web/dev/scripts/quick/app.sh | bash
```


### DEV使用

```
curl -fsSL  https://raw.githubusercontent.com/midoks/mdserver-web/dev/scripts/install_dev.sh | bash
curl -fsSL  https://raw.githubusercontent.com/midoks/mdserver-web/dev/scripts/update_dev.sh | bash


curl -fsSL https://gitee.com/midoks/mdserver-web/raw/master/scripts/install_dev.sh | bash
curl -fsSL https://gitee.com/midoks/mdserver-web/raw/master/scripts/update_dev.sh | bash
```

### 捐赠地址 USDT（TRC20）

TVbNgrpeGBGZVm5gTLa21ADP7RpnPFhjya


### 微信赞助

[![截图](https://cdn.jsdelivr.net/gh/midoks/mdserver-web@latest/route/static/img/weixin_zz.jpg)](https://cdn.jsdelivr.net/gh/midoks/mdserver-web@latest/route/static/img/weixin_zz.jpg)


### 无图不真相

[![截图](https://cdn.jsdelivr.net/gh/midoks/mdserver-web@latest/route/static/mdw.jpg)](https://cdn.jsdelivr.net/gh/midoks/mdserver-web@latest/route/static/mdw.jpg)


### Stargazers over time

[![Stargazers over time](https://starchart.cc/midoks/mdserver-web.svg)](https://starchart.cc/midoks/mdserver-web)


### 感谢开发赞助

[![digitalvirt](https://digitalvirt.com/templates/BlueWhite/img/logo-dark.svg)](https://digitalvirt.com/aff.php?aff=154)

### 授权许可

本项目采用 Apache 开源授权许可证，完整的授权说明已放置在 [LICENSE](https://github.com/midoks/mdserver-web/blob/master/LICENSE) 文件中。

