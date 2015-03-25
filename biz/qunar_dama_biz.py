#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 FIXUN
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import traceback
import urllib
import logging
import datetime
import traceback

import cjson
import requests

from biz.base_biz import BaseBusiness

class QunarDamaBusiness(BaseBusiness):

    _PLATFORM_CODE = BaseBusiness.QUNARDAMA

    def passcode_identify(self, record_id, image_content, params=None, redis_key=''):
        config = self.config
        order_id = self.order_id
        seller = self.change_seller()

        # 获取参数
        query_url = "agentCode=%s&orderNo=%s" % (seller, order_id)
        query_url = config['adepter_url'] + query_url
        query_params = image_content

        logging.debug('[%s][%s]QueryUrl:%s', self._PLATFORM_CODE, record_id, query_url)
        # 发送请求
        try:
            response = requests.post(query_url, data=query_params)
        except:
            logging.error(traceback.format_exc())
            self.error_record(record_id, 2, 1)
            return False

        logging.debug('[%s][%s]Result:%s', self._PLATFORM_CODE, record_id, response.text)
        # 解析结果
        result = self.parse_result(response.text)
        if not result:
            logging.debug('[%s][%s]ResultParseFail:%s', self._PLATFORM_CODE, record_id, result)
            # 解析失败
            self.error_record(record_id, 3, 1)
            return False
        return result

    def parse_params(self, image_content, image_type=287):
        pass

    def parse_result(self, response):
        res = cjson.decode(response)

        if not res.has_key('ret') or res['ret'] != True:
            # 接口调用失败
            return False

        if u"打码错误" in response or "EEEF" in response:
            return False

        ret = {
            'dama_token': 'QunarNoToken',
            'position': res['data']['passcode'],
            'origin_result': response,
            'status': 1
        }

        return ret

    def change_seller(self):

        if self.seller == 'yh':
            code = 'mcslw'
        elif self.seller == 'dh':
            code = 'dongf'
        else:
            code = False

        return code
