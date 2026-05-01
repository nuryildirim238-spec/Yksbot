import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "yks_bot")

async def test_mongo():
    print(f"🔗 URI: {MONGO_URI}")
    print(f"📁 Database: {DB_NAME}")
    
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        await client.admin.command('ping')
        print("✅ MongoDB bağlantısı BAŞARILI!")
        
        # Bot token kontrolü
        BOT_TOKEN = os.getenv("BOT_TOKEN")
        if BOT_TOKEN:
            print("✅ BOT_TOKEN var!")
        else:
            print("❌ BOT_TOKEN yok!")
            
    except Exception as e:
        print(f"❌ HATA: {e}")

if __name__ == "__main__":
    asyncio.run(test_mongo())
