#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import cjson
import datetime
import logging
import traceback
from biz.manul_biz import ManulBusiness

from base_handler import BaseHandler

class ManulHandler(BaseHandler):
    
    def _do_query_dama(self, params):
        config = self._load_config('/config/%s.ini' % ManulBusiness._PLATFORM_CODE)
        manul_biz = ManulBusiness(db=self.db, config=config, app_config=self.application.settings)
        start_time = datetime.datetime.now()
        result = manul_biz.passcode_identify(params['params']['content'],
                config['image_type'])
        end_time =  datetime.datetime.now()

        # 记录打码结果
        id = manul_biz.insert_record(params, result, start_time, end_time,
                self.request.remote_ip)
        
        context = manul_biz.parse_result(id, result)

        # 返回成功
        if context:
            self.write(cjson.encode(context))
        else:
            # 默认返回错误
            self.write(cjson.encode(
                self._error_page('10000')))
