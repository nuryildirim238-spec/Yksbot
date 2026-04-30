from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from services.stats_service import StatsService
from services.user_service import UserService
from keyboards.inline import main_menu, nav_buttons, cancel_button
from utils.formatters import format_hours, format_questions

router = Router()

class DailyState(StatesGroup):
    waiting_hours = State()
    waiting_questions = State()

@router.callback_query(F.data == "daily")
async def daily_entry(callback: CallbackQuery, state: FSMContext):
    """Günlük giriş başlat"""
    user_id = callback.from_user.id
    
    # Bugün giriş yapılmış mı kontrol et
    has_entry = await StatsService.has_daily_entry(user_id)
    
    if has_entry:
        await callback.message.edit_text(
            "⚠️ **Bugün için zaten giriş yapmışsınız!** ⚠️\n\n"
            "Her gün için sadece bir giriş yapabilirsiniz.\n"
            "Yarın tekrar bekleriz. 📅",
            reply_markup=nav_buttons(home_callback="main_menu")
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
        
        user_id = message.from_user.id
        
        # Günlük log kaydet
        await StatsService.add_daily_log(user_id, hours, questions)
        
        # Kullanıcı istatistiklerini güncelle
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
