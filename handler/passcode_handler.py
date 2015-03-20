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
import os
import sys
import csv
import time
import json
import uuid
import utils
import codecs
import logging
import urllib
import random
import requests
import datetime
import traceback
import tornado.web
import base64
from lib import database
from configobj import ConfigObj

from biz.base_biz import BaseBusiness
import cjson

from MySQLdb import IntegrityError
from lxml import etree

from base_handler import BaseHandler

class ManualPasscodeHandler(BaseHandler):
    
    def get(self):
        user_name = self.get_cookie('user_name')
        if not user_name: # 没有cookie
            user_name = self.get_argument('user_name', strip=True, default=None)
            if not user_name: # 没有输入用户名
                self.render("manual_passcode_user.html")
                return
            else:
                self.set_cookie('user_name', user_name+'_'+str(uuid.uuid1()))
                user_name = self.get_cookie('user_name')

        search_key = self.get_argument('search_key', strip=True, default=None)
        passvalue1 = self.get_argument('passvalue1', strip=True, default=None)
        # passvalue2 = self.get_argument('passvalue2', strip=True, default=None)
        if search_key and passvalue1:
            affected = self.db.execute(
                    "UPDATE `pass_code` SET `status`=3, `result`='%s', `operator`='%s' WHERE `search_key`='%s'" % (
                        passvalue1, user_name, search_key)
                    )
            self.redirect('/admin/manual_passcode')
            return

        total = self.db.get("SELECT count(*) as total FROM `pass_code` WHERE status=1")

        # 优先输入已锁定的验证码
        items = self.db.query("SELECT * FROM `pass_code` WHERE status=2 AND `operator` in ('%s', '') ORDER BY `created` ASC LIMIT 20"
                % user_name)
        if items:
            self.render("manual_passcode.html", item=items[0],
                    total = total['total'],
                    active='manual_passcode', user=user_name, navi=u"")
            return
        
        # 从未锁定的记录中选择
        items = self.db.query("SELECT * FROM `pass_code` WHERE status=1 ORDER BY `created` ASC")

        logging.debug(items)

        if not items:
            self.render("manual_passcode.html", item={'search_key':''},
                    total = total['total'],
                    active='manual_passcode', user=user_name, navi=u"")
            return
        for item in items:
            affected = self.db.execute_rowcount("UPDATE `pass_code` SET status=2, operator='%s' WHERE `id`=%s"
                    % (user_name, item['id']))
            logging.debug(affected)
            if affected==1:
                logging.debug(item)
                self.render("manual_passcode.html", item=item,
                        total = total['total'],
                        active='manual_passcode', user=user_name, navi=u"")
                return


    # def post(self):
    def _do_query_dama(self, params):
        root_abspath = os.path.dirname(
                os.path.abspath(sys.argv[0]))

        config = ConfigObj(root_abspath + '/config/config_online.ini',
                encoding='UTF8')
        local_db = database.Connection(**config['mysql'])
        #search_key = self.get_argument('file_name', strip=True)
        #image_content = self.get_argument('file_data', strip=True, default=None)

        # 参数解析
        seller_platform = params['seller_platform']
        seller = params['seller']
        content = params['content']
        image_type = params['image_type']
        search_key = self._md5(content)

        result = local_db.get("SELECT * FROM `pass_code` WHERE `search_key`='%s'" % search_key)

        if result and result['result'] and result['flag'] == 1:
            self.write(result['result'])
            return
        if content:
            file_path = ('%s/runtime' % root_abspath, search_key)
            with open(file_path, 'wb') as image_file:
                image_file.write(base64.b64decode(content))

        sql = ("INSERT IGNORE INTO `pass_code` "
            " (`search_key`, `file_path`, `created`) "
            " VALUES "
            " ('%s', '%s', NOW()) "
            ) % (search_key, file_path)
        
        affect = local_db.execute_rowcount(sql)

        loop_times = 0
        result = []
        flag = True
        code_position = BaseBusiness._CODE_POSITION
        while affect:
            loop_times = loop_times + 1
            if loop_times > 20:
                break

            ret = local_db.get(
                "SELECT * FROM `pass_code` WHERE search_key=%s LIMIT 1", search_key
            )

            if ret['result']:
                hit_numbers = ret['result']

                for p in hit_numbers:
                    if p in code_position:
                        result.append(code_position[p])
                    else:
                        # self.write(cjson.encode(self._error_page('10000')))
                        local_db.execute_rowcount(
                            "UPDATE `pass_code` SET flag=2 WHERE search_key=%s LIMIT 1", search_key
                        )
                        flag = False
                        break
                break
            time.sleep(1)

        if flag:
            # 成功
            codes = ",".join(result)
            ret = {
                'status': 'true',
                'data': {
                    'query_id': '100',
                    'dama_platform': 'manul',
                    'pass_code': codes
                }
            }

            self.write(cjson.encode(ret))
        else:
            self.write(cjson.encode(self._error_page('10000')))

        local_db.close()
        return

