#!/usr/bin/env python

import tornado.database

class WishlistData:
    def __init__(self, database):
        self.db = database
        
    def insert_new_wish(self, uid, category, content):
        try:
            id = self.db.execute("INSERT INTO wishlist (uid, category, content, created_at, is_closed) VALUES (%s,%s,%s,UTC_TIMESTAMP(),%s)",
                                 long(uid), int(category), content, 0 )
            return id
        except Exception,exception:
            print exception
            print "wishlist.py insert_new_wish"
            return -1
        
    def retrieve_alive_wishlist(self, uid):
        try:
            entries = self.db.query("SELECT * FROM wishlist WHERE uid=%s and is_closed=%s ORDER BY created_at DESC",
                                    long(uid), 0)
            return entries
        except Exception,exception:
            print exception
            print "wishlist.py retrieve_alive_wishlist"
            return None
        
    def retrieve_wishlist(self, uid):
        try:
            entries = self.db.query("SELECT * FROM wishlist WHERE uid=%s ORDER BY created_at DESC", long(uid))
            return entries
        except Exception,exception:
            print exception
            print "wishlist.py retrieve_wishlist"
            return None
        
    def close_wish(self, id):
        try:
            res = self.db.execute("UPDATE wishlist SET is_closed=1 WHERE id=%s", long(id))
            print str(res)
            return res
        except Exception,exception:
            print exception
            print "wishlist.py close_wish"
            return None