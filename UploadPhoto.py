#!/usr/bin/env python

#upload photo

import tornado.web
import tornado.httpserver
import tornado.database
import hashlib
from data.photo import PhotoData
from datetime import datetime


class UploadPhoto(tornado.web.RequestHandler):
    allowed_ext = ["jpg","jpeg","bmp","png"]
    @property
    def db(self):
        return self.application.db
    
    def post(self):
        files = self.request.files["deal_photo"]
        for f in files:
            content_type = f["content_type"]
            
            ext = content_type.split("/")[1]
            ext = ext.lower()
            if ext in UploadPhoto.allowed_ext:
                key = f["filename"]+str(datetime.now())
                m = hashlib.md5()
                m.update(key)
                new_filename = m.hexdigest()+"."+ext
                
                ff = open("static/upload_img/"+new_filename, "wb")
                ff.write(f["body"])
                ff.close()
                
                photo_data = PhotoData(self.db)
                pid = photo_data.insert_new_photo(new_filename)
                
                self.write("{\"filename\":\""+new_filename+"\", \"pid\":"+str(pid)+"}")
            else:
                self.write("{\"err\":\"invalid extension\"}");
            
            
        