from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from services.subject_service import SubjectService
from services.user_service import UserService
from services.analysis_service import AnalysisService
from keyboards.inline import category_menu, subject_menu, topic_menu_with_scores, score_range_menu, nav_buttons, main_menu

router = Router()

class UpdateState(StatesGroup):
    selecting_category = State()
    selecting_subject = State()
    selecting_topic = State()

# Tum olası ders adlari (subject_service.py ile ayni olmali)
POSSIBLE_SUBJECTS = [
    "tyt_matematik", "tyt_geometri", "tyt_turkce", "tyt_fizik", 
    "tyt_kimya", "tyt_biyoloji", "tyt_tarih", "tyt_cografya", "tyt_felsefe",
    "ayt_matematik", "ayt_geometri", "ayt_edebiyat", "ayt_fizik", 
    "ayt_kimya", "ayt_biyoloji", "ayt_sosyal1_tarih", "ayt_sosyal1_cografya", 
    "ayt_sosyal2_felsefe", "ayt_sosyal2_din"
]

@router.callback_query(F.data == "update_subjects")
async def start_update(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    tyt_avg = await AnalysisService.get_category_average(user_id, "tyt")
    ayt_avg = await AnalysisService.get_category_average(user_id, "ayt")
    await state.set_state(UpdateState.selecting_category)
    await callback.message.edit_text(
        "📚 KONU GUNCELLEME 📚\n\n"
        "Hangi kategorideki derslerinizi guncellemek istiyorsunuz?\n\n"
        "📊 Genel Durumunuz:",
        reply_markup=category_menu(tyt_avg, ayt_avg)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("category_"))
async def select_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.replace("category_", "")
    subjects = await SubjectService.get_all_subjects()
    filtered_subjects = [s for s in subjects if s["name"].startswith(category)]
    user_id = callback.from_user.id
    subject_scores = {}
    for subject in filtered_subjects:
        avg = await AnalysisService.get_subject_average(user_id, subject["name"])
        subject_scores[subject["name"]] = avg
    await state.update_data(selected_category=category)
    await state.set_state(UpdateState.selecting_subject)
    await callback.message.edit_text(
        f"📖 {category.upper()} DERSLERI 📖\n\n"
        f"Hangi dersi guncellemek istiyorsunuz?",
        reply_markup=subject_menu(filtered_subjects, subject_scores)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("subject_"))
async def select_subject(callback: CallbackQuery, state: FSMContext):
    subject_name = callback.data.replace("subject_", "")
    topics = await SubjectService.get_topics_by_subject(subject_name)
    user_id = callback.from_user.id
    user = await UserService.get_user(user_id)
    topic_scores = {}
    if user and "subjects" in user and subject_name in user["subjects"]:
        topic_scores = user["subjects"][subject_name]
    await state.update_data(selected_subject=subject_name)
    await state.set_state(UpdateState.selecting_topic)
    avg_score = await AnalysisService.get_subject_average(user_id, subject_name)
    await callback.message.edit_text(
        f"📖 {subject_name.replace('_', ' ').title()} KONULARI 📖\n\n"
        f"Mevcut durumunuz:\n"
        f"📊 Ders Ortalamasi: %{avg_score}",
        reply_markup=topic_menu_with_scores(subject_name, topics, topic_scores)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("topic_"))
async def select_topic(callback: CallbackQuery, state: FSMContext):
    callback_data = callback.data
    data = callback_data.replace("topic_", "")
    
    subject_name = None
    topic_name = None
    
    for subject in POSSIBLE_SUBJECTS:
        if data.startswith(subject + "_"):
            subject_name = subject
            topic_name = data[len(subject) + 1:]
            break
    
    if not subject_name:
        await callback.answer("❌ Ders bulunamadi!", show_alert=True)
        return
    
    user_id = callback.from_user.id
    user = await UserService.get_user(user_id)
    current_score = None
    if user and "subjects" in user and subject_name in user["subjects"]:
        current_score = user["subjects"][subject_name].get(topic_name)
    
    await state.update_data(selected_subject=subject_name, selected_topic=topic_name)
    
    subject_display = subject_name.replace("_", " ").title()
    topic_display = topic_name.replace("_", " ").title()
    
    msg = f"📊 {subject_display} - {topic_display}\n\n"
    if current_score is not None:
        msg += f"📌 Mevcut puaniniz: {current_score}\n\n"
    else:
        msg += "📌 Henuz puan vermediniz\n\n"
    msg += "Yeni seviyenizi secin:"
    
    await callback.message.edit_text(
        msg,
        reply_markup=score_range_menu(subject_name, topic_name, current_score)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("score_range_"))
async def save_score(callback: CallbackQuery, state: FSMContext):
    callback_data = callback.data
    data = callback_data.replace("score_range_", "")
    
    # Dersi bul
    subject_name = None
    remaining = data
    
    for subject in POSSIBLE_SUBJECTS:
        if data.startswith(subject + "_"):
            subject_name = subject
            remaining = data[len(subject) + 1:]
            break
    
    if not subject_name:
        await callback.answer("❌ Ders bulunamadi!", show_alert=True)
        return
    
    # Konu ve puan araligini bul
    possible_ranges = ["0_30", "30_50", "50_70", "70_90", "100"]
    topic_name = None
    score_range = None
    
    for r in possible_ranges:
        if remaining.endswith("_" + r):
            topic_name = remaining[:-(len(r) + 1)]
            score_range = r
            break
    
    if not topic_name or not score_range:
        await callback.answer("❌ Hatali puan araligi!", show_alert=True)
        return
    
    # Puani hesapla
    score_map = {"0_30": 15, "30_50": 40, "50_70": 60, "70_90": 80, "100": 100}
    new_score = score_map.get(score_range, 0)
    
    user_id = callback.from_user.id
    user = await UserService.get_user(user_id)
    old_score = None
    if user and "subjects" in user and subject_name in user["subjects"]:
        old_score = user["subjects"][subject_name].get(topic_name)
    
    # Puani kaydet
    await UserService.update_subject_score(user_id, subject_name, topic_name, new_score)
    
    # Basarili mesaji
    if new_score >= 80:
        emoji = "🎉"
        basari_mesaji = "Harika! Bu konuda cok iyisin!"
    elif new_score >= 50:
        emoji = "👍"
        basari_mesaji = "Guzel! Biraz daha calismayla mukemmel olacak."
    else:
        emoji = "📚"
        basari_mesaji = "Tamam! Bu konuya biraz daha zaman ayiralim."
    
    # Puan degisimi
    if old_score is not None:
        degisim = new_score - old_score
        if degisim > 0:
            degisim_text = f" (+{degisim}) 📈"
        elif degisim < 0:
            degisim_text = f" ({degisim}) 📉"
        else:
            degisim_text = ""
    else:
        degisim_text = " (ilk puanin) 🆕"
    
    subject_display = subject_name.replace("_", " ").title()
    topic_display = topic_name.replace("_", " ").title()
    
    # Kisa bildirim
    await callback.answer(f"✅ {topic_display}: {old_score if old_score else '?'} → {new_score}{degisim_text}", show_alert=False)
    
    # Konu listesini tekrar al
    topics = await SubjectService.get_topics_by_subject(subject_name)
    user_current = await UserService.get_user(user_id)
    topic_scores = {}
    if user_current and "subjects" in user_current and subject_name in user_current["subjects"]:
        topic_scores = user_current["subjects"][subject_name]
    
    new_avg = await AnalysisService.get_subject_average(user_id, subject_name)
    
    await state.update_data(selected_subject=subject_name)
    await state.set_state(UpdateState.selecting_topic)
    
    await callback.message.edit_text(
        f"{emoji} {basari_mesaji} {emoji}\n\n"
        f"📖 {subject_display} - {topic_display}\n"
        f"📊 Puan: {old_score if old_score is not None else '?'} → {new_score}{degisim_text}\n\n"
        f"📊 Ders Ortalamasi: %{new_avg}\n\n"
        f"Baska bir konu secmek ister misiniz?",
        reply_markup=topic_menu_with_scores(subject_name, topics, topic_scores, show_continue=True)
    )

@router.callback_query(F.data == "continue_same_subject")
async def continue_same_subject(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    subject_name = data.get("selected_subject")
    if not subject_name:
        await callback.answer("❌ Hata!", show_alert=True)
        return
    
    topics = await SubjectService.get_topics_by_subject(subject_name)
    user_id = callback.from_user.id
    user = await UserService.get_user(user_id)
    topic_scores = {}
    if user and "subjects" in user and subject_name in user["subjects"]:
        topic_scores = user["subjects"][subject_name]
    
    await state.set_state(UpdateState.selecting_topic)
    avg_score = await AnalysisService.get_subject_average(user_id, subject_name)
    
    await callback.message.edit_text(
        f"📖 {subject_name.replace('_', ' ').title()} KONULARI 📖\n\n"
        f"Mevcut durumunuz:\n"
        f"📊 Ders Ortalamasi: %{avg_score}\n\n"
        f"Baska bir konu secin:",
        reply_markup=topic_menu_with_scores(subject_name, topics, topic_scores)
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    tyt_avg = await AnalysisService.get_category_average(user_id, "tyt")
    ayt_avg = await AnalysisService.get_category_average(user_id, "ayt")
    await state.set_state(UpdateState.selecting_category)
    await callback.message.edit_text(
        "📚 KONU GUNCELLEME 📚\n\n"
        "Hangi kategorideki derslerinizi guncellemek istiyorsunuz?\n\n"
        "📊 Genel Durumunuz:",
        reply_markup=category_menu(tyt_avg, ayt_avg)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("back_to_topics_"))
async def back_to_topics_route(callback: CallbackQuery, state: FSMContext):
    subject_name = callback.data.replace("back_to_topics_", "")
    topics = await SubjectService.get_topics_by_subject(subject_name)
    user_id = callback.from_user.id
    user = await UserService.get_user(user_id)
    topic_scores = {}
    if user and "subjects" in user and subject_name in user["subjects"]:
        topic_scores = user["subjects"][subject_name]
    await state.update_data(selected_subject=subject_name)
    await state.set_state(UpdateState.selecting_topic)
    avg_score = await AnalysisService.get_subject_average(user_id, subject_name)
    await callback.message.edit_text(
        f"📖 {subject_name.replace('_', ' ').title()} KONULARI 📖\n\n"
        f"Mevcut durumunuz:\n"
        f"📊 Ders Ortalamasi: %{avg_score}",
        reply_markup=topic_menu_with_scores(subject_name, topics, topic_scores)
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_subjects")
async def back_to_subjects(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category = data.get("selected_category", "tyt")
    subjects = await SubjectService.get_all_subjects()
    filtered_subjects = [s for s in subjects if s["name"].startswith(category)]
    user_id = callback.from_user.id
    subject_scores = {}
    for subject in filtered_subjects:
        avg = await AnalysisService.get_subject_average(user_id, subject["name"])
        subject_scores[subject["name"]] = avg
    await state.set_state(UpdateState.selecting_subject)
    await callback.message.edit_text(
        f"📖 {category.upper()} DERSLERI 📖\n\n"
        f"Hangi dersi guncellemek istiyorsunuz?",
        reply_markup=subject_menu(filtered_subjects, subject_scores)
    )
    await callback.answer()

@router.message()
async def unknown_message_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❓ Anlamadim. Lutfen menuden bir secenek kullanin.",
        reply_markup=main_menu()
    )

@router.callback_query()
async def unknown_callback_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❓ Anlamadim. Ana menuye yonlendiriliyorsunuz.",
        reply_markup=main_menu()
    )
    await callback.answer()
