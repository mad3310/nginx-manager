#!/usr/bin/env python
#-*- coding: utf-8 -*-

import logging.config
import os.path

from tornado.httpserver import HTTPServer
import tornado.ioloop
from tornado.options import options
import tornado.options
import tornado.web

from appdefine import appDefine
import routes


class Application(tornado.web.Application):
    def __init__(self):
        
        settings = dict(
            template_path=os.path.join(options.base_dir, "templates"),
            ui_modules={"Entry": None},
            xsrf_cookies=False,
            cookie_secret="16oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp5XdTP1o/Vo=",
            login_url="/auth/login",
            debug=options.debug,
        )
        
        tornado.web.Application.__init__(self, routes.handlers, **settings)

def main():
    config_path = os.path.join(options.base_dir, "config")
    logging.config.fileConfig(config_path + '/logging.conf')
    tornado.options.parse_command_line()
    http_server = HTTPServer(Application())
    http_server.listen(options.port)
    
    tornado.ioloop.IOLoop.instance().start()
    
if __name__ == "__main__":
    main()
