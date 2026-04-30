from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from services.subject_service import SubjectService
from services.user_service import UserService
from keyboards.inline import subject_menu, topic_menu, score_buttons, nav_buttons, main_menu

router = Router()

class UpdateState(StatesGroup):
    selecting_subject = State()
    selecting_topic = State()

@router.callback_query(F.data == "update_subjects")
async def start_update(callback: CallbackQuery, state: FSMContext):
    """Konu güncellemeyi başlat"""
    subjects = await SubjectService.get_all_subjects()
    
    if not subjects:
        await callback.message.edit_text(
            "❌ Sistem hatası: Ders listesi bulunamadı.\n"
            "Lütfen daha sonra tekrar deneyin.",
            reply_markup=nav_buttons(home_callback="main_menu")
        )
        await callback.answer()
        return
    
    await state.set_state(UpdateState.selecting_subject)
    await callback.message.edit_text(
        "📚 **Konu Güncelleme** 📚\n\n"
        "Hangi dersin konusunu güncellemek istiyorsun?",
        reply_markup=subject_menu(subjects)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("subject_"))
async def select_subject(callback: CallbackQuery, state: FSMContext):
    """Ders seçildi"""
    subject_name = callback.data.replace("subject_", "")
    
    # Dersin varlığını kontrol et
    exists = await SubjectService.subject_exists(subject_name)
    if not exists:
        await callback.message.edit_text(
            "❌ Geçersiz ders seçimi.",
            reply_markup=nav_buttons(home_callback="main_menu")
        )
        await callback.answer()
        return
    
    topics = await SubjectService.get_topics_by_subject(subject_name)
    
    if not topics:
        await callback.message.edit_text(
            f"❌ {subject_name.title()} dersi için konu bulunamadı.",
            reply_markup=nav_buttons(back_callback="update_subjects", home_callback="main_menu")
        )
        await callback.answer()
        return
    
    await state.update_data(selected_subject=subject_name)
    await state.set_state(UpdateState.selecting_topic)
    
    await callback.message.edit_text(
        f"📖 **{subject_name.title()}** dersi için hangi konuyu güncellemek istiyorsun?",
        reply_markup=topic_menu(subject_name, topics)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("topic_"))
async def select_topic(callback: CallbackQuery, state: FSMContext):
    """Konu seçildi"""
    data = callback.data.replace("topic_", "")
    parts = data.split("_", 1)
    
    if len(parts) != 2:
        await callback.message.edit_text(
            "❌ Hatalı konu seçimi.",
            reply_markup=nav_buttons(home_callback="main_menu")
        )
        await callback.answer()
        return
    
    subject_name = parts[0]
    topic_name = parts[1]
    
    await state.update_data(selected_topic=topic_name)
    
    await callback.message.edit_text(
        f"📊 **{subject_name.title()} - {topic_name.title()}**\n\n"
        f"Bu konudaki seviyeni 0-100 arasında puanla:\n\n"
        f"💯 100: Çok iyi hakimim\n"
        f"📌 50: Orta seviyeyim\n"
        f"⚠️ 0: Hiç bilmiyorum",
        reply_markup=score_buttons(subject_name, topic_name)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("score_"))
async def save_score(callback: CallbackQuery, state: FSMContext):
    """Puanı kaydet"""
    data = callback.data.replace("score_", "")
    parts = data.split("_")
    
    if len(parts) != 3:
        await callback.message.edit_text(
            "❌ Hatalı puan seçimi.",
            reply_markup=nav_buttons(home_callback="main_menu")
        )
        await callback.answer()
        return
    
    subject_name = parts[0]
    topic_name = parts[1]
    score = int(parts[2])
    
    user_id = callback.from_user.id
    
    # Puanı kaydet
    await UserService.update_subject_score(user_id, subject_name, topic_name, score)
    
    await state.clear()
    
    # Başarı mesajı
    if score >= 80:
        emoji = "🎉"
        message_text = "Harika! Bu konuda çok iyisin!"
    elif score >= 50:
        emoji = "👍"
        message_text = "Güzel! Biraz daha çalışmayla mükemmel olacak."
    else:
        emoji = "📚"
        message_text = "Tamam! Bu konuya biraz daha zaman ayıralım."
    
    await callback.message.edit_text(
        f"{emoji} **Konu Güncellendi!** {emoji}\n\n"
        f"📖 {subject_name.title()} - {topic_name.title()}\n"
        f"📊 Yeni Puan: **{score}**\n\n"
        f"{message_text}\n\n"
        f"Başka bir konu güncellemek için ana menüden "
        f'"📚 Konularımı Güncelle" seçeneğini kullanabilirsin.',
        reply_markup=main_menu()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("back_to_topics_"))
async def back_to_topics(callback: CallbackQuery, state: FSMContext):
    """Konu listesine geri dön"""
    subject_name = callback.data.replace("back_to_topics_", "")
    
    topics = await SubjectService.get_topics_by_subject(subject_name)
    
    await state.set_state(UpdateState.selecting_topic)
    await state.update_data(selected_subject=subject_name)
    
    await callback.message.edit_text(
        f"📖 **{subject_name.title()}** dersi için hangi konuyu güncellemek istiyorsun?",
        reply_markup=topic_menu(subject_name, topics)
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_subjects")
async def back_to_subjects(callback: CallbackQuery, state: FSMContext):
    """Ders listesine geri dön"""
    subjects = await SubjectService.get_all_subjects()
    
    await state.set_state(UpdateState.selecting_subject)
    
    await callback.message.edit_text(
        "📚 **Konu Güncelleme** 📚\n\n"
        "Hangi dersin konusunu güncellemek istiyorsun?",
        reply_markup=subject_menu(subjects)
    )
    await callback.answer()
