#!/bin/bash

/usr/bin/python /home/kyfw/workspace/code_recognition/crontab_server.py --method=db_backup --log_file_max_size=100000000000 --log_file_num_backups=1 --log_file_prefix=/home/kyfw/workspace/code_recognition/logs/crontab_server.log

