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

class ManulHandler(BaseHandler):

    def get(self):
        user_name = self.get_cookie('user_name')
        if not user_name: # 没有cookie
            user_name = self.get_argument('user_name', strip=True, default=None)
            if not user_name: # 没有输入用户名
                self.render("manual_passcode_user.html")
                return
            else:
                self.set_cookie('user_name', user_name+'_'+str(uuid.uuid1()))
                user_name = self.get_cookie('user_name')

        search_key = self.get_argument('search_key', strip=True, default=None)
        passvalue1 = self.get_argument('passvalue1', strip=True, default=None)
        # passvalue2 = self.get_argument('passvalue2', strip=True, default=None)
        if search_key and passvalue1:
            affected = self.db.execute(
                    "UPDATE `pass_code` SET `status`=3, `result`='%s', `operator`='%s' WHERE `search_key`='%s'" % (
                        passvalue1, user_name, search_key)
                    )
            self.redirect('/dama')
            return

        total = self.db.get("SELECT count(*) as total FROM `pass_code` WHERE status=1")

        # 优先输入已锁定的验证码
        items = self.db.query("SELECT * FROM `pass_code` WHERE status=2 AND `operator` in ('%s', '') ORDER BY `created` ASC LIMIT 20"
                % user_name)
        if items:
            self.render("manual_passcode.html", item=items[0],
                    total = total['total'],
                    active='manual_passcode', user=user_name, navi=u"")
            return

        # 从未锁定的记录中选择
        items = self.db.query("SELECT * FROM `pass_code` WHERE status=1 ORDER BY `created` ASC")

        logging.debug(items)

        if not items:
            self.render("manual_passcode.html", item={'search_key':''},
                    total = total['total'],
                    active='manual_passcode', user=user_name, navi=u"")
            return
        for item in items:
            affected = self.db.execute_rowcount("UPDATE `pass_code` SET status=2, operator='%s' WHERE `id`=%s"
                    % (user_name, item['id']))
            logging.debug(affected)
            if affected==1:
                logging.debug(item)
                self.render("manual_passcode.html", item=item,
                        total = total['total'],
                        active='manual_passcode', user=user_name, navi=u"")
                return

    def _do_query_dama(self, params):
        config = self._load_config('/config/%s.ini' % ManulBusiness._PLATFORM_CODE)
        manul_biz = ManulBusiness(db=self.db, config=config, app_config=self.application.settings)

        # 先记录
        insert_id = manul_biz.query_record(params,  self.request.remote_ip)

        # 打码解析
        start_time = datetime.datetime.now()
        result = manul_biz.passcode_identify(params['params']['content'],
                config['image_type'])
        end_time =  datetime.datetime.now()

        # 执行结果反馈
        manul_biz.response_record(insert_id, start_time, end_time, result)

        context = manul_biz.parse_result(insert_id, result)

        # 返回成功
        if context:
            self.write(cjson.encode(context))
        else:
            # 默认返回错误
            self.write(cjson.encode(
                self._error_page('10000')))
