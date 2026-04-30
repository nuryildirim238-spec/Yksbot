from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from services.stats_service import StatsService
from services.user_service import UserService
from keyboards.inline import main_menu, nav_buttons, cancel_button
from utils.formatters import format_hours, format_questions
from database.mongo import db
router = Router()

class DailyState(StatesGroup):
    waiting_hours = State()
    waiting_questions = State()
    confirm_overwrite = State()

@router.callback_query(F.data == "daily")
async def daily_entry(callback: CallbackQuery, state: FSMContext):
    """Günlük giriş başlat"""
    user_id = callback.from_user.id
    
    # Bugün giriş yapılmış mı kontrol et
    existing_log = await StatsService.get_today_log(user_id)
    
    if existing_log:
        # Var olan giriş varsa, üzerine yazmak isteyip istemediğini sor
        await state.update_data(existing_hours=existing_log.get("study_hours", 0))
        await state.update_data(existing_questions=existing_log.get("questions", 0))
        await state.set_state(DailyState.confirm_overwrite)
        
        await callback.message.edit_text(
            f"⚠️ **Bugün için zaten giriş yapmışsınız!** ⚠️\n\n"
            f"📊 Mevcut girişiniz:\n"
            f"⏱️ {format_hours(existing_log.get('study_hours', 0))}\n"
            f"📝 {format_questions(existing_log.get('questions', 0))}\n\n"
            f"**Bu girişin üzerine yazmak istiyor musunuz?**",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Evet, Güncelle", callback_data="confirm_overwrite_yes")],
                [InlineKeyboardButton(text="❌ Hayır, İptal", callback_data="confirm_overwrite_no")],
                [InlineKeyboardButton(text="🏠 Ana Menü", callback_data="main_menu")]
            ])
        )
        await callback.answer()
        return
    
    await state.set_state(DailyState.waiting_hours)
    await callback.message.edit_text(
        "📝 **Günlük Çalışma Takibi** 📝\n\n"
        "Bugün kaç **saat** çalıştın?\n\n"
        "*(Örnek: 4, 2.5, 3.75)*",
        reply_markup=cancel_button()
    )
    await callback.answer()

@router.callback_query(F.data == "confirm_overwrite_yes")
async def confirm_overwrite(callback: CallbackQuery, state: FSMContext):
    """Üzerine yazmayı onayla"""
    await state.set_state(DailyState.waiting_hours)
    await callback.message.edit_text(
        "📝 **Günlük Çalışma Takibi - Güncelleme** 📝\n\n"
        "Bugün kaç **saat** çalıştın?\n\n"
        "*(Örnek: 4, 2.5, 3.75)*",
        reply_markup=cancel_button()
    )
    await callback.answer()

@router.callback_query(F.data == "confirm_overwrite_no")
async def cancel_overwrite(callback: CallbackQuery, state: FSMContext):
    """Üzerine yazmayı iptal et"""
    await state.clear()
    await callback.message.edit_text(
        "❌ Güncelleme iptal edildi. Mevcut girişiniz korundu.\n\n"
        "Ana menüye döndünüz.",
        reply_markup=main_menu()
    )
    await callback.answer()

@router.message(DailyState.waiting_hours)
async def get_hours(message: Message, state: FSMContext):
    """Çalışma saatini al"""
    try:
        hours = float(message.text.replace(",", "."))
        
        if hours < 0 or hours > 24:
            await message.answer(
                "❌ Lütfen 0-24 arasında geçerli bir saat girin:",
                reply_markup=cancel_button()
            )
            return
        
        await state.update_data(hours=hours)
        await state.set_state(DailyState.waiting_questions)
        
        await message.answer(
            f"✅ {format_hours(hours)} çalışma kaydedildi.\n\n"
            "Şimdi, bugün kaç **soru** çözdün?\n\n"
            "*(Örnek: 120, 45, 200)*",
            reply_markup=cancel_button()
        )
        
    except ValueError:
        await message.answer(
            "❌ Lütfen geçerli bir sayı girin (Örnek: 4, 2.5):",
            reply_markup=cancel_button()
        )

@router.message(DailyState.waiting_questions)
async def get_questions(message: Message, state: FSMContext):
    """Soru sayısını al ve kaydet"""
    try:
        questions = int(message.text)
        
        if questions < 0 or questions > 5000:
            await message.answer(
                "❌ Lütfen 0-5000 arasında geçerli bir sayı girin:",
                reply_markup=cancel_button()
            )
            return
        
        data = await state.get_data()
        hours = data.get("hours")
        existing_hours = data.get("existing_hours")
        existing_questions = data.get("existing_questions")
        
        user_id = message.from_user.id
        
        # Günlük log kaydet (upsert ile üzerine yazar)
        await StatsService.add_daily_log(user_id, hours, questions)
        
        # Kullanıcı istatistiklerini güncelle
        # Eğer eski veri varsa, onu çıkarıp yenisini ekle
        if existing_hours is not None and existing_questions is not None:
            # Eski değerleri düş, yenileri ekle
            user = await UserService.get_user(user_id)
            old_total_hours = user.get("stats", {}).get("total_study_hours", 0)
            old_total_questions = user.get("stats", {}).get("total_questions", 0)
            old_total_days = user.get("stats", {}).get("total_days", 0)
            
            # Düzeltilmiş değerler
            new_total_hours = old_total_hours - existing_hours + hours
            new_total_questions = old_total_questions - existing_questions + questions
            
            # Güncelle
            collection = db.get_collection("users")
            await collection.update_one(
                {"user_id": user_id},
                {"$set": {
                    "stats.total_study_hours": new_total_hours,
                    "stats.total_questions": new_total_questions
                }}
            )
        else:
            await UserService.update_stats(user_id, hours, questions)
        
        await state.clear()
        
        await message.answer(
            f"✅ **Günlük giriş başarıyla kaydedildi!** ✅\n\n"
            f"📊 Bugün:\n"
            f"⏱️ {format_hours(hours)} çalıştın\n"
            f"📝 {format_questions(questions)} soru çözdün\n\n"
            f"🎯 Hedeflerine bir gün daha yaklaştın!\n\n"
            f"Yarın tekrar bekleriz.",
            reply_markup=main_menu()
        )
        
    except ValueError:
        await message.answer(
            "❌ Lütfen geçerli bir sayı girin (Örnek: 120):",
            reply_markup=cancel_button()
        )
