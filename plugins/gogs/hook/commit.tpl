#!/bin/bash

echo `date`

GITADDR="{$GITROOTURL}/{$USERNAME}/{$PROJECT}.git"
GIT_SDIR="{$CODE_DIR}"

GIT_USER_DIR="${GIT_SDIR}/{$USERNAME}"
GIT_PROJECT_DIR="${GIT_USER_DIR}/{$PROJECT}"


git config --global credential.helper store
git config --global pull.rebase false

# echo $GIT_PROJECT_DIR
if [ ! -d $GIT_PROJECT_DIR ];then
	mkdir -p $GIT_USER_DIR && cd $GIT_USER_DIR
	git clone $GITADDR --branch main
	if [ "$?" != "0" ];then 
		git clone $GITADDR
	fi
fi

unset GIT_DIR

cd $GIT_PROJECT_DIR && git pull

# func 2
# cd $GIT_PROJECT_DIR && env -i git pull origin master


#更新的目的地址
WEB_PATH={$WEB_ROOT}/{$USERNAME}/{$PROJECT}

if [ ! -d $WEB_PATH ];then
	mkdir -p $WEB_PATH
	rsync -vauP --delete --exclude=".*" $GIT_PROJECT_DIR/ $WEB_PATH
else
	if [ -f $GIT_PROJECT_DIR/exclude.list ];then
		rsync -vauP --delete --exclude-from="$GIT_PROJECT_DIR/exclude.list" $GIT_PROJECT_DIR/ $WEB_PATH
	else
		rsync -vauP --exclude=".*" $GIT_PROJECT_DIR/ $WEB_PATH
	fi
fi

sysName=`uname`
if [ $sysName == 'Darwin' ]; then
	USER=$(who | sed -n "2,1p" |awk '{print $1}')
	chown -R $USER:staff $WEB_PATH
else
	chown -R www:www $WEB_PATH
fi