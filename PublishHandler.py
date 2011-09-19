#!/usr/bin/env python

#this is the interface for publishing deals

import tornado.database
import tornado.httpserver
import tornado.web
from data.deal import DealData
from data.dealPhoto import DealPhotoData
from data.user import UserData

class PublishHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    
    # user publishes deals
    # @param fbid, category, simdesc, addr, dispaddr, min, max, details, phone, email, imgs
    def post(self):
        fb_uid = self.get_argument("fbid", None)
        category = self.get_argument("category", None)
        simple_desc = self.get_argument("simdesc", None)
        formatted_addr = self.get_argument("addr", None)
        disp_addr = self.get_argument("dispaddr", None)
        min_price = self.get_argument("min", None)
        max_price = self.get_argument("max", None)
        desc = self.get_argument("details", None)
        phone = self.get_argument("phone", None)
        email = self.get_argument("email", None)
        imgs = self.get_argument("imgs", None)
        
        deal_info = {}
        if fb_uid:
            deal_info["fbid"] = fb_uid
        else:
            self.write("{\"err\":\"login facebook\"}")
            return
        
        #check whether this user is registered
        user_data = UserData(self.db)
        if user_data.is_exist(fb_uid) == -1:
            print "reject unregistered user publishing deal"
            return
        
        if category:
            deal_info["category"] = category
        else:
            self.write("{\"err\":\"no category\"}")
            return
        
        if simple_desc:
            deal_info["simple_desc"] = simple_desc
        else:
            self.write("{\"err\":\"no simple desc\"}")
            return
        
        if min_price:
            deal_info["min_price"] = min_price
        else:
            self.write("{\"err\":\"no min price\"}")
            return
        
        if max_price:
            deal_info["max_price"] = max_price
        else:
            self.write("{\"err\":\"no max price\"}")
            return
        
        if formatted_addr:
            deal_info["formatted_addr"] = formatted_addr
        if disp_addr:
            deal_info["disp_addr"] = disp_addr
        if desc:
            deal_info["details"] = desc
        if phone:
            deal_info["phone"] = phone
        if email:
            deal_info["email"] = email
        if imgs:
            img_array = imgs.split("|")
            deal_info["imgs"] = img_array
            
        deal_data = DealData(self.db)
        deal_id = deal_data.insert_new_deal(deal_info)
        if deal_id == -1:
            self.write("{\"err\":\"error in inserting to deal table\"}")
            return
        
        if not ("imgs" in deal_info):
            self.write("{\"success\":"+str(deal_id)+"}")
            return
        
        deal_info["deal_id"] = deal_id
        deal_photo_data = DealPhotoData(self.db)
        res = deal_photo_data.insert_deal_photo(deal_info)
        self.write("{\"success\":"+str(res)+"}")