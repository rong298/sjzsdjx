#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jacky'

from base_biz import BaseBusiness
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
            logging.info('[IMAGE][%s],Image have result:%s',image_search_key, image['result'])
            if image['flag'] != 1:
                affect = self.db.execute_rowcount(
                    "UPDATE `pass_code` SET result='',status=1,flag=1 WHERE search_key=%s", image_search_key
                )
            else:
                return image
        else:
            # 图片不存在,首先写入本地文件
            logging.info('[IMAGE][%s],Image no have result',image_search_key)
            root_abspath = self.app_config['root_abspath']
            file_path = ('%s/static/passcode_file/%s' % (root_abspath, image_search_key))

            with open(file_path, 'wb') as image_file:
                image_file.write(base64.b64decode(image_content))

            # 插入数据库
            affect = self.db.execute_rowcount(
                "INSERT INTO `pass_code` (`search_key`, `file_path`, `created`) VALUES (%s, %s, NOW())",
                image_search_key, file_path
            )

        loop_times = 0
        logging.info('[RESULT][%s]:%s', image_search_key, affect)
        while affect:
            loop_times = loop_times + 1
            image = self.db.get(
                "SELECT * FROM `pass_code` WHERE search_key=%s", image_search_key
            )

            logging.debug('[LOOP][%s][%s] ===> %s', image_search_key, loop_times, image['result'])

            if image['status'] != 3:
                time.sleep(2)
                continue

            if image and image['result']:
                return image

            if loop_times > max_loops:
                break
            time.sleep(1)

        logging.debug('[RESULT][%s] ===> FAIL', image_search_key)
        return dict()

    def query_record(self, params, remote_ip, start_time):

        record = {
                'seller_platform': params['params']['seller_platform'],
                'seller': params['params']['seller'],
                'dama_platform': self._PLATFORM_CODE,
                'dama_token_key': '',
                'dama_account': '',
                'status': 1,
                'start_time': start_time,
                'end_time': start_time,
                'server_address': self.get_local_ip('eth1'),
                'query_address': remote_ip,
                'result': '',
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

    def response_record(self, id, start_time, end_time, result):
        logging.debug('[RESPONSE_RECORD][%s]:%s', id, result)

        self.db.execute_rowcount(
            "UPDATE `pass_code_records` SET `start_time`=%s,`end_time`=%s,`dama_token_key`=%s WHERE id=%s",
            str(start_time),
            str(end_time),
            '' if not result.has_key('search_key') else result['search_key'],
            id
        )

    def parse_result(self, id, result):

        logging.info('[RESULT]:%s', result)

        if 'result' not in result:
            self.report_error(id, 3)
            return False

        response = []
        code_position = BaseBusiness._CODE_POSITION
        for p in result['result']:
            if code_position[p]:
                response.append(random.choice(code_position[p]))
            else:
                self.report_error(id, 4)
                return False

        logging.debug("==CODE==>%s", response)
        ret = {
                'status': 'true',
                'data': {
                    'query_id': id,
                    'dama_platform': self._PLATFORM_CODE,
                    'pass_code': ','.join(response)
                    }
                }
        return ret

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
        logging.warn('[%s] Report Error id:%s row[%s][%s]' % ( self._PLATFORM_CODE,
            id, affected, status))
        return affected





