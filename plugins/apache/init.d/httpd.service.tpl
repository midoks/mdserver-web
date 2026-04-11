[Unit]
Description=Apache Web Server
After=network.target

[Service]
Type=forking 
PIDFile={$SERVER_PATH}/apache/httpd/logs/httpd.pid
ExecStart={$SERVER_PATH}/apache/httpd/bin/apachectl start
ExecReload={$SERVER_PATH}/apache/httpd/bin/apachectl graceful
ExecStop={$SERVER_PATH}/apache/httpd/bin/apachectl stop
PrivateTmp=true
User=apache
Group=apache
Restart=on-failure

[Install]
WantedBy=multi-user.target