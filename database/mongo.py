import os
from motor.motor_asyncio import AsyncIOMotorClient

# SADECE Railway'in MONGO_URI'sini kullan
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "yks_bot")

class MongoDB:
    client = None
    db = None

    @classmethod
    async def connect(cls):
        print(f"🔗 Bağlanılıyor: {MONGO_URI[:50]}...")
        
        if not MONGO_URI:
            print("❌ MONGO_URI bulunamadı!")
            return
        
        try:
            # SSL sorunlarını aşmak için
            cls.client = AsyncIOMotorClient(
                MONGO_URI,
                tlsAllowInvalidCertificates=True,
                serverSelectionTimeoutMS=10000
            )
            cls.db = cls.client[DB_NAME]
            
            # Ping test
            await cls.client.admin.command('ping')
            
            # Index'ler
            await cls.db.users.create_index("user_id", unique=True)
            await cls.db.daily_logs.create_index([("user_id", 1), ("date", 1)], unique=True)
            await cls.db.subjects.create_index("name", unique=True)
            
            print(f"✅ MongoDB bağlantısı başarılı! Database: {DB_NAME}")
            
        except Exception as e:
            print(f"❌ MongoDB bağlantı hatası: {e}")

    @classmethod
    def get_collection(cls, name):
        return cls.db[name]

db = MongoDB()
