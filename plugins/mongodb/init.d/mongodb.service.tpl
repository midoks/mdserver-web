[Unit]
Description=MongoDB Database Server
Documentation=https://docs.mongodb.org/manual
After=network-online.target
Wants=network-online.target

[Service]
User=root
Group=root
#EnvironmentFile=-/etc/default/mongod
Environment="MONGODB_CONFIG_OVERRIDE_NOFORK=1"
Environment="LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib64:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin:/www/server/lib/openssl11/lib"
PIDFile={$SERVER_PATH}/mongodb/mongodb.pid
ExecStart={$SERVER_PATH}/mongodb/bin/mongod -f {$SERVER_PATH}/mongodb/mongodb.conf
ExecReload=/bin/kill -HUP $MAINPID
#RuntimeDirectory=mongodb
# file size
LimitFSIZE=infinity
# cpu time
LimitCPU=infinity
# virtual memory size
LimitAS=infinity
# open files
LimitNOFILE=64000
# processes/threads
LimitNPROC=64000
# locked memory
LimitMEMLOCK=infinity
# total threads (user+kernel)
TasksMax=infinity
TasksAccounting=false

# Recommended limits for mongod as specified in
# https://docs.mongodb.com/manual/reference/ulimit/#recommended-ulimit-settings

[Install]
WantedBy=multi-user.target