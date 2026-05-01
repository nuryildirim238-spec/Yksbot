import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "yks_bot")

class MongoDB:
    client = None
    db = None

    @classmethod
    async def connect(cls):
        print(f"🔗 Bağlanılan: {MONGO_URL}")
        
        if not MONGO_URL:
            print("❌ MONGO_URL bulunamadı!")
            return
        
        try:
            cls.client = AsyncIOMotorClient(MONGO_URL)
            cls.db = cls.client[DB_NAME]
            await cls.client.admin.command('ping')
            
            await cls.db.users.create_index("user_id", unique=True)
            await cls.db.daily_logs.create_index([("user_id", 1), ("date", 1)], unique=True)
            await cls.db.subjects.create_index("name", unique=True)
            
            print("✅ MongoDB bağlantısı başarılı!")
        except Exception as e:
            print(f"❌ HATA: {e}")

    @classmethod
    def get_collection(cls, name):
        return cls.db[name]

db = MongoDB()
