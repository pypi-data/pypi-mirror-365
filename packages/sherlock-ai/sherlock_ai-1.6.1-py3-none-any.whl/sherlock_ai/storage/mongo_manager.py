from pymongo import MongoClient
import os

class MongoManager:
    def __init__(self, mongo_uri=None):
        """
        mongo_uri: MongoDB connection string (optional). 
        If not provided, MongoDB saving will be disabled.
        """
        self.mongo_uri = mongo_uri or os.getenv("MONGO_URI")
        if self.mongo_uri:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client["sherlock-meta"]         # Fixed database name
            self.collection = self.db["error-insights"]    # Fixed collection name
            self.enabled = True
            print("✅ MongoDB backend enabled (DB: sherlock-meta, Collection: error-insights).")
        else:
            self.client = None
            self.enabled = False
            print("ℹ️ MongoDB backend not configured.")

    def save(self, data):
        """
        Saves data (Python dict) to MongoDB if backend is enabled.
        """
        if self.enabled:
            self.collection.insert_one(data)
            print("✅ Saved error insight to MongoDB (sherlock-meta.error-insights).")
        else:
            print("ℹ️ Skipping MongoDB save (backend disabled).")
