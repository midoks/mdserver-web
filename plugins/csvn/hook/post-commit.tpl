#!/bin/bash



REPOS="$1"
REV="$2"
TXN_NAME="$3"


REPOS_NAME=${REPOS##*/}
WEB_DIR={$PRJOECT_DIR}/wwwroot/$REPOS_NAME
SVN_PATH=http://127.0.0.1:{$PORT}/svn/$REPOS_NAME
