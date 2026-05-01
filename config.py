import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("DB_NAME")
    
    # Validasyon
    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("❌ BOT_TOKEN bulunamadı!")
        if not cls.MONGO_URI:
            raise ValueError("❌ MONGO_URI bulunamadı!")
        print("✅ Config validation passed")

config = Config()
