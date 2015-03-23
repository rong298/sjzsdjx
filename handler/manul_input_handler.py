#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import cjson
import datetime
import logging
import uuid
import traceback
from lib.redis_lib import Redis
from biz.manul_biz import ManulBusiness
from base_handler import BaseHandler


class ManulLoginHandler(BaseHandler):
    def get(self):
        self.render('manul_input_login.html')
        return

class ManulLoginProcessHandler(BaseHandler):
    def get(self):
        # 不是登录状态
        user_name = self.get_argument('user_name', strip=True, default=None)
        if not user_name:
            self.redirect('/manul_dama/login')
        else:
            self.set_cookie('user_name', user_name+'_'+str(uuid.uuid1()))
            user_name = self.get_cookie('user_name')
            self.redirect('/manul_dama/search')
        return

class ManulSearchHandler(BaseHandler):

    def get(self):
        if self.check_login():
            self.redirect('/manul_dama/login')
            return
        # 计算总计
        user_name = self.get_cookie('user_name')
        total = self.db.get("SELECT count(*) as total FROM `pass_code` WHERE status=1")
        total = total['total']

        # 优先输入已锁定的验证码
        if self.search_in_checked(user_name, total):
            return

        # 选中一张图片锁定后输出
        if self.search_in_all(user_name, total):
            return

    def search_in_checked(self, user_name, total):
        item = self.db.get(
            "SELECT * FROM `pass_code` WHERE status=2 AND `operator` in ('%s', '') ORDER BY `created` ASC LIMIT 1",
            user_name
        )

        # 如果有图片
        if item:
            redis_key = item['file_path']
            imaget_content = Redis.get(redis_key)

            self.render('manul_search.html',
                        item=item,
                        total = total,
                        active='manual_passcode',
                        user=user_name,
                        imaget_content=imaget_content,
                        navi=u"")
            return True

        return False

    def search_in_all(self, user_name, total):
        items = self.db.query("SELECT * FROM `pass_code` WHERE status=1 ORDER BY `created` ASC")

        for item in items:
            affect = self.db.execute_rowcount(
                "UPDATE `pass_code` SET status=2,operator=%s WHERE id=%s",
                user_name,
                item['id']
            )

            # 锁定
            if affect:
                redis_key = item['file_path']
                imaget_content = Redis.get(redis_key)

                self.render('manul_search.html',
                            item = item,
                            total = total,
                            active = 'manual_passcode',
                            user = user_name,
                            imaget_content = imaget_content,
                            navi = u"")

                return True

        return False

class ManulInputHandler(BaseHandler):

    def post(self):
        if self.check_login():
            self.redirect('/manul_dama/login')
            return

        value = self.get_argument('pass_code_value', default=None)
        search_key = self.get_argument('search_key', default=None)
        user_name = self.get_cookie('user_name')

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

        self.render('/manul_dama/search')
        return

