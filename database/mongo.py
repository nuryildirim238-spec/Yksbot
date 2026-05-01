import os
from motor.motor_asyncio import AsyncIOMotorClient

# Doğrudan os.environ'dan oku (config.py'ye güvenme)
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "yks_bot")

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect(cls):
        """MongoDB'ye bağlan"""
        global MONGO_URI, DB_NAME
        
        if not MONGO_URI:
            print("❌ MONGO_URI environment variable bulunamadı!")
            return False
        
        try:
            cls.client = AsyncIOMotorClient(MONGO_URI)
            cls.db = cls.client[DB_NAME]
            
            # Ping atarak bağlantıyı test et
            await cls.client.admin.command('ping')
            
            # Index'ler
            await cls.db.users.create_index("user_id", unique=True)
            await cls.db.daily_logs.create_index([("user_id", 1), ("date", 1)], unique=True)
            await cls.db.subjects.create_index("name", unique=True)
            
            print("✅ MongoDB bağlantısı başarılı")
            print(f"📁 Database: {DB_NAME}")
            return True
        except Exception as e:
            print(f"❌ MongoDB bağlantı hatası: {e}")
            return False

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
