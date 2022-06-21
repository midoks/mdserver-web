[Unit]
Description=mw-task server daemon
After=network.target

[Service]
Type=simple
WorkingDirectory={$SERVER_PATH}
ExecStart=python3 task.py
ExecStop=kill -HUP $MAINID
ExecReload=kill -HUP $MAINID
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target