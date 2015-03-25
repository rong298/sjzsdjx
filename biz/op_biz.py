#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jacky'

from base_biz import BaseBusiness

class OpBusiness(BaseBusiness):

    def normal_monitor(self, term=10):
        sql = "select dama_platform,status,count(1) as count,avg(end_time-start_time) as spendtime from pass_code_records where created>=DATE_SUB(NOW(),INTERVAL %s MINUTE) and dama_token_key != '' group by dama_platform,status" % int(term)
        res = self.db.query(sql)

        return res


