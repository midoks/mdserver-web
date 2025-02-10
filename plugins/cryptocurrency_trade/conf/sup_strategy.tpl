[program:{$NAME}]
command=bash -c "cd {$RUN_ROOT} && source bin/activate && python3 {$ABS_FILE} long"
directory={$RUN_ROOT}
autorestart=true
startsecs=3
startretries=3
stdout_logfile={$SUP_ROOT}/log/{$NAME}.out.log
stderr_logfile={$SUP_ROOT}/log/{$NAME}.err.log
stdout_logfile_maxbytes=2MB
stderr_logfile_maxbytes=2MB
user=root
priority=999
numprocs=1
process_name=%(program_name)s