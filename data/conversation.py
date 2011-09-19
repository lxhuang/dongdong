#!/usr/bin/env python

import tornado.database

class ConversationData:
    def __init__(self, database):
        self.db = database
        
    def insert_new_conv(self, deal_id, uid, with_uid, msg_id, is_read, is_sender):
        try:
            id = self.db.execute("INSERT INTO conversation (dealid, uid, with_uid, created_at, msg_id, is_read, is_sender) VALUES (%s,%s,%s,UTC_TIMESTAMP(),%s,%s,%s)",
                            long(deal_id), long(uid), long(with_uid), long(msg_id), int(is_read), int(is_sender))
            return id
        except Exception, exception:
            print exception
            return None
        
    def retrieve_deals(self, uid, offset, limit):
        try:
            entries = self.db.query("SELECT DISTINCT dealid FROM conversation WHERE uid=%s ORDER BY created_at DESC LIMIT %s OFFSET %s", long(uid), int(limit), int(offset))
            print str(entries)
            return entries
        except Exception, exception:
            print exception
            return None
        
    def retrieve_contacts(self, deal_id, uid):
        try:
            contacts = self.db.query("SELECT DISTINCT with_uid FROM conversation WHERE uid=%s and dealid=%s ORDER BY created_at DESC", long(uid), long(deal_id))
            return contacts
        except Exception, exception:
            print exception
            return None
    
    def retrieve_unread_message_num(self, deal_id, uid, with_uid):    
        try:
            count = self.db.query("SELECT COUNT(*) AS count FROM conversation WHERE dealid=%s and uid=%s and with_uid=%s and is_read=0", long(deal_id), long(uid), long(with_uid))
            return count
        except Exception, exception:
            print exception
            return 0
    
    def retrieve_messages(self, deal_id, uid, with_uid):
        try:
            messages = self.db.query("SELECT * FROM conversation WHERE dealid=%s and uid=%s and with_uid=%s ORDER BY created_at DESC", long(deal_id), long(uid), long(with_uid))
            return messages
        except Exception, exception:
            print exception
            return None
        
    def make_messages_read(self, deal_id, uid, with_uid):
        try:
            is_read=1
            self.db.execute("UPDATE conversation SET is_read=%s WHERE dealid=%s and uid=%s and with_uid=%s", int(is_read), long(deal_id), long(uid), long(with_uid))
        except Exception,exception:
            print exception