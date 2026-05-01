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

# Tüm olası ders adları
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
        "📚 **Konu Güncelleme** 📚\n\n"
        "Hangi kategorideki derslerinizi güncellemek istiyorsunuz?\n\n"
        "📊 **Genel Durumunuz:**",
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
        f"📖 **{category.upper()} Dersleri** 📖\n\n"
        f"Hangi dersi güncellemek istiyorsunuz?",
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
    await callback.message.edit_text(
        f"📖 **{subject_name.replace('_', ' ').title()} Konuları** 📖\n\n"
        f"Mevcut durumunuz:\n"
        f"📊 **Ders Ortalaması:** {await AnalysisService.get_subject_average(user_id, subject_name)}%",
        reply_markup=topic_menu_with_scores(subject_name, topics, topic_scores)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("topic_"))
async def select_topic(callback: CallbackQuery, state: FSMContext):
    callback_data = callback.data
    print(f"📌 Gelen callback: {callback_data}")
    data = callback_data.replace("topic_", "")
    subject_name = None
    topic_name = None
    for subject in POSSIBLE_SUBJECTS:
        if data.startswith(subject + "_"):
            subject_name = subject
            topic_name = data[len(subject) + 1:]
            break
    if not subject_name:
        await callback.message.edit_text(
            "❌ Hatalı konu seçimi. Ders bulunamadı.",
            reply_markup=nav_buttons(home_callback="main_menu")
        )
        await callback.answer()
        return
    print(f"📌 Ders: {subject_name}, Konu: {topic_name}")
    user_id = callback.from_user.id
    user = await UserService.get_user(user_id)
    current_score = None
    if user and "subjects" in user and subject_name in user["subjects"]:
        current_score = user["subjects"][subject_name].get(topic_name)
    await state.update_data(selected_subject=subject_name, selected_topic=topic_name)
    await callback.message.edit_text(
        f"📊 **{subject_name.replace('_', ' ').title()} - {topic_name.title()}**\n\n"
        f"{f'📌 Mevcut puanınız: **{current_score}**' if current_score is not None else '📌 Henüz puan vermediniz'}\n\n"
        f"**Yeni seviyenizi seçin:**",
        reply_markup=score_range_menu(subject_name, topic_name, current_score)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("score_range_"))
async def save_score(callback: CallbackQuery, state: FSMContext):
    callback_data = callback.data
    print(f"📌 Gelen puan callback: {callback_data}")
    data = callback_data.replace("score_range_", "")
    subject_name = None
    remaining = data
    for subject in POSSIBLE_SUBJECTS:
        if data.startswith(subject + "_"):
            subject_name = subject
            remaining = data[len(subject) + 1:]
            break
    if not subject_name:
        await callback.message.edit_text(
            "❌ Hatalı puan seçimi. Ders bulunamadı.",
            reply_markup=nav_buttons(home_callback="main_menu")
        )
        await callback.answer()
        return
    last_underscore = remaining.rfind("_")
    if last_underscore == -1:
        await callback.message.edit_text(
            "❌ Hatalı puan seçimi formatı.",
            reply_markup=nav_buttons(home_callback="main_menu")
        )
        await callback.answer()
        return
    topic_name = remaining[:last_underscore]
    score_range = remaining[last_underscore + 1:]
    print(f"📌 Ders: {subject_name}, Konu: {topic_name}, Aralık: {score_range}")
    score_map = {"0_30": 15, "30_50": 40, "50_70": 60, "70_90": 80, "100": 100}
    new_score = score_map.get(score_range, 0)
    if new_score == 0 and score_range != "0_30":
        await callback.message.edit_text(
            "❌ Geçersiz puan aralığı.",
            reply_markup=nav_buttons(home_callback="main_menu")
        )
        await callback.answer()
        return
    user_id = callback.from_user.id
    user = await UserService.get_user(user_id)
    old_score = None
    if user and "subjects" in user and subject_name in user["subjects"]:
        old_score = user["subjects"][subject_name].get(topic_name)
    await UserService.update_subject_score(user_id, subject_name, topic_name, new_score)
    new_avg = await AnalysisService.get_subject_average(user_id, subject_name)
    weak_topics = await AnalysisService.get_weak_topics(user_id, 40)
    strong_topics = await AnalysisService.get_strong_topics(user_id, 70)
    await state.update_data(selected_subject=subject_name)
    await state.set_state(UpdateState.selecting_topic)
    if new_score >= 80:
        emoji, message_text = "🎉", "Harika! Bu konuda çok iyisin!"
    elif new_score >= 50:
        emoji, message_text = "👍", "Güzel! Biraz daha çalışmayla mükemmel olacak."
    else:
        emoji, message_text = "📚", "Tamam! Bu konuya biraz daha zaman ayıralım."
    change_text = ""
    if old_score is not None:
        change = new_score - old_score
        if change > 0:
            change_text = f" (+{change}) 📈"
        elif change < 0:
            change_text = f" ({change}) 📉"
    else:
        change_text = " (ilk puanın) 🆕"
    topics = await SubjectService.get_topics_by_subject(subject_name)
    user_current = await UserService.get_user(user_id)
    topic_scores = {}
    if user_current and "subjects" in user_current and subject_name in user_current["subjects"]:
        topic_scores = user_current["subjects"][subject_name]
    await callback.message.edit_text(
        f"{emoji} **Konu Güncellendi!** {emoji}\n\n"
        f"📖 {subject_name.replace('_', ' ').title()} - {topic_name.title()}\n"
        f"📊 Puan: **{old_score if old_score is not None else '?'}** → **{new_score}**{change_text}\n\n"
        f"{message_text}\n\n"
        f"📊 **{subject_name.replace('_', ' ').title()} Güncel Ortalama:** %{new_avg}\n"
        f"📉 **Zayıf konular:** {len(weak_topics)} tane\n"
        f"🔥 **Güçlü konular:** {len(strong_topics)} tane\n\n"
        f"**Devam etmek ister misiniz?**",
        reply_markup=topic_menu_with_scores(subject_name, topics, topic_scores, show_continue=True)
    )
    await callback.answer()

@router.callback_query(F.data == "continue_same_subject")
async def continue_same_subject(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    subject_name = data.get("selected_subject")
    topics = await SubjectService.get_topics_by_subject(subject_name)
    user_id = callback.from_user.id
    user = await UserService.get_user(user_id)
    topic_scores = {}
    if user and "subjects" in user and subject_name in user["subjects"]:
        topic_scores = user["subjects"][subject_name]
    await state.set_state(UpdateState.selecting_topic)
    await callback.message.edit_text(
        f"📖 **{subject_name.replace('_', ' ').title()} Konuları** 📖\n\n"
        f"Mevcut durumunuz:\n"
        f"📊 **Ders Ortalaması:** {await AnalysisService.get_subject_average(user_id, subject_name)}%\n\n"
        f"**Başka bir konu seçin:**",
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
        "📚 **Konu Güncelleme** 📚\n\n"
        "Hangi kategorideki derslerinizi güncellemek istiyorsunuz?\n\n"
        "📊 **Genel Durumunuz:**",
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
    await callback.message.edit_text(
        f"📖 **{subject_name.replace('_', ' ').title()} Konuları** 📖\n\n"
        f"Mevcut durumunuz:\n"
        f"📊 **Ders Ortalaması:** {await AnalysisService.get_subject_average(user_id, subject_name)}%",
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
        f"📖 **{category.upper()} Dersleri** 📖\n\n"
        f"Hangi dersi güncellemek istiyorsunuz?",
        reply_markup=subject_menu(filtered_subjects, subject_scores)
    )
    await callback.answer()
