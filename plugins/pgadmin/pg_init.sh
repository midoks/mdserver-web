#!/bin/expect -d
set timeout 20

spawn gunicorn --bind unix:/tmp/pgadmin4.sock \
--workers=1 \
--threads=25 \
--chdir /www/server/pgadmin/run/lib/python3.10/site-packages/pgadmin4 pgAdmin4:app
expect {
    "Email address:" {  send "mdserver-web@gmail.com\r"; exp_continue }
    "Password" {  send "123123\r"  }
}
expect eof
