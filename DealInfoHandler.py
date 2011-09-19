#!/usr/bin/env python

#get the details about a deal

import tornado.web
import tornado.httpserver
import tornado.database
import json
from data.deal import DealData
from data.user import UserData
from data.dealPhoto import DealPhotoData
from data.photo import PhotoData

class DealInfoHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    
    def get(self, deal_id):
        if not deal_id:
            return
        
        deal_data = DealData(self.db)
        deal_info = deal_data.retrieve_deal_info(deal_id)
        if not deal_info:
            self.render("deal_info.html", deal_info=None)
            return
        
        user_data = UserData(self.db)
        user_info = user_data.retrieve(deal_info["seller"])
        if not user_info:
            self.render("deal_info.html", deal_info=None)
            return
        
        res = {}
        
        deal_photo_data = DealPhotoData(self.db)
        deal_photo_info = deal_photo_data.get_deal_photo(deal_id)
        
        if deal_photo_info and len(deal_photo_info)>0:
            photo_data = PhotoData(self.db)
            photo_urls = []
            photo_pids = []
            for pi in deal_photo_info:
                p = photo_data.retrieve(pi["photo_id"])
                photo_urls.append(p["filename"])
                photo_pids.append(p["pid"])
            res["imgs"] = photo_urls
            res["pids"] = photo_pids
        
        res["id"]=deal_info["id"]
        res["category"]=deal_info["category"]
        res["seller_fbid"]=deal_info["seller"]
        res["seller_name"]=user_info["username"]
        res["created_at"]=str(deal_info["created_at"])
        res["simple_desc"]=deal_info["simple_desc"]
        res["disp_addr"]=deal_info["displayed_addr"]
        res["min_price"]=deal_info["min_price"]
        res["max_price"]=deal_info["max_price"]
        res["details"]=deal_info["details"]
        res["contact_phone"]=deal_info["contact_phone"]
        res["contact_email"]=deal_info["contact_email"]
        
        self.render("deal_info.html", deal_info=res)