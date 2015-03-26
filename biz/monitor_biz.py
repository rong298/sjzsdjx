#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jacky'

from biz.base_biz import BaseBusiness

class MonitorBusiness(BaseBusiness):

    def get_error_ratio(self, term, error_ratio=0.5):
       dp_num = self.db.query(
           "SELECT dama_platform,count(1) as co FROM `pass_code_records` WHERE created>=DATE_SUB(NOW(),INTERVAL %s MINUTE) and status!=0 group by dama_platform", term
       )
       dp_error_num = self.db.query(
           "SELECT dama_platform,count(1) as co FROM `pass_code_records` WHERE created>=DATE_SUB(NOW(),INTERVAL %s MINUTE) and status!=1 and status!=0 group by dama_platform", term
       )
       error_monitor = []
       for su in dp_num:
           da = su['dama_platform']
           co = int(su['co'])
           ratio = 0
           for esu in dp_error_num:
               da_e = esu['dama_platform']
               co_e = int(esu['co'])
               if da == da_e:
                   ratio = float(co_e/co)
                   break
           if ratio > float(error_ratio):
               error_monitor.append(da)
       return error_monitor

    def get_timeout_ratio(self, term, timeout=60):
        dp_num = self.db.query(
            "SELECT dama_platform,avg(TIMESTAMPDIFF(SECOND, FROM_UNIXTIME(UNIX_TIMESTAMP(start_time)), FROM_UNIXTIME(UNIX_TIMESTAMP(end_time)))) as spendtime FROM `pass_code_records` WHERE created>=DATE_SUB(NOW(),INTERVAL %s MINUTE) and status!=0 group by dama_platform", term
        )
        error_monitor = []
        for su in dp_num:
            da = su['dama_platform']
            spendtime = float(su['spendtime'])
            if spendtime > float(timeout):
                error_monitor.append(da)
        return error_monitor
