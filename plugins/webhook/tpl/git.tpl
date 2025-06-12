echo "" > {$ROOT_PATH}/server/webhook/scripts/{$REPO_NAME}.log

export HOME=/tmp
date "+%Y-%m-%d %H:%M:%S"

# 和手动命令一起执行一次
git config --global credential.helper store
git config --global pull.rebase false


if [ ! -d {$ROOT_PATH}/gitcode ];then
	mkdir -p {$ROOT_PATH}/gitcode
fi 

if [ -d {$ROOT_PATH}/gitcode/{$REPO} ];then
	which sudo
	if [ "$?" == "0" ];then
		cd {$ROOT_PATH}/gitcode/{$REPO} && sudo git pull
	else
		cd {$ROOT_PATH}/gitcode/{$REPO} && git pull
	fi
else
	cd {$ROOT_PATH}/gitcode && git clone http://0.0.0.0:6660/xx/{$REPO}
fi

if [ ! -d {$ROOT_PATH}/wwwroot/{$REPO} ];then
	mkdir -p {$ROOT_PATH}/wwwroot/{$REPO}
fi 

rsync -vauP '--exclude=.*' {$ROOT_PATH}/gitcode/{$REPO}/ {$ROOT_PATH}/wwwroot/{$REPO}
chown -R www:www {$ROOT_PATH}/wwwroot/{$REPO}



