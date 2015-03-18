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
import logging
import traceback

from configobj import ConfigObj

from lib.api.ruokuai import RClient
from base_biz import BaseBusiness
import base64

class RuokuaiBusiness(BaseBusiness):


    _PLATFORM_CODE = 'ruokuai'

    def passcode_identify(self, image_content, image_type=6113):
        config = self.config

        buffer = base64.b64decode(image_content)
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
                'result': cjson.encode(result)
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
        
    def report_error(self, id):
        pass

   
