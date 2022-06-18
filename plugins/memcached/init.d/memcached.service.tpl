[Unit]
Description=Free & open source, high-performance, distributed memory object caching system.
After=network.target

[Service]
Type=forking
EnvironmentFile=-{$SERVER_PATH}/memcached/memcached.env
ExecStart={$SERVER_PATH}/memcached/bin/memcached -d -l $IP -p $PORT -u $USER -m $CACHESIZE -c $MAXCONN -P $OPTIONS
ExecReload=/bin/kill -USR2 $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target