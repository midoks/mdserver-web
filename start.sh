#!/bin/sh

gunicorn -b 127.0.0.1:7200 mdweb:app