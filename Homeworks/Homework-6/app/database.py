from pymongo import MongoClient
from app.config import config

client = MongoClient(config.MONGO_URI)
db = client[config.DB_NAME]

# Part 1 - Task Management
tasks_col = db["tasks"]

# Part 2 - AI Memory (reuses same DB, separate collections)
messages_col = db["messages"]
summaries_col = db["summaries"]
episodes_col = db["episodes"]
