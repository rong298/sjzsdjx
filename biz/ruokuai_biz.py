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
import traceback
import re

from lib.api.ruokuai import RClient
from biz.base_biz import BaseBusiness
import base64

class RuokuaiBusiness(BaseBusiness):

    _PLATFORM_CODE = BaseBusiness.RUOKUAI


    def passcode_identify(self, record_id, image_content, params=None, redis_key=''):
        config = self.config
        logging.debug('[ruokuai]account:%s', config)

        try:
            image_buffer = base64.b64decode(image_content)
        except:
            image_buffer = image_content

        try:
            rc = RClient(
                config['account'],
                config['password'],
                config['code'],
                config['token']
            )
            response = rc.rk_create(image_buffer, config['image_type'])
            logging.debug('Result:%s', response)
        except:
            logging.error(traceback.format_exc())
            self.error_record(record_id, 2)

        logging.debug('[ruokuai][%s]Result:%s', record_id, response)
        result = self.parse_result(response)
        if not result:
            logging.debug('[ruokuai][%s]ResultParseFail:%s', record_id, result)
            self.error_record(record_id, 3, 1)
            return False

        return result


    def parse_params(self):
        pass

    def parse_result(self, res):
        if res.has_key('Error_Code'):
            return False

        if not res.has_key('Result'):
            return False

        code = str(res['Result'])

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

    def account_detail(self):
        pass
