import os
from motor.motor_asyncio import AsyncIOMotorClient
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

MONGO_URL = os.getenv("MONGO_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_NAME = os.getenv("DB_NAME", "yks_bot")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher()

class MongoDB:
    client = None
    db = None

    @classmethod
    async def connect(cls):
        if not MONGO_URL:
            print("❌ MONGO_URL bulunamadı!")
            return False
        
        try:
            cls.client = AsyncIOMotorClient(MONGO_URL)
            cls.db = cls.client[DB_NAME]
            await cls.client.admin.command('ping')
            
            await cls.db.users.create_index("user_id", unique=True)
            await cls.db.daily_logs.create_index([("user_id", 1), ("date", 1)], unique=True)
            await cls.db.subjects.create_index("name", unique=True)
            
            print("✅ MongoDB bağlantısı başarılı!")
            return True
        except Exception as e:
            print(f"❌ HATA: {e}")
            return False

    @classmethod
    def get_collection(cls, name):
        return cls.db[name]

db = MongoDB()
