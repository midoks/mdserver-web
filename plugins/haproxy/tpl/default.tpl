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

frontend http-in
	bind *:1080
	default_backend		servers
	option				forwardfor
	option 				http-keep-alive

backend servers
	balance roundrobin
	server web1 0.0.0.0:9090 check inter 2000 rise 2 fall 5


