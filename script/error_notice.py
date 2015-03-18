#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jacky'


#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jacky'

import sys
import signal
import tornado
import logging
import tornado.process
from lib import database
import time
from lib.api import ruokuai as RK

from tornado.options import define, options


define("num_processes", default=1, type=int, help="Starts multiple worker processes")
define("query_id", default='', type=str, help="code query id")


_MYSQL_HOST = '127.0.0.1'
_MYSQL_USER = 'root'
_MYSQL_PASSWORD = '123456'
_MYSQL_DATABASE = 'dama'

_DAMA_TABLE_NAME = 'dama'

_PLATFORM_DAMA2 = 'dama2'
_PLATFORM_RUOKUAI = 'ruokuai'
_PLATFORM_QN = 'qn_dama'
_PLATFORM_MANUL = 'manul'

ruokuai = {
    'account': 'zhoulinhu',
    'password': 'yur140608',
    'code': '28710',
    'token': '8619c2753332465a9507053de2dedfb6'
}


class ErrorNotice(object):

    def __init__(self):
        self.db = database.Connection(
            host=_MYSQL_DATABASE, database=_MYSQL_DATABASE,
            user=_MYSQL_USER, password=_MYSQL_PASSWORD
        )

    def notice_dama2(self, query_id):
        logging.info('Notice ===[dama2]===,query_id:%s', query_id)
        pass

    def notice_ruokuai(self, query_id):
        logging.info('Notice ===[ruokuai]===,query_id:%s', query_id)
        rc = RK(ruokuai['account'], ruokuai['password'], ruokuai['code'], ruokuai['token'])
        result = rc.rk_report_error(id)
        logging.info("Notice Response[ruokuai]: %s" % result)

    def notice_qn(self, query_id):
        logging.info('Notice ===[qn]===,query_id:%s', query_id)
        pass

    def notice_manul(self, query_id):
        logging.info('Notice ===[manul]===,query_id:%s', query_id)
        affect = self.db.execute_rowcount(
            "UPDATE `pass_code` SET `status`=3 WHERE search_key=%s", query_id
        )
        if affect:
            logging.info('Notice Response[manul]:%s', affect)

    def notice(self, error):

        platform = error['dama_platform']
        query_id = error['dama_platform_query_id']

        if platform == _PLATFORM_DAMA2:
            self.notice_dama2(query_id)

        elif platform == _PLATFORM_MANUL:
            self.notice_manul(query_id)

        elif platform == _PLATFORM_RUOKUAI:
            self.notice_ruokuai(query_id)

        elif platform == _PLATFORM_QN:
            self.notice_qn(query_id)

        else:
            return False

    def start(self):

        while True:
            logging.info(u"%s 开始扫描 %s", '='*10, '='*10)
            # 获取错误列表
            errors = self.db.query(
                "SELECT * FROM `%s` WHERE status=2", _DAMA_TABLE_NAME
            )

            for error in errors:
                affect = self.db.execute_rowcount(
                    "UPDATE `%s` SET status=4 WHERE id=%s",
                    _DAMA_TABLE_NAME,
                    error['id']
                )
                if affect:
                    # 通知平台
                    self.notice(error)

            logging.info(u"%s 扫描结束 %s", '='*10, '='*10)
            time.sleep(5)
            if options.logging.lower() == 'debug':
                break

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

