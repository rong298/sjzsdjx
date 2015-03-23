#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Create on 2014-08-12

@author zhoulh
'''

import os

import sys

import logging
import traceback

import cjson
import tornado.web
import hashlib
from configobj import ConfigObj

class BaseHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    @property
    def proxies(self):
        return self.application.proxies

    def get(self):
        self._do_get()

    def _do_get(self):
        ''' get方法
        需要子类实现
        '''
        return

    def post(self):
        self._do_post()

    def _do_post(self):
        ''' post方法
        默认的post操作
        若有特殊需求，则子类自行实现
        '''
        params = self.get_argument('params', strip=True, default=None)
        if params:
            try:
                params = cjson.decode(params)
                if params['method'] == 'query_dama':
                    self._do_query_dama(params)
                elif params['method'] == 'error_notice':
                    self._do_error_notice(params)
            except Exception as e:
                logging.error(traceback.format_exc())

                self.write(cjson.encode(self._error_page('10002')))
                return
        else:
            self.write(cjson.encode(
                self._error_page('10001')))
            return

    def _do_error_notice(self, params):
        sql = (" UPDATE `pass_code_records` "
            " SET `status`=5 WHERE `id`=%s "
            ) % (params['params']['query_id'])
        affected = self.db.execute_rowcount(sql)
        logging.warn('[Self Frontend] Report Error id:%s row[%s]' % ( 
            params['params']['query_id'], affected))

        if affected==1:
            self.write(cjson.encode({'status': 'true', 'data': '1'}))
        else:
            self.write(cjson.encode({'status': 'false', 'data': '0'}))


    _ERROR_CODE={
            '10000': u'打码错误',
            '10001': u'params获取失败',
            '10002': u'服务器异常',
            '10003': u'配置错误',
            }

    def _error_page(self, code, message=''):
        result = {
                'status': 'false',
                'error': {
                    'code': code,
                    'message':  message
                    }
                }
        if message:
            result['error']['message'] = message
        elif code in self._ERROR_CODE:
            result['error']['message'] = self._ERROR_CODE[code]
        else:
            result['error']['message'] = '未知的错误码'
        return result

    def _fail_out(self, code):
        self.write(cjson.encode(self._error_page(str(code))))

    def _succ_out(self, content):
        result = {
            "status": "true",
            "data": content
        }
        self.write(cjson.encode(result))

    def _load_config(self, file_name):
        config = ConfigObj( 
            self.application.settings['root_abspath'] + file_name, encoding='UTF8')
        return config

    def _md5(self, src):
        myMd5 = hashlib.md5()
        myMd5.update(src)
        myMd5_Digest = myMd5.hexdigest()
        return myMd5_Digest

