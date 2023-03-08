[Unit]
Description=Tgbot Service
After=network.target

[Service]
Type=forking
ExecStart={$APP_PATH}/init.d/tgbot start
ExecStop={$APP_PATH}/init.d/tgbot stop
ExecReload={$APP_PATH}/init.d/tgbot reload
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target