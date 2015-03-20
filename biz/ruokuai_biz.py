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

import cjson
from configobj import ConfigObj

from lib.api.ruokuai import RClient
from base_biz import BaseBusiness
import base64

class RuokuaiBusiness(BaseBusiness):

    _PLATFORM_CODE = 'ruokuai'

    def passcode_identify(self, image_content, image_type=6113):
        config = self.config

        buffer = base64.b64decode(image_content)
        logging.info("ACCOUNT:%s-%s-%s-%s" % (config['account'],config['code'],str(image_type),config['token']))
        rc = RClient(config['account'], config['password'], config['code'],
                config['token'])
        result = rc.rk_create(buffer, image_type) # 3040 6113 
        logging.info('Result: %s' % result)
        return result

    def insert_record(self, params, result, start_time, end_time, remote_ip):
        record = {
                'seller_platform': params['params']['seller_platform'],
                'seller': params['params']['seller'],
                'dama_platform': self._PLATFORM_CODE,
                'dama_token_key': '' if 'Id' not in result else result['Id'],
                'dama_account': '',
                'status': 1,
                'server_address': self.get_local_ip('eth1'),
                'query_address': remote_ip,
                'start_time': str(start_time),
                'end_time': str(end_time),
                'result': cjson.encode(result),
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
        if 'Error_Code' in result:
            self.report_error(id, '3')
            return False
            
        code = result['Result']
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

        self.report_error(id, '4')
        return False
    
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
                '1' if status in [4, 5, '4', '5'] else '0',
                id)
        affected = self.db.execute_rowcount(sql)
        logging.warn('[%s] Report Error id:%s row[%s]' % ( self._PLATFORM_CODE,
            id, affected))
        return affected

   
