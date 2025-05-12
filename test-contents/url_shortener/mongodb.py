from pymongo import MongoClient
from django.conf import settings

def get_mongodb_connection():
    client = MongoClient(settings.MONGODB_URI)
    db = client.shorty_db
    return db

def get_urls_collection():
    db = get_mongodb_connection()
    return db.urls

