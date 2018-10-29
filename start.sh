#!/bin/sh

gunicorn -b 127.0.0.1:7200 app:app &

python task.py &

#open "http://127.0.0.1:7200"