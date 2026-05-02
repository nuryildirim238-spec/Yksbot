from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from services.stats_service import StatsService
from services.user_service import UserService
from keyboards.inline import main_menu, nav_buttons
from utils.formatters import format_hours, format_questions
from database.mongo import db

router = Router()

@router.message(Command("work"))
async def work_command(message: Message, state: FSMContext):
    """
    /work komutu ile çalışma kaydı
    Kullanım: /work 3.5  (sadece saat)
    Kullanım: /work 3.5 120  (saat ve soru)
    """
    await state.clear()
    
    args = message.text.split()
    user_id = message.from_user.id
    
    # Mevcut log kontrolü
    existing_log = await StatsService.get_today_log(user_id)
    
    # Argümanları parse et
    hours = None
    questions = None
    
    if len(args) >= 2:
        try:
            hours = float(args[1].replace(",", "."))
        except ValueError:
            await message.answer(
                "❌ Geçersiz saat formatı!\n\n"
                "✅ Doğru kullanım:\n"
                "`/work 3.5` - sadece saat kaydeder\n"
                "`/work 3.5 120` - saat ve soru kaydeder\n"
                "`/soru 120` - sadece soru kaydeder",
                parse_mode="Markdown"
            )
            return
    
    if len(args) >= 3:
        try:
            questions = int(args[2])
        except ValueError:
            await message.answer(
                "❌ Geçersiz soru sayısı! Sayı giriniz.",
                parse_mode="Markdown"
            )
            return
    
    # Sadece soru komutu ayrıca ele alınacak
    if hours is None and questions is None:
        await message.answer(
            "❌ Lütfen çalışma saati veya soru sayısı girin!\n\n"
            "✅ Doğru kullanım:\n"
            "`/work 3.5` - 3.5 saat çalıştım\n"
            "`/work 3.5 120` - 3.5 saat çalıştım, 120 soru çözdüm\n"
            "`/soru 120` - 120 soru çözdüm",
            parse_mode="Markdown"
        )
        return
    
    # Günlük kaydı yap
    if existing_log:
        # Üzerine yazma onayı
        await state.update_data(
            pending_hours=hours,
            pending_questions=questions,
            existing_hours=existing_log.get("study_hours", 0),
            existing_questions=existing_log.get("questions", 0)
        )
        
        response = f"⚠️ **Bugün için zaten giriş yapmışsınız!** ⚠️\n\n"
        response += f"📊 Mevcut girişiniz:\n"
        response += f"⏱️ {format_hours(existing_log.get('study_hours', 0))}\n"
        response += f"📝 {format_questions(existing_log.get('questions', 0))}\n\n"
        
        if hours is not None:
            response += f"📝 Yeni saat: {format_hours(hours)}\n"
        if questions is not None:
            response += f"📝 Yeni soru: {format_questions(questions)}\n\n"
        
        response += f"**Üzerine yazmak istiyor musunuz?**"
        
        await message.answer(
            response,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Evet, Güncelle", callback_data="confirm_overwrite_yes")],
                [InlineKeyboardButton(text="❌ Hayır, İptal", callback_data="confirm_overwrite_no")],
                [InlineKeyboardButton(text="🏠 Ana Menü", callback_data="main_menu")]
            ]),
            parse_mode="Markdown"
        )
        return
    
    # Normal kayıt
    result_text = await save_daily_log(user_id, hours, questions, is_update=False)
    await message.answer(result_text, reply_markup=main_menu(), parse_mode="Markdown")

@router.message(Command("soru"))
async def question_command(message: Message, state: FSMContext):
    """
    /soru komutu ile sadece soru kaydı
    Kullanım: /soru 120
    """
    await state.clear()
    
    args = message.text.split()
    user_id = message.from_user.id
    
    if len(args) < 2:
        await message.answer(
            "❌ Lütfen soru sayısını girin!\n\n"
            "✅ Doğru kullanım: `/soru 120`\n"
            "*(120 soru çözdüm anlamına gelir)*",
            parse_mode="Markdown"
        )
        return
    
    try:
        questions = int(args[1])
    except ValueError:
        await message.answer(
            "❌ Geçersiz soru sayısı! Sayı giriniz.\n\n"
            "✅ Örnek: `/soru 120`",
            parse_mode="Markdown"
        )
        return
    
    existing_log = await StatsService.get_today_log(user_id)
    
    if existing_log:
        await state.update_data(
            pending_hours=None,
            pending_questions=questions,
            existing_hours=existing_log.get("study_hours", 0),
            existing_questions=existing_log.get("questions", 0)
        )
        
        response = f"⚠️ **Bugün için zaten giriş yapmışsınız!** ⚠️\n\n"
        response += f"📊 Mevcut girişiniz:\n"
        response += f"⏱️ {format_hours(existing_log.get('study_hours', 0))}\n"
        response += f"📝 {format_questions(existing_log.get('questions', 0))}\n\n"
        response += f"📝 Yeni soru: {format_questions(questions)}\n\n"
        response += f"**Üzerine yazmak istiyor musunuz?**"
        
        await message.answer(
            response,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Evet, Güncelle", callback_data="confirm_overwrite_yes")],
                [InlineKeyboardButton(text="❌ Hayır, İptal", callback_data="confirm_overwrite_no")],
                [InlineKeyboardButton(text="🏠 Ana Menü", callback_data="main_menu")]
            ]),
            parse_mode="Markdown"
        )
        return
    
    result_text = await save_daily_log(user_id, None, questions, is_update=False)
    await message.answer(result_text, reply_markup=main_menu(), parse_mode="Markdown")

