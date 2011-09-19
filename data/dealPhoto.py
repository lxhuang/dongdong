#!/usr/bin/env python

# interact with deal_photo table
# author: Lixing Huang
# date: May 5th, 2011

import tornado.database

class DealPhotoData:
    def __init__(self,database):
        self.db = database
    
    # retrieve photos related to a deal
    def get_deal_photo(self,deal_id):
        try:
            entries = self.db.query("SELECT * FROM deal_photo where deal_id=%s", long(deal_id))
            return entries
        except Exception, exception:
            print exception
            return None
        
    # a deal may have several attached images
    # @param deal_id, imgs
    # if success return 1 otherwise return -1
    def insert_deal_photo(self,deal_info):
        deal_id = 0
        imgs = None
        if "deal_id" in deal_info:
            deal_id = deal_info["deal_id"]
        else:
            self.write("{\"err\":\"error in inserting to deal photo table, no deal id\"}")
            return
        
        if "imgs" in deal_info:
            imgs = deal_info["imgs"]
        
        try:
            for img in imgs:
                self.db.execute("INSERT INTO deal_photo (deal_id, photo_id) VALUES (%s,%s)", int(deal_id), int(img))
            return 1
        except Exception, exception:
            print exception.args
            print exception
            return -1