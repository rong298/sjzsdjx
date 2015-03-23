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

import random
import logging
import datetime
import traceback
import re

import cjson
from configobj import ConfigObj

from lib.api.ruokuai import RClient
from base_biz import BaseBusiness
import base64

class RuokuaiBusiness(BaseBusiness):

    _PLATFORM_CODE = 'ruokuai'


    def passcode_identify(self, record_id, image_content, redis_key=''):
        config = self.config

        image_buffer = base64.b16encode(image_content)
        rc = RClient(
            config['account'],
            config['password'],
            config['code'],
            config['token']
        )
        try:
            response = rc.rk_create(image_buffer, config['image_type'])
            logging.info('Result:%s', response)
        except:
            logging.error(traceback.format_exc())
            self.error_record(record_id, 2)

        result = self.parse_result(record_id, response)
        if not result:
            self.error_record(record_id, 3, 1)
            return False

        return result


    def parse_params(self):
        pass

    def parse_result(self, res):
        if res.has_key('Error_Code'):
            return False

        if not res.has_key('result'):
            return False

        code = str(res['result'])

        # 正则判断返回的数据是否符合格式要求
        pattern = re.compile(r'^[1-8]{1,8}$')
        match = pattern.match(code)
        if not match:
            return False

        # 获取坐标
        result = []
        for p in code:
            position = random.choice(self._CODE_POSITION[p])
            result.append(position)
        result = ','.join(result)

        # 格式化返回

        ret = {
            'dama_token': res['Id'],
            'position': result,
            'origin_result': code,
            'status': 1
        }

        return ret

