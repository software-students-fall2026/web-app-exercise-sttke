import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

client = MongoClient(
    os.environ["MONGO_URI"],
    serverSelectionTimeoutMS=10000
)

try:
    client.admin.command("ping")
    print("MongoDB connection successful!")
    print("Database:", os.environ["MONGO_DBNAME"])
except Exception as e:
    print("Connection failed:", e)
finally:
    client.close()