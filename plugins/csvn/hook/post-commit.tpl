#!/bin/bash



REPOS="$1"
REV="$2"
TXN_NAME="$3"

REPOS_NAME=${REPOS##*/}

sh -x $REPOS/hooks/commit $REPOS_NAME $REV $TXN_NAME 2>$REPOS/sh.log
