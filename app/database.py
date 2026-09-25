#this file creates a single shared connnection to MongoDB using pymongo

from pymongo import MongoClient
from pymongo.database import Database

from app.config import settings

# MongoClient manages a pool of connections to the MongoDB server and is thread-safe.
client : MongoClient = MongoClient(settings.MONGO_URI)
database : Database = client[settings.MONGO_DB_NAME]

# Sends a ping command to MongoDB to confirm that the connection is alive.
def ping_database() -> bool:
    try:
        client.admin.command("ping")
        return True
    except Exception:
        return False