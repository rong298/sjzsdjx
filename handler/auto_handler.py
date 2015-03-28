#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jacky'

from handler.base_handler import BaseHandler
from biz.base_biz import BaseBusiness
from biz.dama2_biz import Dama2Business
from biz.manul_biz import ManulBusiness
from biz.ruokuai_biz import RuokuaiBusiness
from biz.yundama_biz import YunDamaBusiness
from biz.qunar_dama_biz import QunarDamaBusiness
from biz.yunsu_biz import YunsuBusiness


from lib.md5_lib import MD5
import base64
import datetime
import logging


class AutoHandler(BaseHandler):

    def _do_query_dama(self, params):

        # 参数校验
        params = params['params']
        seller_platform = params['seller_platform']
        seller_platform = params.get('seller_platform', 'default')
        seller = params.get('seller', 'default')
        scene = params.get('scene', 'default')
        order_id = params.get('order_id', '')
        image = params['content']

        # 从数据库中获取分发规则
        dama_platform = self.distribute_v2(seller_platform, seller, scene)

        # 缓存图片到Redis
        search_key = MD5.create(image)
        self.redis.set(search_key, base64.b64encode(image))
        self.redis.expire(search_key, 60*10)

        config = self._load_config('/config/%s.ini' % dama_platform)

        # 启动Biz
        process_biz = None
        if dama_platform == BaseBusiness.MANUL:
            process_biz = ManulBusiness(db=self.db, config=config, dis_code=self.distribute_code)
        elif dama_platform == BaseBusiness.DAMA2:
            process_biz = Dama2Business(db=self.db, config=config, dis_code=self.distribute_code)
        elif dama_platform == BaseBusiness.RUOKUAI:
            process_biz = RuokuaiBusiness(db=self.db, config=config, dis_code=self.distribute_code)
        elif dama_platform == BaseBusiness.YUNDAMA:
            process_biz = YunDamaBusiness(db=self.db, config=config, dis_code=self.distribute_code)
        elif dama_platform == BaseBusiness.QUNARDAMA:
            process_biz = QunarDamaBusiness(db=self.db, config=config, dis_code=self.distribute_code, order_id=order_id, seller=seller)
        elif dama_platform == BaseBusiness.YUNSU:
            process_biz = YunsuBusiness(db=self.db, config=config, dis_code=self.distribute_code)
        else:
            config = self._load_config('/config/%s.ini' % BaseBusiness.YUNDAMA)
            process_biz = RuokuaiBusiness(db=self.db, config=config, dis_code=self.distribute_code)


        # 记录pass_code_records
        start_time = datetime.datetime.now()
        record_id = process_biz.query_record(dama_platform, seller_platform, seller, self.request.remote_ip, start_time, order_id, scene)
        if not record_id:
            logging.error('[%s][%s]RecordFail...',dama_platform, record_id)
            self._fail_out(10002)
            return

        # 根据排序规则选择不同的biz进行调用,返回的是格式化之后的坐标
        #
        # {'dama_token':'', 'position':'', 'origin_result':'', 'status':1}
        #
        result = process_biz.passcode_identify(record_id=record_id, image_content=image, params=params, redis_key=search_key)
        if not result:
            logging.error('[%s][%s]Result:%s',dama_platform, record_id, result)
            self._fail_out(10000)
            return

        end_time = datetime.datetime.now()

        # 记录pass_code_records
        process_biz.response_record(record_id, result['dama_token'], end_time, result['origin_result'], result['status'])

        # 统一输出返回值
        final_out = {
            'query_id': record_id,
            'dama_platform': dama_platform,
            'pass_code': result['position']
            }
        logging.info('[%s][%s][%s][%s]FinalResult:%s,Spend:%s.',dama_platform, seller, scene, record_id, final_out, end_time-start_time)
        self._succ_out(final_out)

    def distribute(self, seller_platform, seller, scene=''):
        logging.info('[%s,%s,%s] Distribute Start', seller_platform, seller, scene)
        dist = self.db.get(
            "SELECT * FROM `pass_code_config` WHERE seller_platform=%s AND seller=%s AND scene=%s LIMIT 1",
            seller_platform, seller, scene
        )

        if not dist:
            dist = self.db.get(
                "SELECT * FROM `pass_code_config` WHERE seller_platform=%s AND seller=%s AND scene='default' LIMIT 1",
                seller_platform, seller
            )

        if not dist:
            dist = self.db.get(
                "SELECT * FROM `pass_code_config` WHERE seller_platform='default' AND seller='default' AND scene='default' LIMIT 1",
            )

        if dist:
            dama_platform = dist['dama_platform']
            self.distribute_code = dist['token']


        if not dist:
            dama_platform = self.config['default']['dama_platform']
            self.distribute_code = self.config['default']['dama_token']

        logging.info('[%s,%s,%s] Distribute ===> %s,%s', seller_platform, seller, scene, dama_platform, self.distribute_code)
        return dama_platform

    def distribute_v2(self, seller_platform, seller, scene=''):
        '''
        使用Redis
        :param seller_platform:
        :param seller:
        :param scene:
        :return:
        '''
        # 校验缓存
        if self.refresh_redis():
            logging.info("Refresh Distribute Redis Success")

        # Redis key 构造
        redis_key = '_'.join([seller_platform, seller, scene])

        # 查询Redis
        item = self.redis.get(redis_key)

        if not item:
            redis_key = '_'.join([seller_platform, seller, 'default'])
            item = self.redis.get(redis_key)

        if not item:
            redis_key = '_'.join(['default', 'default', 'default'])
            item = self.redis.get(redis_key)

        if item:
            dama_platform = item['dama_platform']
            self.distribute_code = item['token']
        else:
            dama_platform = self.config['default']['dama_platform']
            self.distribute_code = self.config['default']['dama_token']

        logging.info('[%s,%s,%s] Distribute ===> %s,%s', seller_platform, seller, scene, dama_platform, self.distribute_code)
        return dama_platform


    def refresh_redis(self):
        # 三分钟前的时间
        now = datetime.datetime.now()

        # 比较是否要更新时间
        redis_config_key = 'pass_code_config_redis_cache_key'

        last_update_time = self.redis.get(redis_config_key)
        delta = datetime.timedelta(minutes = 3)
        last_update_time = last_update_time + delta

        # 还未过期
        if last_update_time < now:
            return False

        # 已过期，需要重新更新redis
        items = self.db.query(
            "SELECT * FROM `pass_code_config`"
        )
        for it in items:
            redis_key = '_'.join[it['seller_platform'], it['seller'], it['scene']]
            self.redis.set(redis_key, it['dama_platform'])
            self.redis.expire(redis_key, 60*3)

        # 更新标志位
        self.redis.set(redis_config_key, datetime.datetime.now())

        return True



