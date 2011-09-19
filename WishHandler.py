#!/usr/bin/env python

import tornado.web
import tornado.httpserver
import tornado.database
from data.wishlist import WishlistData
from data.user import UserData

class WishHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    
    def get(self):
        uid = self.get_argument("uid", None)
        if uid==None:
            self.write("{\"err\": \"not enough arguments\"}")
            return
        
        wishlist_data = WishlistData(self.db)
        wishlist = wishlist_data.retrieve_alive_wishlist(uid)
        if wishlist==None:
            return
        
        user_data = UserData(self.db)
        user_info = user_data.retrieve(uid)
        if not user_info or len(user_info)==0:
            print "no user info found in wishlist.py"
            return
        
        self.render("wishlist.html", wishlist=wishlist, user=user_info)
        
    def post(self):
        type = self.get_argument("t", None)
        if type==None: return
        try:
            type = int(type)
        except:
            return
        
        if type==1:
            uid = self.get_argument("uid", None)
            category = self.get_argument("category", None)
            content = self.get_argument("content", None)
            if (uid==None) or (category==None) or (content==None):
                self.write("{\"err\": \"not enough arguments\"}")
                return
            
            try: long(uid)
            except:
                return
            
            try: int(category)
            except:
                return
            
            wishlist_data = WishlistData(self.db)
            id = wishlist_data.insert_new_wish(uid, category, content)
            self.write("{\"id\": \""+str(id)+"\"}")
            
            
        elif type==2:
            wish_id = self.get_argument("id", None)
            if wish_id==None: return
            
            wishlist_data = WishlistData(self.db)
            res = wishlist_data.close_wish(wish_id)
            if res==None:
                self.write("{\"err\":\"true\"}")
            else:
                self.write("{\"success\":\"true\"}")