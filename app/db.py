
# from pymongo import MongoClient
# import pymongo

# def get_database():
#     client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
#     try:
#         conn = client.server_info()
#         print(f'Connected to MongoDB {conn.get("version")}')
#     except Exception:
#         print("Unable to connect to the MongoDB server.")

#     db = client['portafolio']
#     User = db.users
#     User.create_index([("email", pymongo.ASCENDING)], unique=True)
#     return db

from pymongo import MongoClient
import pymongo
from app.config import settings

client = MongoClient("mongodb://nico:password@database:27017/fastapi?authSource=admin", serverSelectionTimeoutMS=5000)
try:
    conn = client.server_info()
    print(f'Connected to MongoDB {conn.get("version")}')
except Exception:
    print("Unable to connect to the MongoDB server.")

db = client['portafolio']
Project = db.projects
User = db.users
User.create_index([("email", pymongo.ASCENDING)], unique=True)