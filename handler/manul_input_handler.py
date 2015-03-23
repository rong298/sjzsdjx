#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import cjson
import datetime
import logging
import uuid
import traceback
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
        if not self.check_login():
            self.redirect('/manul_dama/login')
            return
        # 计算总计
        user_name = self.get_cookie('user_name')
        total = self.db.get("SELECT count(*) as total FROM `pass_code` WHERE status=1")
        total = total['total']
        logging.debug('[%s]Searching...%s', user_name, total)

        # 优先输入已锁定的验证码
        if self.search_in_checked(user_name, total):
            return

        # 选中一张图片锁定后输出
        if self.search_in_all(user_name, total):
            return

        # 啥也没有，输出空白图
        self.search_in_black(user_name, total)

    def search_in_checked(self, user_name, total):
        item = self.db.get(
            "SELECT * FROM `pass_code` WHERE status=2 AND `operator` in (%s, '') ORDER BY `created` ASC LIMIT 1",
            user_name
        )

        # 如果有图片
        if item:
            redis_key = item['file_path']
            image_content = self.redis_get(redis_key)

            self.render('manul_search.html',
                        item=item,
                        total = total,
                        active='manual_passcode',
                        user=user_name,
                        image_content=image_content,
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
                image_content = self.redis_get(redis_key)

                self.render('manul_search.html',
                            item = item,
                            total = total,
                            active = 'manual_passcode',
                            user = user_name,
                            image_content = image_content,
                            navi = u"")

                return True

        return False

    def search_in_black(self, user_name, total):
        self.render('manul_search.html',
                            item = {},
                            total = total,
                            active = 'manual_passcode',
                            user = user_name,
                            image_content = None,
                            navi = u"")

        return True


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

