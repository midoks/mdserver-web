[Unit]
Description=mw server daemon
After=network.target

[Service]
Type=simple
WorkingDirectory={$SERVER_PATH}
ExecStart=gunicorn -c setting.py app:app
ExecStop=kill -HUP $MAINID
ExecReload=kill -HUP $MAINID
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target