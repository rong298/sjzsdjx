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

import re
import urllib
import logging
import datetime
import traceback

import cjson
import requests
from configobj import ConfigObj

from base_biz import BaseBusiness

class Dama2Business(BaseBusiness):

    _PLATFORM_CODE = 'dama2'

    def passcode_identify(self, image_content, image_type=287):
        config = self.config
        body_data = {'file_type': str(image_type), 'content': image_content}
        
        # logging.debug(body_data)
        logging.debug(config['adepter_url'])

        response = requests.post(config['adepter_url'], data=body_data)
        logging.info('Result: %s' % response.text)
        return response.text

    def insert_record(self, params, result, start_time, end_time, remote_ip):
        try:
            result_json = cjson.decode(result)
        except:
            result_json = {'id':None}
        record = {
                'seller_platform': params['params']['seller_platform'],
                'seller': params['params']['seller'],
                'dama_platform': self._PLATFORM_CODE,
                'dama_token_key': '' if 'id' not in result_json else result_json['id'],
                'dama_account': '',
                'status': 1,
                'server_address': self.get_local_ip('eth1'),
                'query_address': remote_ip,
                'start_time': str(start_time),
                'end_time': str(end_time),
                'result': result,
                'created': str(datetime.datetime.now())
                }

        sql = ("INSERT INTO `pass_code_records`"
                " (`%s`) "
                " VALUES "
                " ('%s') "
                ) % (
                        "`, `".join(map(self.any_to_str, record.keys())),
                        "', '".join(map(self.any_to_str, record.values()))
                        )
        id = self.db.execute_lastrowid(sql)
        return id

    def parse_result(self, id, result):
        result = cjson.decode(result)
        if ('id' not in result or not result['id'] 
                or 'result' not in result):
            self.report_error(id, '3')
            return False
        
        code = result['result'].replace('|', ',')
        if not re.match("^\d[\d,\|]+\d$", code):
            self.report_error(id, '4')
            return False
        logging.debug(code)
        # if (code.isdigit() and len(code)<8 and
        #         '9' not in code and '0' not in code):

        #     result = []
        #     for p in str(code):
        #         result.append(random.choice(self._CODE_POSITION[p]))

        #     # 返回适配好的打码结果
        return {
                'status': 'true',
                'data': {
                    'query_id': str(id),    #数据库自增ID
                    'dama_platform': Dama2Business._PLATFORM_CODE, #打码平台标示
                    'pass_code': code,    #验证码坐标    
                    }
                }
    
    def report_error(self, id, status='5'):
        ''' 记录打码错误
        状态枚举
        1 正常
        2 500
        3 平台返回失败
        4 内部判断胡填
        5 前端汇报失败
        '''
        sql = (" UPDATE `pass_code_records` "
            " SET `status`=%s, `notice_status`=%s WHERE `id`=%s "
            ) % (str(status),
                '1' if status in [4, '4'] else '0',
                id)
        affected = self.db.execute_rowcount(sql)
        logging.warn('[%s] Report Error id:%s row[%s]' % ( self._PLATFORM_CODE,
            id, affected))
        return affected

   
