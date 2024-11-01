[Unit]
Description=A file list program that supports multiple storage
After=network.target

[Service]
Type=simple
WorkingDirectory={$SERVER_PATH}/cloudreve
ExecStart={$SERVER_PATH}/cloudreve/cloudreve
ExecReload=/bin/kill -USR2 $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target