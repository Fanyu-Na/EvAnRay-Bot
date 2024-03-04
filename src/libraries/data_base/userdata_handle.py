import json
from pathlib import Path
import random
import pymongo


class UserData(object):
    def __init__(self):
        username = 'atlaseuan'
        password = 'ysygfy980'
        host = '43.139.85.91'
        port = 21017
        database_name = 'admin'
        connection_string = f'mongodb://{username}:{password}@{host}:{port}/{database_name}'
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client['xray-mai-bot']
        self.userdata_collection = self.db['evanray_user_data']

    def getUserData(self,user_id:str):
        user_data = self.userdata_collection.find_one({"_id":user_id})
        if user_data:
            return user_data
        else:
            return {}
            # return self.userdata_collection.find_one({"_id":"maxscore"})
        
    def bindTencentUserId(self,user_id:str,tencent_user_id:str,user_name:str):
        data = {'tencent_user_id': tencent_user_id, "user_name":user_name}
        existing_data = self.userdata_collection.find_one({'_id': user_id})
        if existing_data:
            self.userdata_collection.update_one({'_id': user_id}, {'$set': data})
        else:
            data['_id'] = user_id
            self.userdata_collection.insert_one(data)

    def bindDivingFishUserId(self,user_id:str,divingfish_user_id:str,user_name:str):
        data = {'divingfish_user_id': divingfish_user_id, "user_name":user_name}
        existing_data = self.userdata_collection.find_one({'_id': user_id})
        if existing_data:
            self.userdata_collection.update_one({'_id': user_id}, {'$set': data})
        else:
            data['_id'] = user_id
            self.userdata_collection.insert_one(data)




userdata = UserData()
