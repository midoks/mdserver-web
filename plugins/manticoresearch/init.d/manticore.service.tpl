[Unit]
Description=Manticore Search
After=network.target

[Service]
Type=simple
User=manticore
Group=manticore
ExecStart=/usr/local/bin/searchd -c /etc/manticoresearch/manticore.conf
ExecStop=/usr/local/bin/searchd -c /etc/manticoresearch/manticore.conf --stopwait
Restart=on-failure
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target