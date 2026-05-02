from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from services.stats_service import StatsService
from services.user_service import UserService
from keyboards.inline import main_menu, nav_buttons
from utils.formatters import format_hours, format_questions
from database.mongo import db

router = Router()

# /work komutu - saat ve isteğe bağlı soru
@router.message(Command("work"))
async def work_command(message: Message):
    args = message.text.split()
    user_id = message.from_user.id
    
    # Argümanları kontrol et
    if len(args) < 2:
        await message.answer(
            "❌ Lutfen calisma saati girin!\n\n"
            "✅ Dogru kullanim:\n"
            "• `/work 3.5` - 3.5 saat calistim\n"
            "• `/work 3.5 120` - 3.5 saat calistim, 120 soru cozdum\n"
            "• `/soru 120` - 120 soru cozdum",
            parse_mode="Markdown"
        )
        return
    
    try:
        hours = float(args[1].replace(",", "."))
        if hours < 0 or hours > 24:
            await message.answer("❌ 0-24 arasinda bir saat giriniz!")
            return
    except ValueError:
        await message.answer("❌ Gecersiz saat! Ornek: `/work 3.5`")
        return
    
    questions = None
    if len(args) >= 3:
        try:
            questions = int(args[2])
            if questions < 0 or questions > 5000:
                await message.answer("❌ 0-5000 arasinda soru sayisi giriniz!")
                return
        except ValueError:
            await message.answer("❌ Gecersiz soru sayisi!")
            return
    
    existing_log = await StatsService.get_today_log(user_id)
    
    if existing_log:
        # Guncelleme durumu
        old_hours = existing_log.get("study_hours", 0)
        old_qs = existing_log.get("questions", 0)
        
        # Yeni degerler
        new_hours = hours
        new_questions = questions if questions is not None else old_qs
        
        await StatsService.add_daily_log(user_id, new_hours, new_questions)
        
        # Istatistikleri guncelle
        user = await UserService.get_user(user_id)
        old_total_hours = user.get("stats", {}).get("total_study_hours", 0)
        old_total_questions = user.get("stats", {}).get("total_questions", 0)
        
        new_total_hours = old_total_hours - old_hours + new_hours
        new_total_questions = old_total_questions - old_qs + new_questions
        
        await db.get_collection("users").update_one(
            {"user_id": user_id},
            {"$set": {
                "stats.total_study_hours": new_total_hours,
                "stats.total_questions": new_total_questions
            }}
        )
        
        await message.answer(
            f"✅ **Gunluk giris GUNCELLENDI!** ✅\n\n"
            f"📊 Bugun:\n"
            f"⏱️ {format_hours(new_hours)} calistin\n"
            f"📝 {format_questions(new_questions)} soru cozdun\n\n"
            f"Eski degerler: {format_hours(old_hours)} / {format_questions(old_qs)}",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )
    else:
        # Yeni kayit
        await StatsService.add_daily_log(user_id, hours, questions or 0)
        await UserService.update_stats(user_id, hours, questions or 0)
        
        msg = f"✅ **Gunluk giris basariyla kaydedildi!** ✅\n\n"
        msg += f"📊 Bugun:\n"
        msg += f"⏱️ {format_hours(hours)} calistin\n"
        if questions:
            msg += f"📝 {format_questions(questions)} soru cozdun\n"
        msg += f"\n🎯 Hedeflerine bir gun daha yaklastin!"
        
        await message.answer(msg, reply_markup=main_menu(), parse_mode="Markdown")

# /soru komutu - sadece soru
@router.message(Command("soru"))
async def question_command(message: Message):
    args = message.text.split()
    user_id = message.from_user.id
    
    if len(args) < 2:
        await message.answer(
            "❌ Lutfen soru sayisini girin!\n\n"
            "✅ Dogru kullanim: `/soru 120`\n"
            "*(120 soru cozdum anlamina gelir)*",
            parse_mode="Markdown"
        )
        return
    
    try:
        questions = int(args[1])
        if questions < 0 or questions > 5000:
            await message.answer("❌ 0-5000 arasinda soru sayisi giriniz!")
            return
    except ValueError:
        await message.answer("❌ Gecersiz soru sayisi! Ornek: `/soru 120`")
        return
    
    existing_log = await StatsService.get_today_log(user_id)
    
    if existing_log:
        # Mevcut kayit var, guncelle
        old_hours = existing_log.get("study_hours", 0)
        old_qs = existing_log.get("questions", 0)
        
        await StatsService.add_daily_log(user_id, old_hours, questions)
        
        # Istatistikleri guncelle
        user = await UserService.get_user(user_id)
        old_total_questions = user.get("stats", {}).get("total_questions", 0)
        new_total_questions = old_total_questions - old_qs + questions
        
        await db.get_collection("users").update_one(
            {"user_id": user_id},
            {"$set": {"stats.total_questions": new_total_questions}}
        )
        
        await message.answer(
            f"✅ **Soru sayisi GUNCELLENDI!** ✅\n\n"
            f"📊 Bugun:\n"
            f"📝 {format_questions(questions)} soru cozdun\n\n"
            f"Eski soru sayisi: {format_questions(old_qs)}",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )
    else:
        # Yeni kayit (sadece soru, saat 0)
        await StatsService.add_daily_log(user_id, 0, questions)
        await UserService.update_stats(user_id, 0, questions)
        
        await message.answer(
            f"✅ **{format_questions(questions)} soru kaydedildi!** ✅\n\n"
            f"📊 Calisma saatinizi de eklemek icin `/work 3.5` yazabilirsiniz.",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )

# Buton ile gunluk giris (komutlari hatirlat)
@router.callback_query(F.data == "daily")
async def daily_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📝 **Gunluk Calisma Takibi** 📝\n\n"
        "Asagidaki komutlari kullanarak hizlica giris yapabilirsin:\n\n"
        "`/work 3.5` - 3.5 saat calistim\n"
        "`/work 3.5 120` - 3.5 saat calistim, 120 soru cozdum\n"
        "`/soru 120` - 120 soru cozdum\n\n"
        "Ornek: `/work 4 150` yazarak 4 saat calistigini ve 150 soru cozdugunu tek mesajda kaydedebilirsin!\n\n"
        "**Not:** Ayni gun tekrar kayit yaparsan, ustune yazilir.",
        reply_markup=nav_buttons(home_callback="main_menu"),
        parse_mode="Markdown"
    )
    await callback.answer()
