#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jacky'

from base_biz import BaseBusiness
import logging

class OpBusiness(BaseBusiness):

    def normal_monitor(self, seller, term=10):
        seller_list = "','".join(seller)
        seller_list = "('" + seller_list + "')"

        sql = "select dama_platform,status,count(1) as count,avg(TIMESTAMPDIFF(SECOND, FROM_UNIXTIME(UNIX_TIMESTAMP(start_time)), FROM_UNIXTIME(UNIX_TIMESTAMP(end_time)))) as spendtime from pass_code_records where created>=DATE_SUB(NOW(),INTERVAL %s MINUTE) and seller in %s and status!=0 group by dama_platform,status" % (int(term), seller_list)
        res = self.db.query(sql)
        logging.debug('[normal_monitor]%s', sql)

        return res

    def get_all_platform(self, seller):

        seller_list = "','".join(seller)
        seller_list = "('" + seller_list + "')"


        sql = "select * from `pass_code_config` where seller in %s order by seller_platform,seller,scene" % seller_list
        res = self.db.query(sql)

        return res

    def change_platform(self, seller_platform, seller, scene, dama_platform):

        seller_platform = "','".join(seller_platform)
        seller_platform = "'" + seller_platform + "'"

        seller = "','".join(seller)
        seller = "'" + seller+ "'"

        scene = "','".join(scene)
        scene = "'" + scene + "'"

        sql = "UPDATE `pass_code_config` SET dama_platform='%s' WHERE seller_platform in (%s) AND seller in (%s) AND scene in (%s)" % \
              (dama_platform, seller_platform, seller, scene)

        logging.debug('[Change Platform]%s',sql)
        affect = self.db.execute_rowcount(sql)

        if affect:
            logging.info('[ChangePlatform]Success,%s,%s,%s,%s', seller_platform, seller, scene, dama_platform)
            return True
        else:
            logging.error('[ChangePlatform]Fail,%s,%s,%s,%s', seller_platform, seller, scene, dama_platform)
            return False

    # 财务信息
    def get_balance(self):
        pass







