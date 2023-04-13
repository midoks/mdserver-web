[Unit]
Description=tamper_proof_py server daemon
After=network.target

[Service]
Type=forking
ExecStart={$SERVER_PATH}/init.d/tamper_proof_py start
ExecStop={$SERVER_PATH}/init.d/tamper_proof_py stop
ExecReload={$SERVER_PATH}/init.d/tamper_proof_py reload
ExecRestart={$SERVER_PATH}/init.d/tamper_proof_py restart
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target