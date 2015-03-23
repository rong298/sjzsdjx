#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jacky'

import hashlib

class MD5(object):

    @staticmethod
    def create(src):
        myMd5 = hashlib.md5()
        myMd5.update(src)
        myMd5_Digest = myMd5.hexdigest()
        return myMd5_Digest