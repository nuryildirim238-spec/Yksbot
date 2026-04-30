import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config import config
from database.mongo import db
from services.subject_service import SubjectService

# Handler'ları import et
from handlers import start, menu, profile, daily, update, survey

logging.basicConfig(level=logging.INFO)

async def main():
    """Botu başlat"""
    
    # MongoDB'ye bağlan
    await db.connect()
    
    # Default ders/konu listesini kontrol et/yükle
    await SubjectService.init_default_subjects()
    
    # Bot'u başlat
    bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)
    dp = Dispatcher()
    
    # Router'ları ekle
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(profile.router)
    dp.include_router(daily.router)
    dp.include_router(update.router)
    dp.include_router(survey.router)
    
    # Botu başlat
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Bot başlatıldı!")
    print(f"🤖 Bot: @{(await bot.get_me()).username}")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
