#!/bin/bash

DST_DIR=/www/server/op_waf
DIS_FILE=${DST_DIR}/cpu.info

CPU_USAGE=`top -bn 1 | fgrep 'Cpu(s)' | awk '{print 100 -$8}' | awk -F . '{print $1}'`
echo $CPU_USAGE
echo $CPU_USAGE > $DIS_FILE
echo "done success!"