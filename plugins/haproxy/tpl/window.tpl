global
	daemon
	pidfile        		/tmp/haproxy.pid
	maxconn        		4000
	user           		haproxy
	group          		haproxy


defaults
	mode				http
	log					global
	option				httplog
	timeout	connect		10s
	timeout client		15s
	timeout	server		15s


listen stats
	mode http
	bind *:10800
	stats enable
	stats refresh 10
	stats uri /haproxy
	stats realm Haproxy\ Statistics
	stats auth {$HA_USER}:{$HA_PWD}


frontend rdp_frontend
    bind *:3389
    mode tcp
    option tcplog
    default_backend rdp_backend

backend rdp_backend
    mode tcp
    server rdp1 192.168.1.100:3389 check


