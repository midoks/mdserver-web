#!/bin/bash

H_DIR={$HOOK_DIR}
HL_DIR={$HOOK_LOGS_DIR}


SH_LIST=`cd ${H_DIR} && ls | grep ".sh$"`

for sh_f in $SH_LIST; do
	ABS_FILE=${H_DIR}/${sh_f}
	ABS_LOGS=${HL_DIR}/${sh_f}.log
	echo "sh ${ABS_FILE} 2>${ABS_LOGS}"
	sh -x ${ABS_FILE} 2>${ABS_LOGS}
done