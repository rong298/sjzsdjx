#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2014年11月4日

@author: TangMing
'''
import os

import tornado.ioloop

class MainProcessorChecker(object):
    def __init__(self):
        def _test_task():
            # print os.getpid(), os.getppid()
            if 1==os.getppid(): # 若主进程退出，则关闭子进程
                exit(0)
        self._timer_task = \
        tornado.ioloop.PeriodicCallback(_test_task, 10000) # 10秒检查一次

    def start(self):
        self._timer_task.start()

    def stop(self):
        self._timer_task.stop()
