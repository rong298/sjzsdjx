#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import cjson
import datetime
import logging
import uuid
import traceback
import base64


from biz.manul_biz import ManulBusiness
from base_handler import BaseHandler


class ManulLoginHandler(BaseHandler):
    def get(self):
        msg = self.get_argument('msg', None)
        self.render('manul_input_login.html', msg=msg)
        return

class ManulLoginProcessHandler(BaseHandler):
    def get(self):
        # 不是登录状态
        user_name = self.get_argument('user_name', strip=True, default=None)
        work_code = self.get_argument('token', strip=True, default='')

        logging.debug('[LoginProcess]%s,%s', user_name, work_code)
        if work_code.lower() != 'all':
            try:
                base64.b64decode(work_code)
            except:
                self.redirect('/manul_dama/login?msg=token错误')
                return
        else:
            work_code = base64.b64encode('all')

        if not user_name:
            self.redirect('/manul_dama/login')
        else:
            self.set_cookie('user_name', user_name+'_'+str(uuid.uuid1()))
            self.set_cookie('token', work_code)
            user_name = self.get_cookie('user_name')
            self.redirect('/manul_dama/search')
        return

class ManulSearchHandler(BaseHandler):

    def get(self):
        if not self.check_login():
            self.redirect('/manul_dama/login')
            return

        # 设置过滤器
        filter = self.filter_config()
        if not filter:
            self.redirect('/manul_dama/login?msg=登陆信息有误')
            return
        self.filter = filter

        # 计算总计
        total = self.total(filter)

        user_name = self.get_cookie('user_name')

        # 优先输入已锁定的验证码
        item = self.search_in_checked(user_name)

        # 选中一张图片锁定后输出
        if not item:
            item = self.search_in_all(user_name)

        self.parse_render(item, total)
        return


    def parse_render(self, item, total):
        user_name = self.get_cookie('user_name')

        image_content = None
        if isinstance(item, dict):
            redis_key = item.get('file_path', None)
            if redis_key:
                image_content = self.redis_get(redis_key)

        self.render('manul_search.html',
                        item=item,
                        total = total,
                        active='manual_passcode',
                        user=user_name,
                        image_content=image_content,
                        navi=u"")

    def filter_config(self):
        tokens = self.db.query("SELECT `token` FROM `pass_code_config`")
        tt = []
        for t in tokens:
            tt.append(t['token'])
        if len(tt) == 0:
            return False

        codes = self.get_cookie('token')

        if codes:
            try:
                codes = base64.b64decode(codes)
            except:
                return False
            if codes.lower() != 'all':
                tt = codes.split(",")

        return tt


    def do_filter(self, filter, items):
        if not filter:
            return items

        new_items = []
        for it in items:
            if it['dis_code'] in filter:
                new_items.append(it)

        return new_items


    def total(self, filter):
        user_name = self.get_cookie('user_name')
        items = self.db.query("SELECT * FROM `pass_code` WHERE status=1")
        if not filter:
            total = len(items)
        else:
            num = 0
            for it in items:
                if it['dis_code'] in filter:
                    num = num + 1

            total = num
        logging.debug('[%s]Searching...%s', user_name, total)

        return total


    def search_in_checked(self, user_name):
        items = self.db.query(
            "SELECT * FROM `pass_code` WHERE status=2 AND `operator` in (%s, '') ORDER BY `created` ASC",
            user_name
        )

        items = self.do_filter(self.filter, items)
        if not items:
            return False

        return items[0]

    def search_in_all(self, user_name):
        items = self.db.query("SELECT * FROM `pass_code` WHERE status=1 ORDER BY `created` ASC")
        items = self.do_filter(self.filter, items)

        for item in items:
            affect = self.db.execute_rowcount(
                "UPDATE `pass_code` SET status=2,operator=%s WHERE id=%s",
                user_name,
                item['id']
            )

            # 锁定
            if affect:
                return item
        return False

class ManulInputHandler(BaseHandler):

    def post(self):
        if not self.check_login():
            self.redirect('/manul_dama/login')
            return

        value = self.get_argument('passvalue1', default=None)
        search_key = self.get_argument('search_key', default=None)
        user_name = self.get_cookie('user_name')
        logging.debug('[%s][%s][%s]EnterInput...', user_name, value, search_key)

        if not value:
            self.redirect('/manul_dama/search')
            return

        # ToDo 这里可以做输入异常判断

        # 输入更新
        affect = self.db.execute_rowcount(
            "UPDATE `pass_code` SET result=%s,status=3 WHERE search_key=%s",
            value,
            search_key
        )

        self.redirect('/manul_dama/search')
        return

