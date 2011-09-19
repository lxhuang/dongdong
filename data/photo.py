#!/usr/bin/env python

import tornado.database

class PhotoData:
    def __init__(self,database):
        self.db = database
        
    def insert_new_photo(self, filename):
        try:
            db_result = self.db.execute("INSERT INTO photo (filename) VALUES (%s)", filename)
            return db_result
        except:
            return -1
        
    def retrieve(self, id):
        try:
            p = self.db.get("SELECT * FROM photo WHERE pid = %s", long(id))
            if not p:
                return None
            else:
                return p
        except:
            return None