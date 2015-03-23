#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jacky'
from base64 import b64encode, b64decode
import configobj as ConfigObj
import redis
import os, sys

ABS_ROOT_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

class Redis(object):

    @staticmethod
    def set(self, key, value, timeout=600):
        config = ConfigObj(ABS_ROOT_PATH+ '/config/config_online.ini', encoding='UTF8')

        redis_handler = redis.Redis(**config['redis'])

        expire = timeout
        self.redis.set(key, value)
        self.redis.expire(key, expire)

