#!/bin/bash
process_num=`ps -ef|grep 'manul_server.py'|grep -v 'grep'|wc -l`

if [ $process_num == 0 ]
then
	echo "start..."
	nohup /usr/bin/python /home/kyfw/workspace/code_recognition/manul_server.py --proc=50 --log_file_max_size=100000000000 --log_file_num_backups=1 --log_file_prefix=/home/kyfw/workspace/code_recognition/logs/manul.log &
else
	echo "Already Started, Please Stop then start"
fi

process_num=`ps -ef|grep 'manul_server.py'|grep -v 'grep'|wc -l`

if [ $process_num > 200 ]
then
	echo "Start Success"
else
	echo "Start Fail"
fi
