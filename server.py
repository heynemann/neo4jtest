#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of bzz.
# https://github.com/heynemann/bzz

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Bernardo Heynemann heynemann@gmail.com

import tornado.web
import tornado.ioloop
from tornado.httpserver import HTTPServer


class GetHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('get')


class PostHandler(tornado.web.RequestHandler):
    def post(self):
        self.write('post')


def main():
    routes = [
        ('/get', GetHandler),
        ('/post', PostHandler),
    ]

    application = tornado.web.Application(routes, debug=True)
    server = HTTPServer(application)
    server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
