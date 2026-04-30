from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME

class MongoDB:
    client = None
    db = None

    @classmethod
    async def connect(cls):
        """MongoDB'ye bağlan"""
        cls.client = AsyncIOMotorClient(MONGO_URI)
        cls.db = cls.client[DB_NAME]
        
        # Index'ler (sorguları hızlandırır)
        await cls.db.users.create_index("user_id", unique=True)
        await cls.db.daily_logs.create_index([("user_id", 1), ("date", 1)], unique=True)
        await cls.db.subjects.create_index("name", unique=True)
        
        print("✅ MongoDB bağlantısı başarılı")

    @classmethod
    async def close(cls):
        """Bağlantıyı kapat"""
        if cls.client:
            cls.client.close()
            print("✅ MongoDB bağlantısı kapandı")

    @classmethod
    def get_collection(cls, name):
        """Collection'a eriş"""
        return cls.db[name]

# Global instance
db = MongoDB()
