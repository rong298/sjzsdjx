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
        # 错误统计数据来源
        config = self.config
        op_config = config['op']
        monitor_term = op_config['monitor_term']
        op_biz = OpBusiness(db=self.db)
        errmsg = self.get_argument('errmsg',None)
        flag = self.get_argument('flag',None)

        # 获取数据
        monitor_data = op_biz.normal_monitor(monitor_term)

        ratio = {}
        for it in monitor_data:
            da = it['dama_platform']
            status = int(it['status'])
            count = it['count']
            if not ratio.has_key(da):
                ratio[da] = {'succ': 0, 'fail': 0}

            if status == 1:
                ratio[da]['succ'] = count
            else:
                ratio[da]['fail'] += count

        logging.debug('[OP][NormalMonitor]%s', monitor_data)

        # 当前打码平台配置
        platforms = op_biz.get_all_platform()

        self.render(
            'platform_view.html',
            items = monitor_data,
            monitor_term = monitor_term,
            ratio = ratio,
            status_dict = self.status_dict,
            platforms = platforms,
            errmsg = errmsg,
            flag = flag
        )

class OpRunningMonitorHandler(BaseHandler):
    status_dict = {
        '1' : u'成功',
        '2' : u'打码平台服务器异常',
        '3' : u'打码平台返回数据异常',
        '4' : u'打码平台数据胡填',
        '5' : u'前端验证错误',
    }

    def _do_get(self):
        config = self.config
        op_config = config['op']
        monitor_term = op_config['monitor_term']
        op_biz = OpBusiness(db=self.db)

        # 获取数据
        monitor_data = op_biz.normal_monitor(monitor_term)

        ratio = {}
        for it in monitor_data:
            da = it['dama_platform']
            status = int(it['status'])
            count = it['count']
            if not ratio.has_key(da):
                ratio[da] = {'succ': 0, 'fail': 0}

            if status == 1:
                ratio[da]['succ'] = count
            else:
                ratio[da]['fail'] += count

        # ToDo 余额信息查询


        logging.debug('[OP][NormalMonitor]%s', monitor_data)
        self.render('running_monitor.html',
                    items = monitor_data,
                    monitor_term = monitor_term,
                    ratio = ratio,
                    status_dict = self.status_dict
                    )
        return

    pass

class OpPlatformChangeHandler(BaseHandler):
    '''
    打码平台配置修改
    '''

    def _do_post(self):
        print self.request.arguments
        seller_platform = self.get_arguments('seller_platform',None)
        seller = self.get_arguments('seller',None)
        dama_platform = self.get_argument('dama_platform',None)
        scene = self.get_arguments('scene',None)

        if not (seller_platform and seller and dama_platform and scene):
            logging.error('[Change Platform]Fail, Params Error')
            self.redirect('/op/platform_view/?errmsg=参数错误,请认真核对,重试无果请联系技术')
            return

        flag = OpBusiness(db=self.db).change_platform(seller_platform, seller, scene, dama_platform)

        if flag:
            self.redirect('/op/platform_view/?flag=true')
        else:
            self.redirect('/op/platform_view/?errmsg=更新失败,请联系技术')

        return



class OpMonitorHandler(BaseHandler):
    '''
    打码平台监控页面
    '''

    status_dict = {
        '1' : u'成功',
        '2' : u'打码平台服务器异常',
        '3' : u'打码平台返回数据异常',
        '4' : u'打码平台数据胡填',
        '5' : u'前端验证错误',
    }

    def _do_get(self):
        config = self.config
        op_config = config['op']
        monitor_term = op_config['monitor_term']
        op_biz = OpBusiness(db=self.db)

        # 获取数据
        monitor_data = op_biz.normal_monitor(monitor_term)

        ratio = {}
        for it in monitor_data:
            da = it['dama_platform']
            status = int(it['status'])
            count = it['count']
            if not ratio.has_key(da):
                ratio[da] = {'succ': 0, 'fail': 0}

            if status == 1:
                ratio[da]['succ'] = count
            else:
                ratio[da]['fail'] += count


        logging.debug('[OP][NormalMonitor]%s', monitor_data)
        self.render('normal_monitor.html',
                    items = monitor_data,
                    monitor_term = monitor_term,
                    ratio = ratio,
                    status_dict = self.status_dict
                    )
        return


class OpBalanceHandler(BaseHandler):
    '''
    财务信息
    '''

    def _do_get(self):
        pass



