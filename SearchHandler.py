#!/usr/bin/env python

import tornado.web
import tornado.httpserver
import tornado.database
import sphinxapi
import sys
from data.deal import DealData
from data.user import UserData
from data.city_index import city_index
import json

class SearchHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    
    def validInt(self, num):
        try:
            v = int(num)
            return v
        except:
            self.write("{\"err\":\"invalid arguments\"}")
            return None
    
    def validFloat(self, num):
        try:
            v = float(num)
            return v
        except:
            self.write("{\"err\":\"invalid arguments\"}")
            return None
    
    def get(self):
        local = self.get_cookie("geo")
        if not local:
            return
        else:
            local = " ".join(local.split("-"))
            local = local.lower()
        
        local     = int(city_index[local])
        category  = self.get_argument("category", None)
        min_price = self.get_argument("min", None)
        max_price = self.get_argument("max", None)
        keywords  = self.get_argument("q", None)
        
        limit = 2
        offset = self.get_argument("p", None)
        if offset==None: 
            offset = 0
        else:
            offset = self.validInt(offset)
            if offset==None: return
        
        if not category: return
        category = self.validInt(category)
        if not category: return
        
        if min_price:
            min_price = self.validFloat(min_price)
            if min_price==None: return
        if max_price:
            max_price = self.validFloat(max_price)
            if max_price==None: return
        if min_price!=None and max_price!=None and min_price > max_price:
            self.write("{\"err\":\"max price should be higher than min price\"}")
            return
        
        deal_data = DealData(self.db)
        user_data = UserData(self.db)
        
        entries = []
        
        if keywords and len(keywords)!=0:
            print keywords
            
            keywords = " ".join(keywords.split("+"))
            
            client = sphinxapi.SphinxClient()
            client.SetFilterRange("category", category, category)
            client.SetFilterRange("city_code", local, local)
            if min_price:
                client.SetFilterFloatRange("min_price", min_price, 99999999999999999.9)
            if max_price:
                client.SetFilterFloatRange("max_price", -1.0, max_price)
            
            client.SetLimits(offset*limit, limit)
            client.SetSortMode(sphinxapi.SPH_SORT_RELEVANCE)
            
            results = client.Query(keywords)
            hits = results["matches"]
            
            for hit in hits:
                deal_id = hit["id"]
                deal = deal_data.retrieve_deal_info(deal_id)
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
                entries.append(deal_info)
        else:
            deals = deal_data.search_deals(local, category, min_price, max_price, limit, offset*limit)
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
                entries.append(deal_info)
        
        if offset==0 and len(entries)==0:
            self.render("error.html", type=0, msg="No results found")
        else:
            query = None
            if keywords and len(keywords)!=0:
                query = "+".join(keywords.split(" "))
            
            if min_price==None:
                min_price=""
            if max_price==None:
                max_price=""
            self.render("search.html", deals=entries, offset=offset, category=category, 
                        min_price=min_price, max_price=max_price, query=query)
            
            
            
            
            