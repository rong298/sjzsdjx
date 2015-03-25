#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jacky'

from handler.base_handler import BaseHandler
from biz.base_biz import BaseBusiness
from biz.op_biz import OpBusiness
from biz.yundama_biz import YunDamaBusiness
from biz.dama2_biz import Dama2Business
from biz.ruokuai_biz import RuokuaiBusiness

import logging

class OpLoginHandler(BaseHandler):
    '''
    控制平台登录
    '''
    pass

class OpLoginProcessHandler(BaseHandler):
    '''
    控制平台登录,提交
    '''
    pass

class OpPlatformViewHandler(BaseHandler):
    '''
    打码平台配置查看
    '''

    def _do_get(self):
        config = self.config
        op_config = config['op']
        monitor_term = op_config['monitor_term']
        op_biz = OpBusiness(db=self.db)
        monitor_data = op_biz.normal_monitor(monitor_term)

    pass

class OpPlatformChangeHandler(BaseHandler):
    '''
    打码平台配置修改
    '''
    pass

class OpMonitorHandler(BaseHandler):
    '''
    打码平台监控页面
    '''

    def _do_get(self):
        config = self.config
        op_config = config['op']
        monitor_term = op_config['monitor_term']
        op_biz = OpBusiness(db=self.db)

        # 获取数据
        monitor_data = op_biz.normal_monitor(monitor_term)
        logging.debug('[OP][NormalMonitor]%s', monitor_data)
        self.render('normal_monitor.html',
                    items = monitor_data,
                    monitor_term = monitor_term
                    )
        return


class OpBalanceHandler(BaseHandler):
    '''
    财务信息
    '''

    def _do_get(self):
        pass



