#!/bin/bash
process_num=`ps -ef|grep 'crontab_server.py'| grep 'method=balance'|grep -v 'grep'|wc -l`

if [ $process_num == 0 ]
then
	echo "There is no process need kill"
else
	echo "Stop Process ..."
        ps -ef|grep "crontab_server.py"|grep 'method=balance'|grep -v grep|awk {'print $2'}|xargs kill -9
fi

process_num=`ps -ef|grep 'crontab_server.py'| grep 'method=balance'|grep -v 'grep'|wc -l`

if [ $process_num > 0 ]
then
	echo "Still Have ${process_num} processes need to kill, please retry"
else
	echo "Stop Success"
fi
