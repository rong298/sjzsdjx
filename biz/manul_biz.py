#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jacky'

from biz.base_biz import BaseBusiness
import base64
import time
import cjson
import datetime
import re
import logging
import random



class ManulBusiness(BaseBusiness):

    _PLATFORM_CODE = 'manul'

    def passcode_identify(self, record_id,  image_content='', redis_key=''):
        # 图片标的
        image_search_key = redis_key

        # 校验旧文件
        result = self.check_old_image(image_search_key)
        if result:
            logging.debug('[%s][%s]CacheResult:%s', self._PLATFORM_CODE, image_search_key, result)
            return self.parse_result(record_id, result)

        # 创造新文件
        result = self.create_new_image(image_search_key)
        if not result:
            logging.debug('[%s][%s]CreateFail:%s', self._PLATFORM_CODE, image_search_key, result)
            # self.error_record(record_id, 2)
            # return False

        # 同步等待
        result = self.wait(image_search_key)
        if not result:
            logging.debug('[%s][%s]WaitFail:%s', self._PLATFORM_CODE, image_search_key, result)
            self.error_record(record_id, 3)
            return False

        result = self.parse_result(record_id, result)
        if not result:
            logging.debug('[%s][%s]ResultParseFail:%s', self._PLATFORM_CODE, record_id, result)
            self.error_record(record_id, 3, 1)
            return False

        return result

    def check_old_image(self, image_search_key):
        # 判断数据库中是否处理过该图片
        # 如果处理过并且验证是正确的，就直接把原值返回

        image = self.db.get(
            "SELECT * FROM `pass_code` WHERE search_key=%s", image_search_key
        )

        if image and image['result']:
            logging.info('[IMAGE][%s],Image have result:%s',image_search_key, image['result'])
            if image['flag'] != 1:
                # 如果这个图片存储过，但是验证是失败的，就重置状态，等待下次扫描
                self.db.execute_rowcount(
                    "UPDATE `pass_code` SET result='',operator'',status=1,flag=1 WHERE search_key=%s", image_search_key
                )
            else:
                return image

        return False

    def create_new_image(self, image_search_key):
        # 创造新文件, 这里是一个兼容，之前file_path是本地文件地址，现在时redis存得key
        affect = self.db.execute_lastrowid(
            "INSERT IGNORE INTO `pass_code` (`search_key`, `file_path`, `created`) VALUES (%s, %s, %s)",
            image_search_key,
            image_search_key,
            str(datetime.datetime.now())
        )
        return affect

    def wait(self, image_search_key):
        max_loops = int(self.config['timeout'])
        loop_times = 0
        while True:
            # Loop Part
            loop_times = loop_times + 1
            time.sleep(1)
            if loop_times > max_loops:
                break

            image = self.db.get(
                "SELECT * FROM `pass_code` WHERE search_key=%s AND status=3", image_search_key
            )
            logging.debug('[LOOP][%s][%s][%s] ===> %s', image_search_key, max_loops, loop_times, image)

            if image and image['result']:
                return image

        logging.error('[%s][%s][%s] ====> TimeOut <====', image_search_key, max_loops, loop_times)
        return False

    def parse_result(self, id, result):

        if 'result' not in result:
            self.error_record(id, 3)
            return False

        response = []
        code_position = BaseBusiness._CODE_POSITION
        for p in result['result']:
            if code_position[p]:
                response.append(random.choice(code_position[p]))
            else:
                self.error_record(id, 4)
                return False

        ret = {
            'dama_token': id,
            'position': ','.join(response),
            'origin_result': result['result'],
            'status': 1
        }
        return ret

