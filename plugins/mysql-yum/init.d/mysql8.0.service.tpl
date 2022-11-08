# It's not recommended to modify this file in-place, because it will be
# overwritten during package upgrades.  If you want to customize, the
# best way is to use systemctl edit:
#
# $ systemctl edit mysqld.service
#
# this will create file
#
#  /etc/systemd/system/mysqld.service.d/override.conf
#
# which be parsed after the file mysqld.service itself is parsed.
#
# For example, if you want to increase mysql's open-files-limit to 20000
# add following when editing with command above:
#
#	[Service]
#	LimitNOFILE=20000
#
# Or if you require to execute pre and post scripts in the unit file as root, set
#       PermissionsStartOnly=true
#
# For more info about custom unit files, see systemd.unit(5) or
# http://fedoraproject.org/wiki/Systemd#How_do_I_customize_a_unit_file.2F_add_a_custom_unit_file.3F
#
# Don't forget to reload systemd daemon after you change unit configuration:
# root> systemctl --system daemon-reload

[Unit]
Description=MySQL 8.0 database server
After=syslog.target
After=network.target

[Service]
Type=notify
User=mysql
Group=mysql

#ExecStartPre=/usr/libexec/mysql-check-socket
#ExecStartPre=/usr/libexec/mysql-prepare-db-dir %n
# Note: we set --basedir to prevent probes that might trigger SELinux alarms,
# per bug #547485
ExecStart={$SERVER_PATH}/mysql-yum/bin/usr/sbin/mysqld --defaults-file={$SERVER_PATH}/mysql-yum/etc/my.cnf --basedir={$SERVER_PATH}/mysql-yum/bin/usr --user=mysql
#ExecStartPost=/usr/libexec/mysql-check-upgrade
#ExecStopPost=/usr/libexec/mysql-wait-stop

# Give a reasonable amount of time for the server to start up/shut down
TimeoutSec=300

# Place temp files in a secure directory, not /tmp
PrivateTmp=false

Restart=on-failure

RestartPreventExitStatus=1

# Sets open_files_limit
LimitNOFILE = 10000

# Set enviroment variable MYSQLD_PARENT_PID. This is required for SQL restart command.
Environment=MYSQLD_PARENT_PID=1

[Install]
WantedBy=multi-user.target
