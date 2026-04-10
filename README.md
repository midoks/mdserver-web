<center><img width="100" height="100" alt="image" src="https://github.com/AndyXeCM/PowerLinux/blob/master/web/static/logo.png" />

# PowerLinux v2.0

#### 轻量易用的下一代Linux控制面板
<p></p>
<img width="2788" height="3022" alt="image" src="https://github.com/user-attachments/assets/495759ae-3987-408f-ab23-f33a75defca5" />

<p></p>
欢迎各位积极完善，提交pull request!
<p></p>
基于[MWPanel](https://github.com/midoks/mdserver-web/) 构建，没有原作者的构建就没有这个面板，非常感谢！！！


***

主要设计语言：MDUI2，简洁美观，功能够用。
<p></p>

功能请参照宝塔面板v9，宝塔面板有的功能这个面板基本上都有，只不过软件商店里面的软件少了一些，欢迎各位为这个面板的生态作出贡献～～～

***

- **一键安装**

```
bash <(curl --insecure -fsSL https://cdn.jsdelivr.net/gh/AndyXeCM/PowerLinux@master/scripts/install.sh)

```
***
- **更新**

```
bash <(curl --insecure -fsSL https://cdn.jsdelivr.net/gh/AndyXeCM/PowerLinux@master/scripts/update.sh)
```

- **卸载**

```
wget --no-check-certificate -O uninstall.sh https://cdn.jsdelivr.net/gh/AndyXeCM/PowerLinux@master/scripts/uninstall.sh && bash uninstall.sh
```

以下是原作者readme中的补充信息：

- 吹水组 - https://t.me/mdserver_web
- 交流论坛 - https://bbs.midoks.icu

```
如果出现问题，最好私给我面板信息。不要让我猜。如果不提供，不要提出问题，自行解决。  — 座右铭
Talk is cheap, show me the code.  -- linus
```

- [兼容性测试报告](/compatibility.md)
- [常用命令说明](/cmd.md) [ mw default ] [ mw dev ]

### 主要插件介绍

* OpenResty - 轻量级，占有内存少，并发能力强。
* PHP[53-85] - PHP是世界上最好的编程语言。
* MySQL - 一种关系数据库管理系统。
* MariaDB - 是MySQL的一个重要分支。
* MySQL[community] - 一种关系数据库管理系统。
* MongoDB - 一种非关系NOSQL数据库管理系统。
* PostgreSQL - 功能强大的开源数据库。
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

## 其他插件

- OP鉴权 - https://github.com/mw-plugin/op_auth


# Note

```
phpMyAdmin[4.4.15]支持MySQL[5.5-5.7]
phpMyAdmin[5.2.1]支持MySQL[8.0+]

PHP[53-72]支持phpMyAdmin[4.4.15]
PHP[72-84]支持phpMyAdmin[5.2.1]
```

# 郑重声明

不卖、不会监控(统计使用除外)、更不会注入病毒,大家使用方便(望大家不吝捐赠)。

- https://www.youtube.com/watch?v=2taa5K-Jmmw



### 授权许可

本项目采用 Apache 开源授权许可证，完整的授权说明已放置在 [LICENSE](https://github.com/midoks/mdserver-web/blob/master/LICENSE) 文件中。