async def save_daily_log(user_id: int, hours: float, questions: int, is_update: bool = False):
    """Günlük log kaydetme işlemi"""
    
    if is_update:
        # Güncelleme durumunda eski değerleri düş
        user = await UserService.get_user(user_id)
        old_hours = user.get("stats", {}).get("total_study_hours", 0)
        old_questions = user.get("stats", {}).get("total_questions", 0)
        
        # Bu mantık daha önceki gibi çalışacak
        # Şimdilik basit tutalım, gerekirse detaylandırırız
    
    # Mevcut logu al veya oluştur
    existing = await StatsService.get_today_log(user_id)
    
    new_hours = hours if hours is not None else (existing.get("study_hours") if existing else 0)
    new_questions = questions if questions is not None else (existing.get("questions") if existing else 0)
    
    # Log kaydet
    await StatsService.add_daily_log(user_id, new_hours, new_questions)
    
    # İstatistikleri güncelle (değişim hesapla)
    collection = db.get_collection("users")
    user = await UserService.get_user(user_id)
    
    old_total_hours = user.get("stats", {}).get("total_study_hours", 0)
    old_total_questions = user.get("stats", {}).get("total_questions", 0)
    old_total_days = user.get("stats", {}).get("total_days", 0)
    
    if existing:
        # Güncelleme: eski değerleri düş, yeni ekle
        old_hours = existing.get("study_hours", 0)
        old_qs = existing.get("questions", 0)
        
        new_total_hours = old_total_hours - old_hours + new_hours
        new_total_questions = old_total_questions - old_qs + new_questions
        
        await collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "stats.total_study_hours": new_total_hours,
                "stats.total_questions": new_total_questions
            }}
        )
    else:
        # Yeni kayıt
        await UserService.update_stats(user_id, new_hours, new_questions)
    
    # Sonuç mesajı oluştur
    result = f"✅ **Günlük giriş başarıyla kaydedildi!** ✅\n\n"
    result += f"📊 Bugün:\n"
    
    if hours is not None:
        result += f"⏱️ {format_hours(hours)} çalıştın\n"
    if questions is not None:
        result += f"📝 {format_questions(questions)} soru çözdün\n"
    
    result += f"\n🎯 Hedeflerine bir gün daha yaklaştın!\n\n"
    result += f"💡 İpucu: Yarın `/work 4 150` yazarak tekrar hızlıca kayıt yapabilirsin!"
    
    return result

@router.callback_query(F.data == "confirm_overwrite_yes")
async def confirm_overwrite(callback: CallbackQuery, state: FSMContext):
    """Üzerine yazmayı onayla"""
    data = await state.get_data()
    hours = data.get("pending_hours")
    questions = data.get("pending_questions")
    user_id = callback.from_user.id
    
    result_text = await save_daily_log(user_id, hours, questions, is_update=True)
    await state.clear()
    
    await callback.message.edit_text(result_text, reply_markup=main_menu(), parse_mode="Markdown")
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

@router.callback_query(F.data == "daily")
async def daily_menu(callback: CallbackQuery):
    """Günlük giriş menüsü (komutları hatırlat)"""
    await callback.message.edit_text(
        "📝 **Günlük Çalışma Takibi** 📝\n\n"
        "Aşağıdaki komutları kullanarak hızlıca giriş yapabilirsin:\n\n"
        "`/work 3.5` - 3.5 saat çalıştım\n"
        "`/work 3.5 120` - 3.5 saat çalıştım, 120 soru çözdüm\n"
        "`/soru 120` - 120 soru çözdüm\n\n"
        "Örnek: `/work 4 150` yazarak 4 saat çalıştığını ve 150 soru çözdüğünü tek mesajda kaydedebilirsin! 🚀\n\n"
        "**Not:** Aynı gün tekrar kayıt yaparsan, üzerine yazman istenecektir.",
        reply_markup=nav_buttons(home_callback="main_menu"),
        parse_mode="Markdown"
    )
    await callback.answer()
            
