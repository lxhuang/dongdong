#!/usr/bin/env python

# this is the homepage handler

import tornado.database
import tornado.httpserver
import tornado.web
from data.user import UserData

class HomeHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get(self):
        self.render("home.html")
