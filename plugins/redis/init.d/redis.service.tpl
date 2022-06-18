[Unit]
Description=Redis In-Memory Data Store
After=network.target

[Service]
ExecStart={$SERVER_PATH}/redis/bin/redis-server {$SERVER_PATH}/redis/redis.conf
ExecStop={$SERVER_PATH}/redis/redis-cli shutdown
Restart=always

[Install]
WantedBy=multi-user.target