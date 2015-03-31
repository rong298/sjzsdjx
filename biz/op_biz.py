#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jacky'

from base_biz import BaseBusiness
import logging

class OpBusiness(BaseBusiness):

    def normal_monitor(self, term=10):
        sql = "select dama_platform,status,count(1) as count,avg(TIMESTAMPDIFF(SECOND, FROM_UNIXTIME(UNIX_TIMESTAMP(start_time)), FROM_UNIXTIME(UNIX_TIMESTAMP(end_time)))) as spendtime from pass_code_records where created>=DATE_SUB(NOW(),INTERVAL %s MINUTE) and status!=0 group by dama_platform,status" % int(term)
        res = self.db.query(sql)
        logging.debug('[normal_monitor]%s', sql)

        return res

    def get_all_platform(self):
        sql = "select * from `pass_code_config` order by seller_platform,seller,scene"
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





