import pymongo
from bson.objectid import ObjectId

client = pymongo.MongoClient('localhost', 27017)
db = client['TimeTable']

def add_task (user_id, date, task, completed=False):
    #"u" is prefix for chat_id
    collection = db[f"u{str(user_id)}"]
    collection.insert_one({"task":task, "date":date, "completed":completed})
    

def get_day(user_id, date):
    collection = db[f"u{str(user_id)}"]
    day = list(collection.find({"date":date}))
    if (day == []):
        return None
    else:
        return day

def change_completed(user_id, task_id):
    collection = db[f"u{str(user_id)}"]
    completed = collection.find_one({"_id":ObjectId(task_id)}, {"completed":True, "_id":False})["completed"]
    collection.update_one({"_id":ObjectId(task_id)}, {"$set":{"completed":not completed}})


def delete_task(user_id, task_id):
    collection = db[f"u{str(user_id)}"]
    collection.delete_one({"_id":ObjectId(task_id)})


def create_users_document(user_id):
    collection = db["users"]
    collection.insert_one({"_id":user_id})


def set_current_date(user_id, date):
    collection = db["users"]
    collection.update_one({"_id":user_id}, {"$set":{"date":date}})


def get_current_date(user_id):
    collection = db["users"]
    date = collection.find_one({"_id":user_id}, {"_id":False})
    #date is dict like {"date":"1.2.2022"}
    return date["date"]


def set_message_id(user_id, message_id):
    collection = db["users"]
    collection.update_one({"_id":user_id}, {"$set":{"message_id":message_id}})


def get_message_id(user_id):
    collection = db["users"]
    message_id = collection.find_one({"_id":user_id}, {"_id":False})
    #message_id is dict like {"message_id":"324325325"}
    return message_id["message_id"]