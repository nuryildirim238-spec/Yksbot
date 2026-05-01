import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "yks_bot")

class MongoDB:
    client = None
    db = None

    @classmethod
    async def connect(cls):
        print(f"🔗 MongoDB bağlantısı deneniyor...")
        print(f"📌 MONGO_URL: {MONGO_URL[:50] if MONGO_URL else 'YOK'}...")
        
        if not MONGO_URL:
            print("❌ MONGO_URL environment variable bulunamadı!")
            return False
        
        try:
            cls.client = AsyncIOMotorClient(MONGO_URL)
            cls.db = cls.client[DB_NAME]
            
            # Ping ile test et
            await cls.client.admin.command('ping')
            
            # Index'ler
            await cls.db.users.create_index("user_id", unique=True)
            await cls.db.daily_logs.create_index([("user_id", 1), ("date", 1)], unique=True)
            await cls.db.subjects.create_index("name", unique=True)
            
            print(f"✅ MongoDB bağlantısı başarılı! Database: {DB_NAME}")
            return True
            
        except Exception as e:
            print(f"❌ MongoDB bağlantı hatası: {e}")
            return False

    @classmethod
    def get_collection(cls, name):
        if cls.db is None:
            print(f"❌ HATA: MongoDB bağlı değil! '{name}' koleksiyonu alınamadı.")
            return None
        return cls.db[name]

db = MongoDB()
