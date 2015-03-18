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
    
    def post(self):
        params = self.get_argument('params', strip=True, default=None)
	config = self._load_config()
        if params:
            try:
                rk_biz = RuokuaiBusiness(db=self.db, config=config)
                params = cjson.decode(params)
                if params['method'] == 'query_dama':
                    
                    start_time = datetime.datetime.now()
                    result = rk_biz.passcode_identify(params['params']['content'],
                            6113) # TODO params['params']['image_type']
                    end_time =  datetime.datetime.now()

                    # 记录打码结果
                    id = rk_biz.insert_record(params, result, start_time, end_time,
                            self.request.remote_ip)
                    
                    context = self._parse_result(id, result)
                    self.write(cjson.encode(context))
                    return


            except Exception as e:
                logging.error(traceback.format_exc())
        else:
            self.write(cjson.encode(
                self._error_page('10001')))
            return

    def _parse_result(self, id, result):
        if 'Error_Code' in result:
            # TODO 直接向打码平台报错
            # TODO  记录错误打码结果
            return self._error_page('10000')
            
        code = response.json()['Result']
        logging.debug(code)
        if (code.isdigit() and len(code)<8 and
                '9' not in code and '0' not in code):

            result = []
            for p in str(code):
                result.append(random.choice(self._CODE_POSITION[p]))

            # 返回适配好的打码结果
            return {
                    'status': 'true',
                    'data': {
                        'query_id': str(id),    #数据库自增ID
                        'dama_platform': RuokuaiBusiness._PLATFORM_CODE, #打码平台标示
                        'pass_code': ','.join(result),    #验证码坐标    
                        }
                    }
        # TODO 直接向打码平台报错
        # TODO  记录错误打码结果
        return self._error_page('10000')

    def _load_config(self, file_name='/config/ruokuai.ini'):
        config = ConfigObj( 
            self.application.settings['root_abspath'] + file_name, encoding='UTF8')
        return config



