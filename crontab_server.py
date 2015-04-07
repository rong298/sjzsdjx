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
from biz.ruokuai_biz import RuokuaiBusiness
from biz.yunsu_biz import YunsuBusiness
from biz.base_biz import BaseBusiness
import redis


ABSPATH = os.path.dirname(os.path.abspath(sys.argv[0]))
CONFIG_PATH = ABSPATH + '/config'

define("method", type=str, help="Starts multiple worker processes")

class CrontabServer(object):

    def __init__(self):
        temp_config = ConfigObj(CONFIG_PATH + '/config_online.ini', encoding='UTF8')
        self.db = database.Connection(**temp_config['mysql'])
        self.config = ConfigObj(CONFIG_PATH + '/dama_platform.ini', encoding='UTF8')
        self.redis = redis.Redis(**temp_config['redis'])

    def db_backup(self):
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

    def balance(self):
        if datetime.datetime.now().time() > datetime.time(23, 30, 0) or datetime.datetime.now().time() < datetime.time(7, 0, 0):
            logging.info(">>> 12306 under maintenance.")
            return

        # 获取打码平台的剩余题分

        # ruokuai
        config = self.config[BaseBusiness.RUOKUAI]['yh']
        redis_key = BaseBusiness.REDIS_KEY_RUOKUAI
        result = RuokuaiBusiness(db=self.db, config=config).account_detail()
        logging.info('[Ruokuai]Result:%s', result)
        self.redis.set(redis_key, result)
        self.redis.expire(redis_key, 60*60*1)

        # yunsu
        config = self.config[BaseBusiness.YUNSU]['yh']
        redis_key = BaseBusiness.REDIS_KEY_YUNSU
        result = YunsuBusiness(db=self.db, config=config).account_detail()
        logging.info('[Yunsu]Result:%s', result)
        self.redis.set(redis_key, result)
        self.redis.expire(redis_key, 60*60*1)

        # yundama
        # dama2




def signal_handler(signal, frame):
    logging.warn('You pressed Ctrl+C - or killed me with -2')
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    tornado.options.parse_command_line()
    method = str(options.method).lower()
    if method == 'db_backup':
        CrontabServer().db_backup()
    elif method == 'balance':
        CrontabServer().balance()

if __name__ == '__main__':
    main()

