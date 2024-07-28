[Unit]
Description=Fail2Ban Service
Documentation=man:fail2ban(1)
After=network.target iptables.service firewalld.service ip6tables.service ipset.service nftables.service
PartOf=firewalld.service

[Service]
Type=simple
Environment="PYTHONNOUSERSITE=1"
ExecStartPre=/bin/mkdir -p /run/fail2ban
ExecStart=/usr/bin/fail2ban-server -xf start
# if should be logged in systemd journal, use following line or set logtarget to sysout in fail2ban.local
# ExecStart=/usr/bin/fail2ban-server -xf --logtarget=sysout start
ExecStop=/usr/bin/fail2ban-client stop
ExecReload=/usr/bin/fail2ban-client reload
PIDFile=/run/fail2ban/fail2ban.pid
Restart=on-failure
RestartPreventExitStatus=0 255
Environment="PYTHONNOUSERSITE=yes"

[Install]
WantedBy=multi-user.target
