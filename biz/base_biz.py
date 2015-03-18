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

    _CODE_POSITION = {'1': ['37,45','33,42','43,47','38,44'],
            '2': ['109,49','111,34','108,43','101,46'], 
            '3': ['199,45','169,41','190,39','180,41'], 
            '4': ['255,43','258,39','265,34','257,43'], 
            '5': ['41,114','41,112','38,110','44,113'], 
            '6': ['112,124','126,110','117,118','110,123'], 
            '7': ['186,119','171,115','192,118','191,118'], 
            '8': ['257,109','253,116','242,107','265,122']} 

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

