
from pymongo import MongoClient
from app.config import settings

Mongo_URL = settings.MONGODB_URI


client = MongoClient(Mongo_URL)
db = client.InsightEdge


def get_db():
    return db


    
  