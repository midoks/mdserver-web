#!/bin/sh

gunicorn -c setting.py app:app &
python task.py &