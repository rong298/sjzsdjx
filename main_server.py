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
import sys
import logging

from configobj import ConfigObj

import tornado.web
import tornado.ioloop
import tornado.httpserver
from tornado.options import define
from tornado.options import options

from lib import database
from timer.main_processor_checker import MainProcessorChecker
from handler.ruokuai_handler import RuokuaiHandler
from handler.dama2_handler import Dama2Handler

from handler.passcode_handler import ManualPasscodeHandler

define("port", default=9001, help="run on the given port", type=int)
define("proc", default=2, help="the number of system processes", type=int)
define("proxies", default='', help="Proxies for requests")
define("platform", default='ruokuai', help="ruokuai若快; dama2 打码2; qn_dama去哪儿; manul人工")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = []
        if options.platform == 'manul':
            handlers.append((r"/dama[/]?", ManualPasscodeHandler))
            handlers.append((r"/dama/manual_passcode[/]?", ManualPasscodeHandler))
        elif options.platform == 'ruokuai':
            handlers.append((r"/dama[/]?", RuokuaiHandler))
        elif options.platform == 'dama2':
            handlers.append((r"/dama[/]?", Dama2Handler))
        elif options.platform == 'ruokuai':
            handlers.append((r"/dama[/]?", RuokuaiHandler))

        root_abspath = os.path.dirname(
                os.path.abspath(sys.argv[0]))
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
            login_url="/dama"
        )

        logging.debug(settings)
        tornado.web.Application.__init__(self, handlers, **settings)

        # Have one global connection to the blog DB across all handlers
        self.db = database.Connection(**config['mysql'])
        '''
            host=config['mysql']['host'], database=config['mysql']['database'],
            user=config['mysql']['user'], password=config['mysql']['password'])
        '''

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
