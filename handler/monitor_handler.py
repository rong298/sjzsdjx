#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jacky'

from handler.base_handler import BaseHandler
from biz.monitor_biz import MonitorBusiness
import datetime
import logging
import time

class MonitorErrorHandler(BaseHandler):

    def _do_get(self):
        if datetime.datetime.now().time() < datetime.time(
                    7, 0, 0) or datetime.datetime.now().time() > datetime.time(23, 0, 0):
            logging.info(">>> 12306 under maintenance.")
            self.write("OK")
            time.sleep(60)
            return

        config = self.config
        op_config = config['monitor']
        monitor_term = op_config['monitor_term']
        error_ratio = op_config['error_ratio']

        monitor_biz = MonitorBusiness(db=self.db)

        # 错误数监控
        error_info = monitor_biz.get_error_ratio(monitor_term, error_ratio)

        if not error_info:
            self.write("OK")
        else:
            self.write("%s,错误率超过%s,取样时间%s分钟" % (','.join(error_info), error_ratio, monitor_term))
        return

class MonitorTimeOutHandler(BaseHandler):

    def _do_get(self):
        if datetime.datetime.now().time() < datetime.time(
                    7, 0, 0) or datetime.datetime.now().time() > datetime.time(23, 0, 0):
            logging.info(">>> 12306 under maintenance.")
            self.write("OK")
            time.sleep(60)
            return

        config = self.config
        op_config = config['monitor']
        monitor_term = op_config['monitor_term']
        timeout = op_config['timeout']

        monitor_biz = MonitorBusiness(db=self.db)

        # 超时统计
        error_info = monitor_biz.get_timeout_ratio(monitor_term, timeout)

        if not error_info:
            self.write("OK")
        else:
            self.write("%s,平均处理时间超过%s秒,取样时间%s分钟" % (','.join(error_info), timeout, monitor_term))

        return

