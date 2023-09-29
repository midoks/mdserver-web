[Unit]
Description=Mosquitto MQTT Broker
After=network.target

[Service]
Type=forking
ExecStart={$SERVER_PATH}/mosquitto/sbin/mosquitto -c {$SERVER_PATH}/mosquitto/etc/mosquitto/mosquitto.conf
ExecReload=/bin/kill -USR2 $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target