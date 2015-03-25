#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Create on 2014-08-12

@author zhoulh
'''

import os
import sys
import hashlib


import socket
import fcntl
import struct 
import logging
import traceback

import cjson
import datetime
import requests

class BaseBusiness(object):

    _CODE_POSITION = {'1': ['37,45','33,42','43,47','38,44'],
            '2': ['109,49','111,34','108,43','101,46'], 
            '3': ['199,45','169,41','190,39','180,41'], 
            '4': ['255,43','258,39','265,34','257,43'], 
            '5': ['41,114','41,112','38,110','44,113'], 
            '6': ['112,124','126,110','117,118','110,123'], 
            '7': ['186,119','171,115','192,118','191,118'], 
            '8': ['257,109','253,116','242,107','265,122']}

    MANUL = 'manul'
    DAMA2 = 'dama2'
    RUOKUAI = 'ruokuai'
    YUNDAMA = 'yundama'
    QUNARDAMA = 'qunar_dama'

    def __init__(self, **kargs):
        self.db = kargs.get('db', None)
        self.config = kargs.get('config', None)
        self.app_config = kargs.get('app_config', None)
        self.dis_code = kargs.get('dis_code', None)
        self.order_id = kargs.get('order_id', None)
        self.seller = kargs.get('seller', None)

    def get_local_ip(self, ifname): 
        #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #inet = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))
        #ret = socket.inet_ntoa(inet[20:24])

        ret = '127.0.0.1'
        return ret

    def any_to_str(self, value):            
        if not isinstance(value, unicode):
            return str(value)
        return value

    def _md5(self, src):
        myMd5 = hashlib.md5()
        myMd5.update(src)
        myMd5_Digest = myMd5.hexdigest()
        return myMd5_Digest

    def query_record(self, platform, seller_platform, seller, remote_ip, start_time, order_id, scene):

        record = {
                'seller_platform': seller_platform,
                'seller': seller,
                'dama_platform': platform,
                'dama_token_key': '',
                'dama_account': '',
                'status': 0,
                'order_id': order_id,
                'dis_code': self.dis_code,
                'scene': scene,
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

    def response_record(self, id, dama_token_key, end_time, result, status=1):

        affect = self.db.execute_rowcount(
            "UPDATE `pass_code_records` SET dama_token_key=%s,end_time=%s,result=%s,status=%s WHERE id=%s",
            dama_token_key,
            end_time,
            result,
            status,
            id
        )

        return affect

    def error_record(self, id, status, notice_status=0):
        affect = self.db.execute_rowcount(
            "UPDATE `pass_code_records` SET status=%s,notice_status=%s,end_time=%s WHERE id=%s",
            status,
            notice_status,
            str(datetime.datetime.now()),
            id
        )

        return affect

    def get_pic(self):
        url = 'https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=login&rand=sjrand&0.289653001120314'
        r = requests.get(url, verify=False)
        return r.content

