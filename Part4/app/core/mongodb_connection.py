from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, Any
import os
from contextlib import asynccontextmanager
class MongoDBConnection:
   client: AsyncIOMotorClient = None
   
   @classmethod
   async def connect_to_mongodb(cls):
       cls.client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
       return cls.client
       
   @classmethod
   async def close_mongodb_connection(cls):
       if cls.client:
           cls.client.close()
   
   @classmethod
   @asynccontextmanager
   async def get_collection(cls, db_name: str, collection_name: str):
       if not cls.client:
           await cls.connect_to_mongodb()
       collection = cls.client[db_name][collection_name]
       try:
           yield collection
       finally:
           pass
