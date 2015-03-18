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

import cjson
import datetime
import logging
import traceback
from biz.ruokuai_biz import RuokuaiBusiness
from configobj import ConfigObj

from base_handler import BaseHandler

class RuokuaiHandler(BaseHandler):
    
    def _do_query_dama(self, params):
        config = self._load_config('/config/%s.ini' % RuokuaiBusiness._PLATFORM_CODE)
        rk_biz = RuokuaiBusiness(db=self.db, config=config)
        start_time = datetime.datetime.now()
        result = rk_biz.passcode_identify(params['params']['content'],
                config['image_type'])
        end_time =  datetime.datetime.now()

        # 记录打码结果
        id = rk_biz.insert_record(params, result, start_time, end_time,
                self.request.remote_ip)
        
        context = rk_biz.parse_result(id, result)

        # 返回成功
        if context:
            self.write(cjson.encode(context))
        else:
            # 默认返回错误
            self.write(cjson.encode(
                self._error_page('10000')))
