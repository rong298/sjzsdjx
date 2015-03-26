#!/bin/bash
process_num=`ps -ef|grep platform=auto|grep -v 'grep'|wc -l`

if [ $process_num == 0 ]
then
	echo "start..."
	nohup /usr/bin/python /home/kyfw/workspace/code_recognition/main_server.py --port=10008 --platform=auto --proc=200 --log_file_max_size=100000000000 --log_file_num_backups=1 --log_file_prefix=/home/kyfw/workspace/code_recognition/logs/auto.log &
else
	echo "Already Started, Please Stop then start"
fi

process_num=`ps -ef|grep platform=auto|grep -v 'grep'|wc -l`

if [ $process_num > 200 ]
then
	echo "Start Success"
else
	echo "Start Fail"
fi