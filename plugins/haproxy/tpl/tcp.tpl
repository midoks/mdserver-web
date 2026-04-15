global
	daemon
	pidfile        		/tmp/haproxy.pid
	maxconn        		4000
	user           		haproxy
	group          		haproxy


defaults
	mode				tcp
	log					local local0
	option				tcplog
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


frontend tcp_frontend
    bind *:8090
    mode tcp
    default_backend tcp_backend

backend tcp_backend
    mode tcp
    server tcp1 192.168.1.100:8090 check


