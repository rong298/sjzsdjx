#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jacky'

import sys
import signal
import tornado
import logging
import tornado.process
#from lib import database
import lib.database as database
import time
from lib.api import ruokuai as RK

from tornado.options import define, options


define("num_processes", default=1, type=int, help="Starts multiple worker processes")
define("query_id", default='', type=str, help="code query id")


_MYSQL_HOST = '115.29.108.132'
_MYSQL_USER = 'root'
_MYSQL_PASSWORD = 'kyfw100+'
_MYSQL_DATABASE = 'pass_code'


_PLATFORM_DAMA2 = 'dama2'
_PLATFORM_RUOKUAI = 'ruokuai'
_PLATFORM_QN = 'qn_dama'
_PLATFORM_MANUL = 'manul'

# 若快的账号信息
ruokuai = {
    'account': 'yunhu001',
    'password': 'yur140608',
    'code': 'yunhu001',
    'token': '2bc2d023cf3641bda85c476488d30197'
}

# 打码兔的账号信息
dama2 = {
    'account': 'yunhu001',
    'password': 'yur140608',
    'code': 'yunhudama2',
    'token': '0b9c7e07a56c23d53bf9031c305e1fc3'
}


class ErrorNotice(object):

    def __init__(self):
        self.db = database.Connection(
            host=_MYSQL_HOST, database=_MYSQL_DATABASE,
            user=_MYSQL_USER, password=_MYSQL_PASSWORD
        )

    def notice_dama2(self, query_id):
        logging.info('Notice ===[dama2]===,query_id:%s', query_id)

    def notice_ruokuai(self, query_id):
        logging.info('Notice ===[ruokuai]===,query_id:%s', query_id)
        rc = RK(ruokuai['account'], ruokuai['password'], ruokuai['code'], ruokuai['token'])
        result = rc.rk_report_error(id)
        logging.info("Notice Response[ruokuai]: %s" % result)
        return True

    def notice_qn(self, query_id):
        logging.info('Notice ===[qn]===,query_id:%s', query_id)

    def notice_manul(self, query_id):
        logging.info('Notice ===[manul]===,query_id:%s', query_id)
        affect = self.db.execute_rowcount(
            "UPDATE `pass_code` SET `status`=3 WHERE search_key=%s", query_id
        )
        if affect:
            logging.info('Notice Response[manul]:%s', affect)
            return True

        return False

    def notice(self, error):
        platform = error['dama_platform']
        query_id = error['dama_platform_query_id']

        if platform == _PLATFORM_DAMA2:
            flag = self.notice_dama2(query_id)

        elif platform == _PLATFORM_MANUL:
            flag = self.notice_manul(query_id)

        elif platform == _PLATFORM_RUOKUAI:
            flag = self.notice_ruokuai(query_id)

        elif platform == _PLATFORM_QN:
            flag = self.notice_qn(query_id)
        else:
            flag = False

        if flag:
            affect = self.db.execute_rowcount("UPDATE `pass_code_records` SET status=5 WHERE id=%s", error['id'])
        else:
            affect = self.db.execute_rowcount("UPDATE `pass_code_records` SET status=2 WHERE id=%s", error['id'])




    def start(self):
        while True:
            logging.info(u"%s 开始扫描 %s", '='*10, '='*10)
            # 获取错误列表
            errors = self.db.query(
                "SELECT * FROM `pass_code_records` WHERE status=2"
            )

            for error in errors:
                affect = self.db.execute_rowcount(
                    "UPDATE `pass_code_records` SET status=4 WHERE id=%s",
                    error['id']
                )
                if affect:
                    # 通知平台
                    self.notice(error)

            logging.info(u"%s 扫描结束 %s", '='*10, '='*10)
            if options.logging.lower() == 'debug':
                break

            time.sleep(5)

def signal_handler(signal, frame):
    logging.warn('You pressed Ctrl+C - or killed me with -2')
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    tornado.options.parse_command_line()
    if options.num_processes != 1:
        tornado.process.fork_processes(options.num_processes)
    ErrorNotice().start()

if __name__ == '__main__':
    main()

