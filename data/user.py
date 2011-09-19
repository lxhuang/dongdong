#!/usr/bin/env python

# interact with the user table
# author: Lixing Huang
# date: May 2nd, 2011

import tornado.database

class UserData:
    def __init__(self, database):
        self.db = database

    # check whether this user has already existed
    # @param: fb_uid, the facebook user id, returned by Facebook Javascript API
    # @return: if existed, return the uid; otherwise, return -1
    def is_exist(self, fb_uid):
        user = self.db.get("SELECT * FROM user WHERE fb_uid = %s", long(fb_uid))
        if not user:
            return -1
        else:
            return user["uid"]

    # retrieve the user info
    def retrieve(self, fb_uid):
        user = self.db.get("SELECT * FROM user WHERE fb_uid = %s", long(fb_uid))
        if not user:
            return None
        else:
            return user

    # update user information
    def update(self, user_info):
        fb_uid = ""
        user_name = ""
        phone = ""
        home_address = ""
        fb_email = ""
        fb_location = ""
        if "fb_uid" in user_info:
            fb_uid = user_info["fb_uid"]
        if "username" in user_info:
            user_name = user_info["username"]
        if "phone" in user_info:
            phone = user_info["phone"]
        if "home_address" in user_info:
            home_address = user_info["home_address"]
        if "fb_email" in user_info:
            fb_email = user_info["fb_email"]
        if "fb_location" in user_info:
            fb_location = user_info["fb_location"]
        
        try:
            self.db.execute("UPDATE user SET username=%s, phone=%s, home_address=%s, fb_email=%s, fb_location=%s "
                            "WHERE fb_uid=%s", user_name, phone, home_address, fb_email, fb_location, int(fb_uid))
            return 1
        except Exception, exception:
            print exception.args
            print exception
            return -1

    # insert new user
    # @param: user_info, this is a dictionary containing all available information, the keys are:
    # username, phone, home_address, fb_uid, fb_username, fb_thumbnail, fb_email, fb_gender, fb_location
    # @return if success, return the uid; otherwise, return -1
    def insert_new_user(self, user_info):
        user_name = ""
        phone = ""
        home_address = ""
        fb_uid = ""
        fb_username = ""
        fb_email = ""
        fb_thumbnail = ""
        fb_gender = ""
        fb_location = ""
        
        if "username" in user_info:
            user_name = user_info["username"]
        if "phone" in user_info:
            phone = user_info["phone"]
        if "home_address" in user_info:
            home_address = user_info["home_address"]

        if "fb_uid" in user_info:
            fb_uid = user_info["fb_uid"]
        if "fb_username" in user_info:
            fb_username = user_info["fb_username"]
        if "fb_email" in user_info:
            fb_email = user_info["fb_email"]
        if "fb_thumbnail" in user_info:
            fb_thumbnail = user_info["fb_thumbnail"]
        if "fb_gender" in user_info:
            fb_gender = user_info["fb_gender"]
        if "fb_location" in user_info:
            fb_location = user_info["fb_location"]

        try:
            db_result = self.db.execute(
                "INSERT INTO user (username, phone, home_address, fb_uid, fb_username, fb_thumbnail, fb_email, fb_gender, fb_location) VALUES "
                "(%s,%s,%s,%s,%s,%s,%s,%s,%s)", user_name, phone, home_address, fb_uid, fb_username, fb_thumbnail, fb_email, fb_gender, fb_location
                )
            return db_result
        except:
            print "error: insert into user table"
            return -1
    
