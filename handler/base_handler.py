#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Create on 2014-08-12

@author zhoulh
'''

import os
import sys

import cjson
import logging
import traceback

import tornado.web

class BaseHandler(tornado.web.RequestHandler):

    _CODE_POSITION = {'1': ['37,45','33,42','43,47','38,44'],
            '2': ['109,49','111,34','108,43','101,46'], 
            '3': ['199,45','169,41','190,39','180,41'], 
            '4': ['255,43','258,39','265,34','257,43'], 
            '5': ['41,114','41,112','38,110','44,113'], 
            '6': ['112,124','126,110','117,118','110,123'], 
            '7': ['186,119','171,115','192,118','191,118'], 
            '8': ['257,109','253,116','242,107','265,122']} 
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
            '10000': '打码错误',
            '10001': 'params获取失败',
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
        elif code in _ERROR_CODE:
            result['error']['message'] = _ERROR_CODE[code]
        else:
            result['error']['message'] = '未知的错误码'
        return result
