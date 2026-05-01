import os
from motor.motor_asyncio import AsyncIOMotorClient

# Railway otomatik olarak MONGO_URL değişkenini oluşturur
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "yks_bot")

class MongoDB:
    client = None
    db = None

    @classmethod
    async def connect(cls):
        if not MONGO_URL:
            print("❌ MONGO_URL bulunamadı!")
            print("📌 Railway'de MongoDB servisinin eklendiğinden emin ol!")
            return False
        
        print("🔄 MongoDB'ye bağlanılıyor...")
        print(f"📌 URL: {MONGO_URL[:50]}...")
        
        try:
            cls.client = AsyncIOMotorClient(MONGO_URL)
            cls.db = cls.client[DB_NAME]
            
            # Ping test
            await cls.client.admin.command('ping')
            print("✅ MongoDB bağlantısı başarılı!")
            
            # Index'ler
            await cls.db.users.create_index("user_id", unique=True)
            await cls.db.daily_logs.create_index([("user_id", 1), ("date", 1)], unique=True)
            await cls.db.subjects.create_index("name", unique=True)
            
            return True
        except Exception as e:
            print(f"❌ MongoDB bağlantı hatası: {e}")
            return False

    @classmethod
    def get_collection(cls, name):
        return cls.db[name]

db = MongoDB()
