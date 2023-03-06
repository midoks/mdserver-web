[Unit]
Description=Tgbot Service
After=network.target

[Service]
Type=forking
ExecStart={$APP_PATH}/init.d/tgbot start
ExecStop={$APP_PATH}/init.d/tgbot stop
ExecReload={$APP_PATH}/init.d/tgbot reload
ExecRestart={$APP_PATH}/init.d/tgbot restart
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target