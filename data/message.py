#!/usr/bin/env python

import tornado.database

class MessageData:
    def __init__(self,database):
        self.db = database
        
    def insert_message(self, msg):
        try:
            id = self.db.execute("INSERT INTO message (message) VALUES (%s)", msg)
            return id
        except Exception, exception:
            print exception
            return None
        
    def retrieve_message(self, id):
        try:
            entry = self.db.get("SELECT * FROM message WHERE id=%s", long(id))
            return entry
        except Exception, exception:
            print exception
            return None