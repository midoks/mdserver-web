#!/bin/sh

DEBUG=True
gunicorn -b 127.0.0.1:7200 main:app

#open "http://127.0.0.1:7200"