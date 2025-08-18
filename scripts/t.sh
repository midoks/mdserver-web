#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
export LANG=en_US.UTF-8


DOMAIN="https://gh-proxy.com/"

DOMAIN=`echo $DOMAIN | sed 's|https://||g'`
DOMAIN=`echo $DOMAIN | sed 's|/||g'`
echo $DOMAIN