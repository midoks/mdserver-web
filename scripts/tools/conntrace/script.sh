#!/bin/bash

# 测试中.

# /opt/iptables-switch.sh status | disable | enable
ipt_mod_conf="/etc/modprobe.d/iptables.conf"
ipt_mod_list="ip_vs iptable_nat nf_nat_ipv4 ipt_MASQUERADE nf_nat nf_conntrack_ipv4 nf_defrag_ipv4 xt_conntrack nf_conntrack iptable_filter ip_tables xt_tcpudp xt_multiport xt_length xt_addrtype x_tables"
nf_max=$(sysctl -e -n net.nf_conntrack_max)
nf_cur=$(sysctl -e -n net.netfilter.nf_conntrack_count)
ipt_hsize=$(grep 'MemTotal' /proc/meminfo | awk '{printf("%d",$2/16)}')

fuck_ipt_mod(){
	echo '# disable iptables conntrack modules' > ${ipt_mod_conf}
	for ipt_mod in ${ipt_mod_list}; do
		echo "blacklist ${ipt_mod}" >> ${ipt_mod_conf}
	    modprobe -r ${ipt_mod}
	done
}

clean_ipt_rule(){
	iptables -F
	iptables -Z
	iptables -X
	for ipt_table in $(cat /proc/net/ip_tables_names 2>/dev/null); do
	    iptables -t ${ipt_table} -F
	    iptables -t ${ipt_table} -Z
	    iptables -t ${ipt_table} -X
	done
	iptables -P INPUT ACCEPT
	iptables -P OUTPUT ACCEPT
	iptables -P FORWARD ACCEPT
}

ipt_enable(){
	echo "options nf_conntrack hashsize=${ipt_hsize}" > ${ipt_mod_conf} # /sys/module/nf_conntrack/parameters/hashsize
	for ipt_mod in ${ipt_mod_list}; do
		modprobe -q -r ${ipt_mod} && modprobe -a ${ipt_mod}
	done

	dmesg --reltime | grep nf_conntrack | tail -2 2>/dev/null
	sysctl -e -w net.nf_conntrack_max=4194304
	sysctl -e -w net.ipv4.netfilter.ip_conntrack_max=4194304
	sysctl -e -w net.netfilter.nf_conntrack_max=4194304
	sysctl -e -w net.netfilter.nf_conntrack_tcp_timeout_established=1200
	sysctl -e -w net.netfilter.nf_conntrack_tcp_timeout_close_wait=60
	sysctl -e -w net.netfilter.nf_conntrack_tcp_timeout_fin_wait=120
	sysctl -e -w net.netfilter.nf_conntrack_tcp_timeout_time_wait=120
}

case "$1" in
status)
    if [[ -z ${nf_max} ]]; then
        echo 'nf_conntrack disabled.'
    else
        echo "nf_conntrack used: ${nf_cur}/${nf_max}."
    fi
    ;;
disable)
    clean_ipt_rule
    fuck_ipt_mod
    $0 status
    ;;
enable)
    ipt_enable
    $0 status
;;
*)
    echo "Usage: $0 {status|disable|enable}"
    exit 2
    ;;
esac
exit 0