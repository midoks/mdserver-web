### mdserver-web 0.8.6
简单的Linux面板,感谢BT.CN写出如此好的web管理软件。我一看到，就知道这是我一直想要的页面化管理方式。
复制了后台管理界面，按照自己想要的方式写了一版。

```
为了兼容CentOS,Ubuntu,Debian,Fedora, 由chkconfig改systemd管理。原来都要重新安装。还在进行修改..

chkconfig 支持 Fedora,CentOS
update-rc.d 支持 Ubuntu,Debian | 功能不够
systemd 支持 CentOS,Ubuntu,Debian,Fedora...

```

![CentOS](https://img.shields.io/badge/LINUX-CentOS-blue?style=for-the-badge&logo=CentOS)
![Ubuntu](https://img.shields.io/badge/LINUX-Ubuntu-blue?style=for-the-badge&logo=Ubuntu)
![Debian](https://img.shields.io/badge/LINUX-Debian-blue?style=for-the-badge&logo=Debian)
![Fedora](https://img.shields.io/badge/LINUX-Fedora-blue?style=for-the-badge&logo=Fedora)

[![Wiki](https://img.shields.io/badge/MW-Wiki-red?style=for-the-badge&logo=wiki)](https://github.com/midoks/mdserver-web/wiki)

* SSH工具
* 面板收藏功能
* 网站子目录绑定
* 网站备份功能
* 自动更新优化
* 插件方式管理

基本上可以使用,后续会继续优化!欢迎提供意见！


### 主要插件介绍
* OpenResty - 轻量级，占有内存少，并发能力强。
* PHP[52-81] - PHP是世界上最好的编程语言。
* MySQL - 一种关系数据库管理系统。
* MongoDB - 一种非关系NOSQL数据库管理系统。
* phpMyAdmin - 著名Web端MySQL管理工具。
* Memcached - 一个高性能的分布式内存对象缓存系统。
* Redis - 一个高性能的KV数据库。
* CSVN - 最流行的SVN代码共享管理软件。
* PureFtpd - 一款专注于程序健壮和软件安全的免费FTP服务器软件。
* Gogs - 一款极易搭建的自助Git服务。
* Rsyncd - 通用同步服务。


### 版本更新 0.8.6
* mysql主从配置。
* swap插件[虚拟内存]。


### 问题
- Ubuntu 20 无法安装mysql5.7 && mysql 80.
- Ftp debian无法安装成功。
- php52,在debian无法安装成功。


### GW使用

- 自动安装

```
curl -fsSL  https://raw.githubusercontent.com/midoks/mdserver-web/master/scripts/install.sh | bash
```

- 脚本更新

```
curl -fsSL  https://raw.githubusercontent.com/midoks/mdserver-web/master/scripts/update.sh | bash
```

### GN使用

- 自动安装

```
curl -fsSL  https://gitee.com/midoks/mdserver-web/raw/master/scripts/install_cn.sh | bash
```

- 脚本更新

```
curl -fsSL  https://gitee.com/midoks/mdserver-web/raw/master/scripts/update_cn.sh | bash
```


### DEV使用

- 自动安装

```
curl -fsSL  https://raw.githubusercontent.com/midoks/mdserver-web/dev/scripts/install_dev.sh | bash
```

- 脚本更新

```
curl -fsSL  https://raw.githubusercontent.com/midoks/mdserver-web/dev/scripts/update_dev.sh | bash
```


### 无图不真相

[![截图](/route/static/mdw.jpg)](/route/static/mdw.jpg)


### 插件开发相关

```
插件文档还不完善，如果有不明白的地方提Issue! 我会尽力完善。
如果你自己写了插件，想分享出来，也可以提Issue。
```

- 开发文档 - https://github.com/midoks/mdserver-web/wiki/%E6%8F%92%E4%BB%B6%E5%BC%80%E5%8F%91
- 插件地址 - https://github.com/mw-plugin
- 例子 - https://github.com/mw-plugin/simple-plugin 



### Stargazers over time

[![Stargazers over time](https://starchart.cc/midoks/mdserver-web.svg)](https://starchart.cc/midoks/mdserver-web)


### 感谢

- 开发赞助

[digitalvirt](https://digitalvirt.com/)

### 授权许可

本项目采用 Apache 开源授权许可证，完整的授权说明已放置在 [LICENSE](https://github.com/midoks/mdserver-web/blob/master/LICENSE) 文件中。

