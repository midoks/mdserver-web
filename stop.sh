#!/bin/sh

ps -ef|grep app:app |grep -v grep|awk '{print $2}'|xargs kill -9

ps -ef|grep task.py |grep -v grep|awk '{print $2}'|xargs kill -9

#open "http://127.0.0.1:7200"