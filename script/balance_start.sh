#!/bin/bash
process_num=`ps -ef|grep 'crontab_server.py'| grep 'method=balance'|grep -v 'grep'|wc -l`

if [ $process_num == 0 ]
then
	echo "start..."
	nohup /usr/bin/python /home/kyfw/workspace/code_recognition/crontab_server.py --method=balance --log_file_max_size=100000000000 --log_file_num_backups=1 --log_file_prefix=/home/kyfw/workspace/code_recognition/logs/balance.log &
else
	echo "Already Started, Please Stop then start"
fi

process_num=`ps -ef|grep 'crontab_server.py'| grep 'method=balance'|grep -v 'grep'|wc -l`

if [ $process_num > 0 ]
then
	echo "Start Success"
else
	echo "Start Fail"
fi
