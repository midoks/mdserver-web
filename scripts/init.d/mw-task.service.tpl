[Unit]
Description=mw-task daemon
After=network.target

[Service]
Type=simple
WorkingDirectory={$SERVER_PATH}
EnvironmentFile={$SERVER_PATH}/scripts/init.d/service.sh
ExecStart=python3 task.py
ExecStop=kill -HUP $MAINID
ExecReload=kill -HUP $MAINID
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target