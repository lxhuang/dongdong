#!/usr/bin/env python

#interact with the deal table
#author: Lixing Huang
#date: May 5th, 2011

import tornado.database
import city_index

class DealData:
    def __init__(self, database):
        self.db = database
    
    def retrieve_first_deal(self, local, category):
        city_code = city_index.city_index[local]
        try:
            id = self.db.query("SELECT MIN(id) as val FROM deal WHERE city_code=%s and category=%s", int(city_code), int(category))
            first = id[0]["val"]
            if not first:
                return -1
            else:
                return int(first)
        except Exception, exception:
            print exception
            return -1
    
    def retrieve_last_deal(self, local, category):
        city_code = city_index.city_index[local]
        try:
            id = self.db.query("SELECT MAX(id) as val FROM deal WHERE city_code=%s and category=%s", int(city_code), int(category))
            last = id[0]["val"]
            if not last:
                return -1
            else:
                return int(last)
        except Exception, exception:
            print exception
            return -1
    
    # retrieve the details about a deal
    def retrieve_deal_info(self, deal_id):
        try:
            entry = self.db.get("SELECT * FROM deal WHERE id=%s", long(deal_id))
            return entry
        except Exception, exception:
            print exception
            return None
    
    def search_deals(self, local, category, min_price, max_price, limit, offset):
        try:
            if min_price!=None and max_price!=None:
                entries = self.db.query("SELECT * FROM deal WHERE city_code=%s and category=%s and min_price>=%s and max_price<=%s ORDER BY score DESC LIMIT %s OFFSET %s",
                                    int(local), int(category), float(min_price), float(max_price), int(limit), int(offset))
            elif min_price!=None:
                entries = self.db.query("SELECT * FROM deal WHERE city_code=%s and category=%s and min_price>=%s ORDER BY score DESC LIMIT %s OFFSET %s",
                                    int(local), int(category), float(min_price), int(limit), int(offset))
            elif max_price!=None:
                entries = self.db.query("SELECT * FROM deal WHERE city_code=%s and category=%s and max_price<=%s ORDER BY score DESC LIMIT %s OFFSET %s",
                                    int(local), int(category), float(max_price), int(limit), int(offset))
            elif min_price==None and max_price==None:
                entries = self.db.query("SELECT * FROM deal WHERE city_code=%s and category=%s ORDER BY score DESC LIMIT %s OFFSET %s",
                                    int(local), int(category), int(limit), int(offset))
            return entries
        except Exception, exception:
            print exception
            return None
    
    # retrieve deals in a local city in a specific category
    # @param local: local city, category: index of the category, 
    def retrieve_deals(self, local, category, limit, offset=None, morethan=None, lessthan=None):
        try:
            local = city_index.city_index[local]
            entries = None
            if offset:
                entries = self.db.query("SELECT * FROM deal WHERE city_code=%s and category=%s ORDER BY id DESC LIMIT %s OFFSET %s", int(local), int(category), int(limit), int(offset))
            elif morethan:
                entries = self.db.query("SELECT * FROM deal WHERE city_code=%s and category=%s and id>%s ORDER BY id ASC LIMIT %s", int(local), int(category), int(morethan), int(limit))
                entries.reverse()
            elif lessthan:
                entries = self.db.query("SELECT * FROM deal WHERE city_code=%s and category=%s and id<%s ORDER BY id DESC LIMIT %s", int(local), int(category), int(lessthan), int(limit))
            else:
                entries = self.db.query("SELECT * FROM deal WHERE city_code=%s and category=%s ORDER BY id ASC LIMIT %s", int(local), int(category), int(limit))
                entries.reverse()
            return entries
        except Exception, exception:
            print exception.args
            print exception
            return None
    
    # when user publishes a deal, the deal is inserted into db
    # @param deal_info: contains fbid, category, simple_desc, formatted_addr, 
    # disp_addr, min_price, max_price, details, phone, email, imgs
    # @return if success return deal_id otherwise return -1
    def insert_new_deal(self, deal_info):
        seller = 0
        category = 0
        simple_desc = ""
        formatted_addr = ""
        disp_addr = ""
        min_price = ""
        max_price = ""
        details = ""
        phone = ""
        email = ""
        
        if "fbid" in deal_info:
            seller = int(deal_info["fbid"])
        if "category" in deal_info:
            category = int(deal_info["category"])
        if "simple_desc" in deal_info:
            simple_desc = deal_info["simple_desc"]
        if "formatted_addr" in deal_info:
            formatted_addr = deal_info["formatted_addr"]
        if "disp_addr" in deal_info:
            disp_addr = deal_info["disp_addr"]
        if "min_price" in deal_info:
            min_price = float(deal_info["min_price"])
        if "max_price" in deal_info:
            max_price = float(deal_info["max_price"])
        if "details" in deal_info:
            details = deal_info["details"]
        if "phone" in deal_info:
            phone = deal_info["phone"]
        if "email" in deal_info:
            email = deal_info["email"]
        
        addr_tokens = formatted_addr.split(",")
        city = addr_tokens[len(addr_tokens)-1].lower()
        city_code = city_index.city_index[city]
        
        try:
            did = self.db.execute("INSERT INTO deal (category,seller,created_at,simple_desc,formatted_addr,displayed_addr,min_price,max_price,details,contact_phone,contact_email,city_code)"
                            " VALUES (%s,%s,UTC_TIMESTAMP(),%s,%s,%s,%s,%s,%s,%s,%s,%s)", category,seller,simple_desc,formatted_addr,disp_addr,min_price,max_price,details,phone,email,int(city_code))
            return did
        except Exception, exception:
            print exception.args
            print exception
            return -1