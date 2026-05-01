import asyncio
import os
import sys

# Proje kök dizinini ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Database
from database.mongo import db

# Services
from services.subject_service import SubjectService

# Handlers
from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.profile import router as profile_router
from handlers.daily import router as daily_router
from handlers.update import router as update_router
from handlers.survey import router as survey_router

async def main():
    print("🚀 Bot başlatılıyor...")
    
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN bulunamadı!")
        return
    
    # MongoDB'ye bağlan
    await db.connect()
    
    # Default dersleri yükle
    await SubjectService.init_default_subjects()
    
    # Bot'u başlat
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)
    dp = Dispatcher()
    
    # Router'ları ekle
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(profile_router)
    dp.include_router(daily_router)
    dp.include_router(update_router)
    dp.include_router(survey_router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Bot başlatıldı!")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
