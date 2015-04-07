#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 FIXUN
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import logging
import redis

import sys
reload(sys)
sys.setdefaultencoding('utf8')

from configobj import ConfigObj

import tornado.web
import tornado.ioloop
import tornado.httpserver
from tornado.options import define
from tornado.options import options
from lib.md5_lib import MD5

from lib import database
from timer.main_processor_checker import MainProcessorChecker
from handler.manul_input_handler import *
from handler.op_handler import *
from handler.monitor_handler import *

define("port", default=10010, help="run on the given port", type=int)
define("proc", default=2, help="the number of system processes", type=int)
define("proxies", default='', help="Proxies for requests")

ABS_ROOT_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
STATIC_PATH = ABS_ROOT_PATH + "/static"

class Application(tornado.web.Application):
    def __init__(self):
        handlers = []

        # 打码控制平台
        handlers.append((r"/op/login[/]?", OpLoginHandler))
        handlers.append((r"/op/login_process[/]?", OpLoginProcessHandler))

        # TODO 后期要上升到整个页面的退出
        handlers.append((r"/admin/logout[/]?", OpLogoutHandler))

        handlers.append((r"/op/platform_view[/]?", OpPlatformViewHandler))
        handlers.append((r"/op/normal_monitor[/]?", OpRunningMonitorHandler))
        handlers.append((r"/op/platform_change[/]?", OpPlatformChangeHandler))

        handlers.append((r"/op/monitor[/]?", OpMonitorHandler))
        handlers.append((r"/op/balance[/]?", OpBalanceHandler))

        # 监控接口
        handlers.append((r"/monitor/error[/]?", MonitorErrorHandler))
        handlers.append((r"/monitor/timeout[/]?", MonitorTimeOutHandler))

        root_abspath = os.path.dirname(os.path.abspath(sys.argv[0]))
        web_root = os.path.dirname(__file__)

        config = ConfigObj(root_abspath + '/config/config_online.ini',
                encoding='UTF8')

        logging.debug(config)

        settings = dict(
            root_path = os.path.join(web_root),
            root_abspath = root_abspath,
            template_path=os.path.join(web_root, "templates"),
            static_path=os.path.join(web_root, "static"),
            ui_modules={},
            xsrf_cookies=False, #True,
            cookie_secret="9OWWEaJVQ3m0WOHDLJbX7+XKm8TCmUuki6BEE7RVur4=",
            login_url="/op/login"
        )

        logging.debug(settings)
        tornado.web.Application.__init__(self, handlers, **settings)

        # Have one global connection to the blog DB across all handlers
        self.db = database.Connection(**config['mysql'])
        '''
            host=config['mysql']['host'], database=config['mysql']['database'],
            user=config['mysql']['user'], password=config['mysql']['password'])
        '''

        self.query_id = MD5.random_md5()
        self.config = config

        self.proxies = {}
        if options.proxies:
            self.proxies = {"https": "http://"+options.proxies}

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.bind(options.port)
    http_server.start(options.proc)

    MainProcessorChecker().start()
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
