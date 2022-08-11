[Unit]
Description=PostgreSQL: a powerful open source database
After=network.target

[Service]
Type=forking
User=postgres    
Group=postgres
WorkingDirectory={$APP_PATH}
ExecStart={$APP_PATH}/bin/pg_ctl start -D {$APP_PATH}/data
ExecReload={$APP_PATH}/bin/pg_ctl restart -D {$APP_PATH}/data
ExecStop={$APP_PATH}/bin/pg_ctl stop -D {$APP_PATH}/data
PrivateTmp=false

[Install]
WantedBy=multi-user.target