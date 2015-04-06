#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jacky'

import signal
import tornado
import logging
import tornado.process
import lib.database as database
import time
import datetime

import traceback
import requests

from tornado.options import define, options
import os, sys
from configobj import ConfigObj


ABSPATH = os.path.dirname(os.path.abspath(sys.argv[0]))
CONFIG_PATH = ABSPATH + '/config'

class CrontabServer(object):

    def __init__(self):
        config = ConfigObj(CONFIG_PATH + '/config_online.ini', encoding='UTF8')
        self.db = database.Connection(**config['mysql'])

    def start(self):
        if not (datetime.datetime.now().time() > datetime.time(1, 30, 0) and datetime.datetime.now().time() < datetime.time(3, 0, 0)):
            logging.info(">>> 12306 under maintenance.")
            return

        current_table_name = 'pass_code_records'
        backup_table_name = current_table_name + '_' + datetime.datetime.now().strftime('%Y%m%d')

        # 重命名数据库
        rename_sql = "RENAME TABLE `%s` TO `%s`" % (current_table_name, backup_table_name)
        self.db.execute(rename_sql)

        # 创建新数据库
        create_sql = "CREATE TABLE `%s` LIKE `%s`" % (current_table_name, backup_table_name)
        self.db.execute_rowcount(create_sql)

        # 检查创建结果
        try:
            check_sql = "SELECT count(1) as co FROM `%s`" % current_table_name
            row = self.db.get(check_sql)

            if 0 == row['co']:
                logging.info("Rename Table Success")
            else:
                logging.error("Rename Table Fail, Old Table Exists!")

        except Exception as e:
            logging.error(traceback.format_exc())


def signal_handler(signal, frame):
    logging.warn('You pressed Ctrl+C - or killed me with -2')
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    tornado.options.parse_command_line()
    CrontabServer().start()

if __name__ == '__main__':
    main()

