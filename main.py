import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

from database.mongo import db
from services.subject_service import SubjectService
from handlers import start, menu, profile, daily, update, survey

async def main():
    print("🚀 Bot başlatılıyor...")
    
    # MongoDB bağlantısı
    connected = await db.connect()
    if not connected:
        print("❌ MongoDB bağlanamadı! Bot kapatılıyor...")
        return
    
    # Default dersler
    await SubjectService.init_default_subjects()
    
    # ÖNEMLİ: Router sıralaması - spesifik handler'lar önce, genel handler en sonda!
    dp.include_router(start.router)
    dp.include_router(daily.router)      # /work ve /soru komutları için
    dp.include_router(profile.router)
    dp.include_router(update.router)
    dp.include_router(survey.router)
    dp.include_router(menu.router)       # Genel mesaj yakalayıcı EN SONDA olmalı!
    
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Bot hazır!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
