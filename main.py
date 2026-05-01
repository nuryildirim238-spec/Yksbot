import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from motor.motor_asyncio import AsyncIOMotorClient

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("✅ Bot çalışıyor! Telegram bağlantısı var.")

async def main():
    print("🚀 Bot başlatılıyor...")
    
    # MongoDB test
    if MONGO_URL:
        try:
            client = AsyncIOMotorClient(MONGO_URL)
            await client.admin.command('ping')
            print("✅ MongoDB bağlantısı doğrulandı!")
        except Exception as e:
            print(f"❌ MongoDB hatası: {e}")
    
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Bot hazır! /start yazabilirsin.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
