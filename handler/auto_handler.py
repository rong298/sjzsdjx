#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jacky'

from handler.base_handler import BaseHandler
from biz.base_biz import BaseBusiness
from biz.dama2_biz import Dama2Business
from biz.manul_biz import ManulBusiness
from biz.ruokuai_biz import RuokuaiBusiness
from biz.yundama_biz import YunDamaBusiness


from lib.md5_lib import MD5
import base64
import datetime
import logging


class AutoHandler(BaseHandler):

    def _do_query_dama(self, params):

        # 参数校验
        params = params['params']
        seller_platform = params['seller_platform']
        seller = params['seller']
        scene = params['scene']
        image = params['content']

        # 从数据库中获取分发规则
        dama_platform = self.distribute(seller_platform, seller, scene)
        if not dama_platform:
            self._fail_out(10003)
            return

        # 缓存图片到Redis
        search_key = MD5.create(image)
        self.redis.set(search_key, base64.b64encode(image))
        self.redis.expire(search_key, 60*10)

        config = self._load_config('/config/%s.ini' % dama_platform)

        # 启动Biz
        process_biz = None
        if dama_platform == BaseBusiness.MANUL:
            process_biz = ManulBusiness(db=self.db, config=config)
        elif dama_platform == BaseBusiness.DAMA2:
            process_biz = Dama2Business(db=self.db, config=config)
        elif dama_platform == BaseBusiness.RUOKUAI:
            process_biz = RuokuaiBusiness(db=self.db, config=config)
        elif dama_platform == BaseBusiness.YUNDAMA:
            process_biz = YunDamaBusiness(db=self.db, config=config)
        else:
            config = self._load_config('/config/%s.ini' % BaseBusiness.RUOKUAI)
            process_biz = RuokuaiBusiness(db=self.db, config=config)


        # 记录pass_code_records
        start_time = datetime.datetime.now()
        record_id = process_biz.query_record(dama_platform, seller_platform, seller, self.request.remote_ip, start_time)
        if not record_id:
            logging.error('[%s][%s]RecordFail...',dama_platform, record_id)
            self._fail_out(10002)
            return

        # 根据排序规则选择不同的biz进行调用,返回的是格式化之后的坐标
        #
        # {'dama_token':'', 'position':'', 'origin_result':'', 'status':1}
        #
        result = process_biz.passcode_identify(record_id=record_id, image_content=image, redis_key=search_key)
        if not result:
            logging.error('[%s][%s]Result:%s',dama_platform, record_id, result)
            self._fail_out(10000)
            return

        end_time = datetime.datetime.now()

        logging.info('[%s][%s]Result:%s',dama_platform, record_id, result)
        # 记录pass_code_records
        process_biz.response_record(record_id, result['dama_token'], end_time, result['origin_result'], result['status'])

        # 统一输出返回值
        self._succ_out({
            'query_id': record_id,
            'dama_platform': dama_platform,
            'pass_code': result['position']
            })

    def distribute(self, seller_platform, seller, scene):
        dist = self.db.get(
            "SELECT * FROM `pass_code_config` WHERE seller_platform=%s AND seller=%s AND scene=%s",
            seller_platform, seller, scene
        )
        if not dist:
            return False

        dama_platform = dist['dama_platform']
        return dama_platform



