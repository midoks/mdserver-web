[Unit]
Description=mw-panel daemon
After=network.target

[Service]
Type=simple
WorkingDirectory={$SERVER_PATH}
EnvironmentFile={$SERVER_PATH}/scripts/init.d/service.sh
ExecStart=gunicorn -c setting.py app:app
ExecStop=kill -HUP $MAINID
ExecReload=kill -HUP $MAINID
KillMode=process
Restart=on-failure

[Timer]
# 每日凌晨点重启
OnCalendar=*-*-* 03:30:00
Unit=mw.service

[Install]
WantedBy=multi-user.target