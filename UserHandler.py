#!/usr/bin/env python

# this is the interface of the user table

import tornado.database
import tornado.httpserver
import tornado.web
import json
from data.user import UserData

class UserHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    
    # user request the user table by posting messages
    # we use keyword "t" to indicate the type
    #    0: check whether the user exists. @param facebook uid
    #    1: register new user. @param username, phone, home_address, fbuid, fbusername, fbthumbnail, fbmail, fbgender, fbloc
    #    2: retrieve the user info @param facebook uid
    #    3: update user info @param username phone home_address fbmail fbloc
    def post(self):
        type = self.get_argument("t", None)
        type = int(type)
        if type == 0:
            fb_uid = self.get_argument("fbid", None)
            if fb_uid:
                user_data = UserData(self.db)
                uid = user_data.is_exist(fb_uid)
                self.write(str(uid))
            else:
                return
        elif type == 1:
            user_name    = self.get_argument("username", None)
            phone        = self.get_argument("phone", None)
            home_address = self.get_argument("addr", None)
            fb_uid       = self.get_argument("fbid", None)
            fb_username  = self.get_argument("fbu", None)
            fb_thumbnail = self.get_argument("fbthumb", None)
            fb_email     = self.get_argument("fbmail", None)
            fb_gender    = self.get_argument("fbgender", None)
            fb_location  = self.get_argument("fbloc", None)

            user_info = {}
            if user_name:
                user_info["username"] = user_name
            else:
                return
            if phone:
                user_info["phone"] = phone
            if home_address:
                user_info["home_address"] = home_address

            if fb_uid:
                user_info["fb_uid"] = fb_uid
            else:
                return
            if fb_username:
                user_info["fb_username"] = fb_username
            if fb_thumbnail:
                user_info["fb_thumbnail"] = fb_thumbnail
            if fb_email:
                user_info["fb_email"] = fb_email
            if fb_gender:
                user_info["fb_gender"] = fb_gender
            if fb_location:
                user_info["fb_location"] = fb_location
                
            user_data = UserData(self.db)
            uid = user_data.insert_new_user(user_info)
            self.write(str(uid))
        elif type == 2:
            fb_uid = self.get_argument("fbid", None)
            if fb_uid:
                user_data = UserData(self.db)
                user_info = user_data.retrieve(fb_uid)
                self.write(json.dumps(user_info))
        elif type == 3:
            fb_uid       = self.get_argument("fbid", None)
            user_name    = self.get_argument("username", None)
            phone        = self.get_argument("phone", None)
            home_address = self.get_argument("addr", None)
            fb_email     = self.get_argument("fbmail", None)
            fb_location  = self.get_argument("fbloc", None)
            
            user_info = {}
            if fb_uid:
                user_info["fb_uid"] = fb_uid
            else:
                return
            if user_name:
                user_info["username"] = user_name
            else:
                return
            if phone:
                user_info["phone"] = phone
            if home_address:
                user_info["home_address"] = home_address
            if fb_email:
                user_info["fb_email"] = fb_email
            if fb_location:
                user_info["fb_location"] = fb_location
            user_data = UserData(self.db)
            res = user_data.update(user_info)
            self.write(str(res));