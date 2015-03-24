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

from lib.api.yundama import YDMHttp
from biz.base_biz import BaseBusiness
import base64
import requests

class YunDamaBusiness(BaseBusiness):

    _PLATFORM_CODE = 'yundama'

    def passcode_identify(self, record_id, image_content, params=None, redis_key=''):
        config = self.config
        logging.debug('[%s]account:%s', self._PLATFORM_CODE, config)

        try:
            image_buffer = base64.b64decode(image_content)
        except:
            image_buffer = image_content

        try:
            yun_dama = YDMHttp(
                username = config['username'].encode("UTF-8"),
                password = config['password'].encode("UTF-8"),
                appid = config['appid'].encode("UTF-8"),
                appkey = config['appkey'].encode("UTF-8")
            )

            uid = yun_dama.login()
            response_id, result = yun_dama.decode(image_buffer, '6701', 60)
            logging.debug('[%s]Result:[%s][%s]', self._PLATFORM_CODE, response_id, result )
        except:
            logging.error(traceback.format_exc())
            self.error_record(record_id, 2)

        logging.debug('[%s][%s]Result:%s, %s', self._PLATFORM_CODE, record_id, response_id, result)
        result = self.parse_result(response_id, result)
        if not result:
            logging.error('[%s][%s]ResultParseFail:%s', self._PLATFORM_CODE, record_id, result)
            self.error_record(record_id, 3, 1)
            return False

        return result


    def parse_params(self):
        pass

    def parse_result(self, id, res):
        if not res:
            return False

        if id < 0:
            return False

        code = str(res)

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
            'dama_token': id,
            'position': result,
            'origin_result': res,
            'status': 1
        }

        return ret

