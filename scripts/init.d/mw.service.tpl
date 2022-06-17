[Unit]
Description=mw server daemon
After=network.target

[Service]
Type=forking
ExecStart=cd {$SERVER_PATH} &&  gunicorn -c setting.py app:app
ExecStop=kill -HUP $MAINID
ExecReload=kill -HUP $MAINID
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target