#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl
SYS_ARCH=`arch`

# 关于macosx使用dtrace

# https://groups.google.com/g/openresty/c/MswlH_8DDHA
# http://dtrace.org/blogs/brendan/2012/11/14/dtracing-in-anger/

# sudo dtrace -x ustackframes=100 -n 'pid$target::mach_msg_trap:entry { @[ustack()] = count(); } tick-30s { exit(0); }' -p 2915 -o out.SystemUIServer_stacks

