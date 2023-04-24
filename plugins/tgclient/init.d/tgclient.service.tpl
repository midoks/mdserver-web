[Unit]
Description=Tgbot Service
After=network.target

[Service]
Type=forking
ExecStart={$APP_PATH}/init.d/tgclient start
ExecStop={$APP_PATH}/init.d/tgclient stop
ExecReload={$APP_PATH}/init.d/tgclient reload
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target