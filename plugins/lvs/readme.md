debian 

# 查看网卡
ls /sys/class/net/

ifconfig ens256 172.16.204.100 netmask 255.255.255.255 broadcast 192.168.212.100 up

route add -host 172.16.204.100 dev ens256

ipvsadm -A -t 172.16.204.100:80 -s rr
ipvsadm -a -t 172.16.204.100:80 -r 172.16.204.129:80 -m

跨机房
ipvsadm -A -t 154.21.1.1:8016 -s wlc
ipvsadm -a -t 154.21.1.1:8016 -r 103.39.78.2 -i
源
ifconfig tunl0 154.21.1.1 netmask 255.255.255.255 up

# 清空LVS规则

ipvsadm -C

# 查看LVS

ipvsadm -L -n