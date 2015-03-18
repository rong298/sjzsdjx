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

from handler import BaseHandler

class RuokuaiHandler(BaseHandler):
    
    def post(self):
        params = self.get_argument('params', strip=True, default=None)

        if params:
            try:
                params = cjson(params)
            except Exception as e:
                logging.error(traceback.fo)
        else:
            self._error_page('10001')
            return
