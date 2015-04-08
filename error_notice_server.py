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
from lib.api.ruokuai import RClient as RK
from lib.api.yundama import YDMHttp
import traceback
import requests

from tornado.options import define, options
import os, sys
from configobj import ConfigObj
from biz.base_biz import BaseBusiness


define("proc", default=1, type=int, help="Starts multiple worker processes")
define("query_id", default='', type=str, help="code query id")


_MYSQL_HOST = '127.0.0.1'
_MYSQL_USER = 'root'
_MYSQL_PASSWORD = 'kyfw100+'
_MYSQL_DATABASE = 'pass_code'


_PLATFORM_DAMA2 = BaseBusiness.DAMA2
_PLATFORM_RUOKUAI = BaseBusiness.RUOKUAI
_PLATFORM_QN = BaseBusiness.RUOKUAI
_PLATFORM_YUNDAMA = BaseBusiness.YUNDAMA
_PLATFORM_MANUL = BaseBusiness.MANUL
_PLATFORM_YUNSU = BaseBusiness.YUNSU


ABSPATH = os.path.dirname(os.path.abspath(sys.argv[0]))
CONFIG_PATH = ABSPATH + '/config'


class RuoKuai(object):

    def __init__(self, seller='yh'):
        config = ConfigObj(CONFIG_PATH + '/dama_platform.ini', encoding='UTF8')
        self.config = config[_PLATFORM_RUOKUAI][seller]

    def notice(self, query_id):
        ruokuai = self.config
        logging.info('Notice ===[ruokuai]===,query_id:%s', query_id)
        try:
            rc = RK(ruokuai['account'], ruokuai['password'], ruokuai['code'], ruokuai['token'])
            result = rc.rk_report_error(query_id)
        except:
            logging.error(traceback.format_exc())
            return False

        logging.info("Notice Response[ruokuai]: %s" % result)
        if result.has_key('Result') and result['Result'] == u'报告成功':
            return True
        else:
            return False

class YunSu(object):

    def __init__(self, seller='yh'):
        config = ConfigObj(CONFIG_PATH + '/dama_platform.ini', encoding='UTF8')
        self.config = config[_PLATFORM_YUNSU][seller]

    def notice(self, query_id):
        ruokuai = self.config
        logging.info('Notice ===[yunsu]===,query_id:%s', query_id)
        try:
            rc = RK(ruokuai['account'], ruokuai['password'], ruokuai['code'], ruokuai['token'])
            result = rc.rk_report_error(query_id)
        except:
            logging.error(traceback.format_exc())
            return False

        logging.info("Notice Response[yunsu]: %s" % result)
        if result.has_key('Result') and result['Result'] == u'报告成功':
            return True
        else:
            return False


class Dama2(object):
    def __init__(self, seller='yh'):
        config = ConfigObj(CONFIG_PATH + '/dama_platform.ini', encoding='UTF8')
        self.config = config[_PLATFORM_DAMA2][seller]

    def notice(self, query_id):
        logging.info('Notice ===[dama2]===,query_id:%s', query_id)
        url = self.config['adepter_url']+'/balance.php'
        post_data = {
            'id': query_id,
            'username': self.config['account'],
            'password': self.config['password'],
            'app_key': self.config['token'],
            'app_id': self.config['code']
        }
        response = requests.post(url=url, data=post_data)
        logging.info('Notice ===[dama2]===,response:%s', response.text)
        result = response.json()
        if result.has_key('ret') and result['ret'] == '0':
            return True
        return False

class YunDama(object):
    def __init__(self, seller='yh'):
        config = ConfigObj(CONFIG_PATH + '/dama_platform.ini', encoding='UTF8')
        self.config = config[_PLATFORM_YUNDAMA][seller]

    def notice(self, query_id):
        config = self.config
        logging.info('Notice ===[yundama]===,query_id:%s', query_id)
        try:
            yundama = YDMHttp(
                username = config['username'].encode("UTF-8"),
                password = config['password'].encode("UTF-8"),
                appid = config['appid'].encode("UTF-8"),
                appkey = config['appkey'].encode("UTF-8")
            )

            uid = yundama.login()
            result = yundama.report(query_id)
        except:
            logging.error(traceback.format_exc())
            return False

        logging.info("Notice Response[yundama]: %s" % result)
        if int(result) == 0:
            return True
        else:
            return False


class ErrorNotice(object):

    def __init__(self):
        config = ConfigObj(CONFIG_PATH + '/config_online.ini', encoding='UTF8')
        self.db = database.Connection(**config['mysql'])

    def notice_qn(self, query_id):
        logging.info('Notice ===[qn]===,query_id:%s', query_id)
        return True

    def notice_manul(self, query_id):
        logging.info('Notice ===[manul]===,query_id:%s', query_id)
        affect = self.db.execute_rowcount(
            "UPDATE `pass_code` SET `flag`=2 WHERE `id`=%s", query_id
        )
        if affect:
            logging.info('Notice Response[manul]:%s', affect)
            return True

        return False

    def notice(self, error):
        platform = error['dama_platform']
        query_id = error['dama_token_key']
        seller = error['seller']

        try:
            if platform == _PLATFORM_DAMA2:
                flag = Dama2(seller).notice(query_id=query_id)
            elif platform == _PLATFORM_MANUL:
                flag = self.notice_manul(query_id=query_id)
            elif platform == _PLATFORM_RUOKUAI:
                flag = RuoKuai(seller).notice(query_id=query_id)
            elif platform == _PLATFORM_QN:
                flag = self.notice_qn(query_id)
            elif platform == _PLATFORM_YUNDAMA:
                flag = YunDama(seller).notice(query_id)
            else:
                flag = False
        except:
            flag = False

        if flag:
            to_status = 3
            logging.info('Notice Completed [SUCCESS],query_id:%s', query_id)
        else:
            to_status = 4
            logging.info('Notice Completed [FAIL],query_id:%s', query_id)

        affect = self.db.execute_rowcount("UPDATE `pass_code_records` SET notice_status=%s WHERE id=%s", to_status, error['id'])

        if affect:
            logging.info('Update Records [SUCCESS],query_id:%s,status:%s', query_id, to_status)
        else:
            logging.info('Update Records [FAIL],query_id:%s', query_id)

    def start(self):
        while True:
            logging.info(u"%s scanning ... %s", '='*10, '='*10)
            # 获取错误列表
            errors = self.db.query(
                "SELECT * FROM `pass_code_records` WHERE notice_status=1"
            )


            numbers = 0
            for error in errors:
                affect = self.db.execute_rowcount(
                    "UPDATE `pass_code_records` SET notice_status=2 WHERE id=%s",
                    error['id']
                )
                if affect:
                    # 通知平台
                    self.notice(error)
                    numbers = numbers + 1

            if options.logging.lower() == 'debug':
                break

            time.sleep(1)

def signal_handler(signal, frame):
    logging.warn('You pressed Ctrl+C - or killed me with -2')
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    tornado.options.parse_command_line()
    if options.proc!= 1:
        tornado.process.fork_processes(options.proc)
    ErrorNotice().start()

if __name__ == '__main__':
    main()

