echo "" > {$ROOT_PATH}/server/webhook/scripts/{$REPO_NAME}.log

export HOME=/tmp
date "+%Y-%m-%d %H:%M:%S"

git config --global credential.helper store
git config --global pull.rebase false


if [ -d {$ROOT_PATH}/gitcode/{$REPO} ];then
	cd {$ROOT_PATH}/gitcode/{$REPO} && sudo git pull
else
	git clone http://0.0.0.0:6660/xx/{$REPO}
fi


rsync -vauP '--exclude=.*' {$ROOT_PATH}/gitcode/{$REPO}/ {$ROOT_PATH}/wwwroot/{$REPO}
chown -R www:www {$ROOT_PATH}/wwwroot/{$REPO}



