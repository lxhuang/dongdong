#!/usr/bin/env python

import tornado.web
import tornado.httpserver
import tornado.database
import json
from data.deal import DealData
from data.user import UserData

class DealHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    
    def validInt(self, num):
        try:
            int(num)
            return 1
        except:
            self.write("{\"err\":\"invalid arguments\"}")
            return -1
    
    # there are several ways to retrieve deals:
    #    1. where category=%s, city=%s, and use offset and limit 
    #    2. where category=%s, city=%s, and use more-than(mt) and limit
    #    3. where category=%s, city=%s, and use less-than(lt) and limit
    def get(self):
        #local = self.get_argument("local", None)
        local = self.get_cookie("geo")
        if not local:
            return
        local = " ".join(local.split("-"))
        if not local:
            return
        else:
            local = local.lower()
        
        category = self.get_argument("category", None)
        #limit = self.get_argument("limit", None)
        limit = 4
        
        if not category:
            self.render("deals.html", last=None, first=None, deals=None)
            return
        
        offset = self.get_argument("offset", None)
        morethan = self.get_argument("more", None)
        lessthan = self.get_argument("less", None)
        
        if (offset==None) and (morethan==None) and (lessthan==None):
            self.write("{\"err\":\"incomplete arguments\"}")
            return
        
        self.validInt(category)
        self.validInt(limit)
        
        if offset!=None:
            self.validInt(offset)
        elif morethan!=None:
            self.validInt(morethan)
        elif lessthan!=None:
            self.validInt(lessthan)
        
        deal_data = DealData(self.db)
        
        deals = None
        if offset:
            deals = deal_data.retrieve_deals(local, category, limit, offset)
        elif morethan:
            deals = deal_data.retrieve_deals(local, category, limit, None, morethan)
        elif lessthan:
            deals = deal_data.retrieve_deals(local, category, limit, None, None, lessthan)
        else: # this only happens when it is the end of deals and user presses prev page
            deals = deal_data.retrieve_deals(local, category, limit, None, None, None)
        
        last_id = deal_data.retrieve_last_deal(local, category)
        first_id= deal_data.retrieve_first_deal(local, category)
        
        user_data = UserData(self.db)
        
        deal_array = []
        for deal in deals:
            deal_info = {}
            deal_info["id"] = deal["id"]
            deal_info["category"] = deal["category"]
            deal_info["seller_fbid"] = deal["seller"]
            user_info = user_data.retrieve(deal["seller"])
            deal_info["seller_name"] = user_info["username"]
            deal_info["created_at"] = str(deal["created_at"])
            deal_info["simple_desc"] = deal["simple_desc"]
            deal_info["disp_addr"] = deal["displayed_addr"]
            deal_info["min_price"] = deal["min_price"]
            deal_info["max_price"] = deal["max_price"]
            deal_array.append(deal_info)
        
        self.render("deals.html", last=last_id, first=first_id, deals=deal_array)
        #self.write(json.dumps(res))