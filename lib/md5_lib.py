#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jacky'

import hashlib
import datetime
import random

class MD5(object):

    @staticmethod
    def create(src):
        myMd5 = hashlib.md5()
        myMd5.update(src)
        myMd5_Digest = myMd5.hexdigest()
        return myMd5_Digest

    @staticmethod
    def random_md5():
        str1 = str(datetime.datetime.now())
        str2 = str(random.uniform(10,20))

        src = str1 + str2
        myMd5 = hashlib.md5()
        myMd5.update(src)
        myMd5_Digest = myMd5.hexdigest()
        return myMd5_Digest

