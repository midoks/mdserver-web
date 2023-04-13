[Unit]
Description=system_safe server daemon
After=network.target

[Service]
Type=forking
ExecStart={$SERVER_PATH}/init.d/system_safe start
ExecStop={$SERVER_PATH}/init.d/system_safe stop
ExecReload={$SERVER_PATH}/init.d/system_safe reload
ExecRestart={$SERVER_PATH}/init.d/system_safe restart
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target