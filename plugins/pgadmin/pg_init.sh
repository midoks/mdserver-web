#!/bin/bash

python_ver=`ls /www/server/pgadmin/run/lib/ | grep python | cut -d \  -f 1 | awk 'END {print}'`

expect <<-EOF
set time 10
spawn gunicorn --bind unix:/tmp/pgadmin4.sock \
--workers=1 \
--threads=25 \
--chdir /www/server/pgadmin/run/lib/${python_ver}/site-packages/pgadmin4 pgAdmin4:app
expect {
    "Email address:" {  send "mdserver-web@gmail.com\r"; exp_continue }
    "Password" {  send "123123\r"; exp_continue  }
    "Retype password" {  send "123123\r"  }
}
expect eof
EOF

pids=$(ps aux | grep 'pgAdmin4:app' | grep -v grep | awk '{print $2}')
arr=($pids)
for p in ${arr[@]}
do
    kill -9 $p  > /dev/null 2>&1
done
