#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jacky'

from handler.base_handler import OpBaseHandler
from biz.base_biz import BaseBusiness
from biz.op_biz import OpBusiness
from biz.yundama_biz import YunDamaBusiness
from biz.dama2_biz import Dama2Business
from biz.ruokuai_biz import RuokuaiBusiness
import cjson
import tornado
import logging

class OpLoginHandler(OpBaseHandler):
    '''
    控制平台登录
    '''
    def _do_get(self):
        errmsg = self.get_argument('errmsg', '')
        self.render(
            'op_login.html',
            errmsg=errmsg
            )
        return

class OpLogoutHandler(OpBaseHandler):
    def _do_get(self):
        self.clear_cookie('op_server_seller')
        self.redirect('/op/login')
        return

class OpLoginProcessHandler(OpBaseHandler):
    '''
    控制平台登录,提交
    '''
    def _do_post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')

        if password != 'yur140608':
            self.redirect('/op/login?errmsg=账号密码错误')
            return

        if username == 'yunhu':
            seller = 'yh'
        elif username == 'duhang':
            seller = 'dh'
        elif username == 'common':
            seller = 'common'
        else:
            self.redirect('/op/login?errmsg=账号密码错误')
            return

        self.set_cookie('op_server_seller', seller)
        self.redirect('/op/platform_view')
        return

class OpPlatformViewHandler(OpBaseHandler):
    '''
    打码平台配置查看
    '''
    @tornado.web.authenticated
    def _do_get(self):
        # 错误统计数据来源
        config = self.config
        op_config = config['op']
        monitor_term = op_config['monitor_term']
        op_biz = OpBusiness(db=self.db)
        errmsg = self.get_argument('errmsg',None)
        flag = self.get_argument('flag',None)
        seller = self.get_cookie('op_server_seller')

        # 余额信息查询
        #balance = self.redis.get(BaseBusiness.REDIS_KEY_TOTAL)
        #balance = cjson.decode(balance)
        #balance = balance.get(seller)

        # 当前打码平台配置
        platforms = op_biz.get_all_platform(seller)

        self.render(
            'platform_view.html',
            status_dict = self.status_dict,
            platforms = platforms,
            errmsg = errmsg,
            flag = flag,
            current_user = seller,
            seller = seller
            #balance = balance
        )

class OpRunningMonitorHandler(OpBaseHandler):
    status_dict = {
        '1' : u'成功',
        '2' : u'打码平台服务器异常',
        '3' : u'打码平台返回数据异常',
        '4' : u'打码平台数据胡填',
        '5' : u'前端验证错误',
    }

    @tornado.web.authenticated
    def _do_get(self):
        config = self.config
        op_config = config['op']
        monitor_term = op_config['monitor_term']
        op_biz = OpBusiness(db=self.db)
        seller = self.get_cookie('op_server_seller')

        # 获取数据
        monitor_data = op_biz.normal_monitor(seller=seller, term=monitor_term)

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

        # 余额信息查询
        balance = self.redis.get(BaseBusiness.REDIS_KEY_TOTAL)
        if balance:
            balance = cjson.decode(balance)
            balance = balance.get(seller)
        else:
            balance = {}

        logging.debug('[OP][NormalMonitor]%s', monitor_data)
        logging.info('[OP][Balance]%s', balance)
        self.render('running_monitor.html',
                    items = monitor_data,
                    monitor_term = monitor_term,
                    ratio = ratio,
                    status_dict = self.status_dict,
                    balance = balance,
                    current_user = seller,
                    seller = seller
                    )
        return

    pass

class OpPlatformChangeHandler(OpBaseHandler):
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



class OpMonitorHandler(OpBaseHandler):
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


class OpBalanceHandler(OpBaseHandler):
    '''
    财务信息
    '''

    def _do_get(self):
        pass



