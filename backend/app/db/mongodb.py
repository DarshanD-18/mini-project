from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.db.indexes import ensure_indexes

client: AsyncIOMotorClient = None
db = None


async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    await ensure_indexes(db)
    print(f" Connected to MongoDB database: '{settings.DATABASE_NAME}'")


async def close_mongo_connection():
    global client
    if client:
        client.close()
        print(" MongoDB connection closed.")


def get_database():
    return db
