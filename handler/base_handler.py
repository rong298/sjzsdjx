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
        需要子类实现
        '''
        return

    _ERROR_CODE={
            '10000': u'打码错误',
            '10001': u'params获取失败',
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

    def _load_config(self, file_name):
        config = ConfigObj( 
            self.application.settings['root_abspath'] + file_name, encoding='UTF8')
        return config

