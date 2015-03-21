#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jacky'

from base_biz import BaseBusiness
import main_server
import base64
import time
import cjson
import datetime
import re
import logging
import random



class ManulBusiness(BaseBusiness):

    _PLATFORM_CODE = 'manul'

    def passcode_identify(self, image_content, image_type=0):
        # 图片标的
        image_search_key = self._md5(image_content)
        max_loops = self.config['timeout']

        # 将图片存入本地
        image = self.db.get(
            "SELECT * FROM `pass_code` WHERE search_key=%s", image_search_key
        )

        affect = 0
        # 如果图片已经存在
        if image and image['result']:
            if image['flag'] != 1:
                affect = self.db.execute_rowcount(
                    "UPDATE `pass_code` SET result='',status=1,flag=1 WHERE search_key=%s", image_search_key
                )
            else:
                return image['result']

        else:
            # 图片不存在,首先写入本地文件
            root_abspath = self.app_config['root_abspath']
            file_path = ('%s/static/passcode_file/%s' % (root_abspath, image_search_key))

            with open(file_path, 'wb') as image_file:
                image_file.write(base64.b64decode(image_content))

            # 插入数据库
            affect = self.db.execute_rowcount(
                "INSERT IGNORE INTO `pass_code` (`search_key`, `file_path`, `created`) VALUES (%s, %s, NOW())",
                image_search_key, file_path
            )

        loop_times = 0
        while affect:
            image = self.db.get(
                "SELECT * FROM `pass_code` WHERE search_key=%s AND status=1", image_search_key
            )

            if image and image['result']:
                return image['result']

            if loop_times > max_loops:
                break
            time.sleep(1)
            loop_times = loop_times + 1

        return False

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

    def parse_result(self, id, hit_numbers):
        result = []
        code_position = BaseBusiness._CODE_POSITION
        for p in hit_numbers:
            result.append(random.choice(code_position[p]))

        logging.debug("==CODE==>%s", result)
        ret = {
                'status': 'true',
                'data': {
                    'query_id': id,
                    'dama_platform': self._PLATFORM_CODE,
                    'pass_code': ','.join(result)
                    }
                }
        return ret






