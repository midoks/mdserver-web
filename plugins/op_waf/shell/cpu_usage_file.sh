#!/bin/bash

DST_DIR=/www/server/op_waf
DIS_FILE=${DST_DIR}/cpu.info

function GetCpuUsage(){
	cpu_info=`cat /proc/stat | head -n 1`
	idle_cpu=`echo $cpu_info|awk '{print $2}'`
	cpu_total_time=0
	for ci in ${cpu_info[@]}; do
		if [ "$ci" == "cpu" ];then
			continue
		else
			#echo $ci
			cpu_total_time=`expr $cpu_total_time + $ci`
		fi
	done
	#echo "idle_cpu:${idle_cpu}"
	#echo "cpu_total_time:${cpu_total_time}"

	cpu_percet=$(awk "BEGIN{print ((${cpu_total_time}-${idle_cpu})/${cpu_total_time})*100}")
	echo "${cpu_percet}"
	return 0
}

# one value detal 
getOne=`GetCpuUsage`

CPU_USAGE=`echo $getOne | awk -F . '{print $1}'`
echo "cpu usage:${CPU_USAGE}"
echo $CPU_USAGE > $DIS_FILE
echo "done success!"


# two value compare 

# getOne=`GetCpuUsage`
# echo "getOne:$getOne"
# sleep 1
# getTwo=`GetCpuUsage`
# echo "getTwo:$getTwo"

# cpu_percet_calc=$(awk "BEGIN{print (${getOne}+${getTwo})/2}")
# echo "cpu_percet_calc:${cpu_percet_calc}"

# #echo '0.61212' | awk -F . '{print $1}'
# CPU_USAGE=`echo $cpu_percet_calc | awk -F . '{print $1}'`
# echo "cpu usage:${CPU_USAGE}"
# echo $CPU_USAGE > $DIS_FILE
# echo "done success!"