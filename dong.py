#!/usr/bin/env python

# dong-dong web application start up page

import os
import tornado.auth
import tornado.database
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from HomeHandler import HomeHandler
from UserHandler import UserHandler
from PublishHandler import PublishHandler
from UploadPhoto import UploadPhoto
from DealHandler import DealHandler
from DealInfoHandler import DealInfoHandler
from SearchHandler import SearchHandler
from ConvHandler import ConvHandler
from WishHandler import WishHandler

from tornado.options import define, options

define("port", default=8483, type=int)
define("mysql_host", default="127.0.0.1:3306")
define("mysql_database", default="dong")
define("mysql_user", default="root")
define("mysql_password", default="")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/user/register", UserHandler),
            (r"/publish", PublishHandler),
            (r"/upload", UploadPhoto),
            (r"/deal", DealHandler),
            (r"/deal/([0-9]+)", DealInfoHandler),
            (r"/search", SearchHandler),
            (r"/conversation", ConvHandler),
            (r"/wishlist", WishHandler)
        ]

        settings = dict(
            title = "Dong-Dong",
            base_url = "http://localhost:8483/",
            login_url = "/login",
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            ui_modules={
                "Deal": DealModule
            }
        )

        tornado.web.Application.__init__(self, handlers, **settings)

        self.db = tornado.database.Connection(
            host = options.mysql_host,
            database = options.mysql_database,
            user = options.mysql_user,
            password = options.mysql_password
            )

class DealModule(tornado.web.UIModule):
    def render(self, deal):
        return self.render_string("modules/deal.html", deal=deal)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
