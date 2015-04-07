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

class Dama2Business(BaseBusiness):

    _PLATFORM_CODE = BaseBusiness.DAMA2

    def passcode_identify(self, record_id, image_content, params=None, redis_key=''):
        config = self.config

        # 获取参数
        query_params = self.parse_params(image_content)

        # 发送请求
        try:
            response = requests.post(config['adepter_url'], data=query_params)
        except:
            logging.error(traceback.format_exc())
            self.error_record(record_id, 2)
            return False

        logging.info('[dama2][%s]Result:%s', record_id, response.text)
        # 解析结果
        result = self.parse_result(record_id, response.text)
        if not result:
            logging.error('[dama2][%s]ResultParseFail:%s', record_id, response.text)
            return False

        return result

    def parse_params(self, image_content, image_type=287):
        params = {
            'file_type': str(image_type),
            'content': image_content
        }
        return params

    def parse_result(self, r_id, response):
        res = cjson.decode(response)

        if not res.has_key('ret') or res['ret'] != "0":
            # 接口调用失败
            self.error_record(r_id, 3)
            return False

        ret = {
            'dama_token': res['id'],
            'position': res['result'].replace('|', ","),
            'origin_result': res['result'],
            'status': 1
        }

        return ret

    def account_detail(self):
        config = self.config

        # 发送请求
        try:
            response = requests.post(config['adepter_url'])
        except:
            logging.error(traceback.format_exc())
            return False
        logging.debug('[%s]%s', self._PLATFORM_CODE, response.text)

        # 解析结果
        result = response.json()
        return {'score': result['balance'], 'update_time': datetime.datetime.now()}

