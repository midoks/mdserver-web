# 火焰图安装 [ubuntu 20.04]
```

sudo apt-get install -y linux-tools-common linux-tools-generic linux-tools-`uname -r`
apt-get update -y
sudo apt -y install elfutils
apt-get install -y systemtap gcc
sudo apt-get install -y linux-headers-generic gcc libcap-dev
apt install -y kernel-debuginfo-common kernel-debuginfo
```

# 测试有效性
```
stap -ve 'probe begin { log("hello systemtap!") exit() }'


stap -e 'probe kernel.function("sys_open") {log("hello world") exit()}'


stap -v -e 'probe vfs.read {printf("read performed\n"); exit()}'
```


# openresty 测试
```

cd /www/server/mdserver-web/plugins/op_waf/t && sh ngx_debug.sh lua t1
cd /www/server/mdserver-web/plugins/op_waf/t && sh ngx_debug.sh c t2
```
