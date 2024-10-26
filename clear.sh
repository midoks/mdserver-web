#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/usr/local/lib/python2.7/bin



find . -name .DS_Store -print0 | xargs -0 git rm -f --ignore-unmatch
find . -name .DS_Store  | xargs rm -rf
find . -type d -name "*.pyc" | xargs rm -rf