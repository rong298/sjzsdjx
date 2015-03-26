#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jacky'

from handler.base_handler import BaseHandler
from biz.monitor_biz import MonitorBusiness

class MonitorErrorHandler(BaseHandler):

    def _do_get(self):

        config = self.config
        op_config = config['monitor']
        monitor_term = op_config['monitor_term']
        error_ratio = op_config['error_ratio']

        monitor_biz = MonitorBusiness(db=self.db)

        # 错误数监控
        error_info = monitor_biz.get_error_ratio(monitor_term, error_ratio)

        if not error_info:
            self.write("SUCCESS")
        else:
            self.write("%s,错误率超过%s,取样时间%s", ','.join(error_info), error_ratio, monitor_term)
        return

class MonitorTimeOutHandler(BaseHandler):

    def _do_get(self):
        config = self.config
        op_config = config['monitor']
        monitor_term = op_config['monitor_term']
        timeout = op_config['timeout']

        monitor_biz = MonitorBusiness(db=self.db)

        # 超时统计
        error_info = monitor_biz.get_timeout_ratio(monitor_term, timeout)

        if not error_info:
            self.write("SUCCESS")
        else:
            self.write("%s,平均处理时间超过%s,取样时间%s", ','.join(error_info), timeout, monitor_term)

        return

