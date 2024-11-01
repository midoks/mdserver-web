# It's not recommended to modify this file in-place, because it
# will be overwritten during upgrades.  If you want to customize,
# the best way is to use the "systemctl edit" command.
# systemctl daemon-reload

[Unit]
Description=pgadmin service
After=network.target

[Service]

ExecStart={$SERVER_PATH}/pgadmin/run/bin/gunicorn --bind unix:/tmp/pgadmin4.sock --workers=1 --threads=25 --chdir {$SERVER_PATH}/pgadmin/run/lib/{$PY_VER}/site-packages/pgadmin4 pgAdmin4:app
ExecReload=/bin/kill -USR2 $MAINPID
PrivateTmp=false

[Install]
WantedBy=multi-user.target
