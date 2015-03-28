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
import cjson


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

        logging.info('NewQuery ==> %s,%s,%s', seller_platform, seller, scene)

        # 从数据库中获取分发规则
        dama_platform = self.distribute_v2(seller_platform, seller, scene)

        # 缓存图片到Redis
        search_key = MD5.create(image)
        self.redis.set(search_key, base64.b64encode(image))
        self.redis.expire(search_key, 60*10)

        config = self.dp_config[dama_platform][seller]

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
            config = self.dp_config[BaseBusiness.RUOKUAI]
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
        if self.check_redis():
            logging.info("Refresh Distribute Redis Success")

        item = self.get_dist_from_redis(seller_platform, seller, scene)
        logging.debug('Redis Distribut:%s',item)

        if not item:
            item = self.db.get(
                "SELECT * FROM `pass_code_config` WHERE seller_platform='default' AND seller='dafault' AND scene='default' LIMIT 1",
                seller_platform, seller
            )

        if item:
            dama_platform = item['dama_platform']
            self.distribute_code = item['token']
        else:
            dama_platform = self.config['default']['dama_platform']
            self.distribute_code = self.config['default']['dama_token']

        logging.info('[%s,%s,%s] Distribute ===> %s,%s', seller_platform, seller, scene, dama_platform, self.distribute_code)
        return dama_platform

    def get_dist_from_redis(self, seller_platform, seller, scene):
        redis_key = '_'.join([seller_platform, seller])
        item = self.redis.get(redis_key)
        if not item:
            return False

        item = cjson.decode(item)

        if item.has_key(scene):
            item = item.get(scene)
        else:
            item = item.get('default', False)

        return item

    def check_redis(self):
        # 三分钟前的时间
        now = datetime.datetime.now()

        # 比较是否要更新时间
        redis_config_key = 'pass_code_config_redis_cache_key'
        last_update_time = self.redis.get(redis_config_key)
        if last_update_time:
            last_update_time_1 = datetime.datetime.strptime(last_update_time,'%Y-%m-%d %H:%M:%S')
            diff = (now-last_update_time_1).seconds
            logging.debug('In Refresh:old:%s,now:%s', last_update_time, now)
            # 还未过期
            if diff < 180:
                return False

        # 已过期，需要重新更新redis
        items = self.db.query(
            "SELECT * FROM `pass_code_config`"
        )
        logging.debug('check_redis=001=>%s', datetime.datetime.now()-now)
        content = {}
        for it in items:
            redis_key = '_'.join([it['seller_platform'], it['seller']])
            if not content.has_key(redis_key):
                content[redis_key] = {}
            content[redis_key][it['scene']] = {
                'dama_platform': it['dama_platform'],
                'token': it['token']
            }
        logging.debug('check_redis=002=>%s', datetime.datetime.now()-now)
        now = datetime.datetime.now()
        for k,v in content.items():
            self.redis.set(k, cjson.encode(v))
            self.redis.expire(k, 60*3)
        logging.debug('check_redis=003=>%s', datetime.datetime.now()-now)
        now = datetime.datetime.now()
        # 更新标志位
        self.redis.set(redis_config_key, str(datetime.datetime.now())[:19])
        self.redis.expire(redis_config_key, 60*3)
        logging.debug('check_redis=004=>%s', datetime.datetime.now()-now)

        return True

    def refresh_redis(self):
        redis_config_key = 'pass_code_config_redis_cache_key'
        self.redis.set(redis_config_key, None)
        self.redis.expire(redis_config_key, 1)




