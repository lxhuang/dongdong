#!/usr/bin/env python

import tornado.web
import tornado.httpserver
import tornado.database
from data.conversation import ConversationData
from data.message import MessageData
from data.deal import DealData
from data.user import UserData
import json

class ConvHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db
    
    def validInt(self, v):
        try:
            return int(v)
        except:
            return None
    
    def validLong(self, v):
        try:
            return long(v)
        except:
            return None
    
    def post(self):
        type = self.get_argument("t", None)
        if not type: return
        try:
            type = int(type)
        except:
            return
        
        if type==0:
            deal_id = self.get_argument("dealid", None)
            uid = self.get_argument("uid", None) #the one who sends the message
            with_uid = self.get_argument("to", None) #the one who receives the message
            message = self.get_argument("msg", None)
            
            if (not deal_id) or (not uid) or (not with_uid) or (not message):
                self.write("{\"err\": \"not enough arguments\"}")
                return
            
            if self.validLong(deal_id)==None:
                print "invalid deal_id in ConvHandler.py post"
                return
            if self.validLong(uid)==None:
                print "invalid uid_id in ConvHandler.py post"
                return
            if self.validLong(with_uid)==None:
                print "invalid with_uid in ConvHandler.py post"
                return
            
            #insert the message into message table and get the message id
            message_data = MessageData(self.db)
            mid = message_data.insert_message(message)
            if mid==None:
                self.write("{\"err\": \"error in saving message\"}")
                return
            
            #insert the conversation into the conversation table twice
            conversation_data = ConversationData(self.db)
            cid = conversation_data.insert_new_conv(deal_id, uid, with_uid, mid, 1, 1)
            if cid==None:
                self.write("{\"err\": \"error in saving conversation\"}")
                return
            if uid!=with_uid:
                cid = conversation_data.insert_new_conv(deal_id, with_uid, uid, mid, 0, 0)
                if cid==None:
                    self.write("{\"err\": \"error in saving conversation\"}")
                    return
            
            self.write("{\"success\": \"true\"}")
        elif type==1:
            deal_id = self.get_argument("dealid", None)
            uid = self.get_argument("uid", None)
            if (not deal_id) or (not uid):
                self.write("{\"err\": \"not enough arguments\"}")
                return
            
            print deal_id
            
            if self.validLong(deal_id) == None:
                print "invalid deal_id in ConvHandler.py post"
                return
            if self.validLong(uid) == None:
                print "invalid uid_id in ConvHandler.py post"
                return
            
            # retrieve all contact ranked by date
            user_data = UserData(self.db)
            conversation_data = ConversationData(self.db)
            contacts = conversation_data.retrieve_contacts(deal_id, uid)
            
            result = []
            for contact in contacts:
                with_uid = contact["with_uid"]
                user_info = user_data.retrieve(with_uid)
                
                entry = {}
                entry["username"] = user_info["username"]
                entry["id"] = with_uid
                # retrieve the unread number for each contact
                count = conversation_data.retrieve_unread_message_num(deal_id, uid, with_uid)
                entry["unread"] = count[0]["count"];
                
                result.append(entry)
            
            self.write(json.dumps(result))
        elif type==2:
            deal_id = self.get_argument("dealid", None)
            uid = self.get_argument("uid", None)
            with_uid = self.get_argument("with_uid", None)
            if (not deal_id) or (not uid) or (not with_uid):
                self.write("{\"err\": \"not enough arguments\"}")
                return
            
            conversation_data = ConversationData(self.db)
            messages = conversation_data.retrieve_messages(deal_id, uid, with_uid)
            if (not messages) or len(messages)==0:
                return
            
            message_data = MessageData(self.db)
            
            result = []
            for message in messages:
                entry = {}
                msg_id = message["msg_id"]
                content= message_data.retrieve_message(msg_id)
                
                entry["message"] = content["message"]
                entry["msg_id"] = msg_id
                entry["created_at"] = str(message["created_at"])
                entry["is_sender"] = message["is_sender"]
                
                result.append(entry)
            self.write(json.dumps(result))
        elif type==3:
            deal_id = self.get_argument("dealid", None)
            uid = self.get_argument("uid", None)
            with_uid = self.get_argument("with_uid", None)
            if (not deal_id) or (not uid) or (not with_uid):
                self.write("{\"err\": \"not enough arguments\"}")
                return
            
            conversation_data = ConversationData(self.db)
            conversation_data.make_messages_read(deal_id, uid, with_uid)
            
    def get(self):
        uid = self.get_argument("uid", None)
        if not uid:
            return
        
        limit = 4
        offset = self.get_argument("p", None)
        if offset==None: 
            offset=0
        else:
            try:
                offset=int(offset)
            except:
                return;
        
        conversation_data = ConversationData(self.db)
        entries = conversation_data.retrieve_deals(uid, offset*limit, limit)
        if entries!=None:
            deal_data = DealData(self.db)
            
            deals = []
            for entry in entries:
                deal_info = deal_data.retrieve_deal_info(entry["dealid"])
                entry = {}
                entry["simple_desc"] = deal_info["simple_desc"]
                entry["created_at"] = str(deal_info["created_at"])
                entry["id"] = deal_info["id"]
                entry["min_price"] = deal_info["min_price"]
                entry["max_price"] = deal_info["max_price"]
                deals.append(entry)
            
            self.render("conversation.html", deals=deals, offset=offset, uid=uid)
        else:
            self.render("error.html", type=0, msg="No conversation exists")
        
        
        
        