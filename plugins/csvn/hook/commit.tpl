#!/bin/bash

export LC_ALL=en_US.UTF-8
export LC_CTYPE=zh_CN.UTF-8


REPOS="$1"
REV="$2"
TXN_NAME="$3"


if [ ! -d  {$PROJECT_DIR}/csvn ]; then
	sudo mkdir -p {$PROJECT_DIR}/csvn
	sudo chown -R csvn:csvn {$PROJECT_DIR}/csvn
fi

SAVE_PATH={$PROJECT_DIR}/csvn/$REPOS
SVN_PATH=http://127.0.0.1:{$PORT}/svn/$REPOS

if [ ! -d  $SAVE_PATH ]; then
	svn co $SVN_PATH $SAVE_PATH 	\
		--username={$CSVN_USER}	\
		--password={$CSVN_PWD} 	\
		--no-auth-cache 		\
		--non-interactive
fi

cd $SAVE_PATH && svn update --username={$CSVN_USER} --password={$CSVN_PWD} --no-auth-cache  --non-interactive

WEB_PATH={$PROJECT_DIR}/wwwroot/$REPOS
sudo mkdir -p $WEB_PATH

sudo rsync -vauP --delete --exclude=".*" $SAVE_PATH/ $WEB_PATH
sudo chown -R www:www $WEB_PATH