#!/bin/sh

DEBUG=True
gunicorn -b 127.0.0.1:7200 mdweb:app