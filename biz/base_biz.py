#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Create on 2014-08-12

@author zhoulh
'''

import os
import sys


import socket
import fcntl
import struct 
import logging
import traceback

import cjson

class BaseBusiness(object):

    def __init__(self, **kargs):
        self.db = kargs.get('db', None)
        self.config = kargs.get('config', None)

    def get_local_ip(self, ifname): 
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        inet = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15])) 
        ret = socket.inet_ntoa(inet[20:24]) 
        return ret

    def any_to_str(self, value):            
        if not isinstance(value, unicode):
            return str(value)
        return value

