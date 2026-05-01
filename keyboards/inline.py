from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.formatters import progress_bar

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Profilim", callback_data="profile")],
        [InlineKeyboardButton(text="📝 Gunluk Giris", callback_data="daily")],
        [InlineKeyboardButton(text="📚 Konularimi Guncelle", callback_data="update_subjects")],
        [InlineKeyboardButton(text="📈 Analiz", callback_data="analysis")],
        [InlineKeyboardButton(text="⚙️ Ayarlar", callback_data="settings")],
    ])

def nav_buttons(back_callback: str = None, home_callback: str = "main_menu"):
    buttons = []
    if back_callback:
        buttons.append(InlineKeyboardButton(text="🔙 Geri", callback_data=back_callback))
    buttons.append(InlineKeyboardButton(text="🏠 Ana Menu", callback_data=home_callback))
    buttons.append(InlineKeyboardButton(text="❌ Iptal", callback_data="cancel"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

def category_menu(tyt_avg: int = None, ayt_avg: int = None):
    buttons = []
    if tyt_avg is not None:
        tyt_text = f"📖 TYT Dersleri  {progress_bar(tyt_avg)} %{tyt_avg}"
    else:
        tyt_text = "📖 TYT Dersleri"
    if ayt_avg is not None:
        ayt_text = f"📚 AYT Dersleri  {progress_bar(ayt_avg)} %{ayt_avg}"
    else:
        ayt_text = "📚 AYT Dersleri"
    buttons.append([InlineKeyboardButton(text=tyt_text, callback_data="category_tyt")])
    buttons.append([InlineKeyboardButton(text=ayt_text, callback_data="category_ayt")])
    buttons.append([InlineKeyboardButton(text="🏠 Ana Menu", callback_data="main_menu")])
    buttons.append([InlineKeyboardButton(text="❌ Iptal", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def subject_menu(subjects: list, subject_scores: dict = None):
    buttons = []
    row = []
    for subject in subjects:
        name = subject["name"]
        display = subject.get("display_name", name.replace("_", " ").title())
        if "matematik" in name:
            short = "📐 Matematik"
        elif "geometri" in name:
            short = "📏 Geometri"
        elif "turkce" in name or "edebiyat" in name:
            short = "📖 " + (display.split()[-1] if " " in display else display)
        elif "fizik" in name:
            short = "⚡ Fizik"
        elif "kimya" in name:
            short = "🧪 Kimya"
        elif "biyoloji" in name:
            short = "🧬 Biyoloji"
        elif "tarih" in name:
            short = "📜 Tarih"
        elif "cografya" in name:
            short = "🌍 Cografya"
        elif "felsefe" in name:
            short = "💭 Felsefe"
        elif "din" in name:
            short = "🕌 Din"
        else:
            short = display
        score = subject_scores.get(name) if subject_scores else None
        text = f"{short} %{score}" if score is not None else short
        row.append(InlineKeyboardButton(text=text, callback_data=f"subject_{name}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 Kategorilere Don", callback_data="back_to_categories")])
    buttons.append([InlineKeyboardButton(text="🏠 Ana Menu", callback_data="main_menu")])
    buttons.append([InlineKeyboardButton(text="❌ Iptal", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def topic_menu_with_scores(subject: str, topics: list, topic_scores: dict, show_continue: bool = False):
    buttons = []
    row = []
    for topic in topics:
        score = topic_scores.get(topic)
        if score is not None:
            text = f"{topic} {progress_bar(score, 5)} %{score}"
        else:
            text = f"{topic} 📝"
        row.append(InlineKeyboardButton(text=text[:40], callback_data=f"topic_{subject}_{topic}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    if show_continue:
        buttons.append([InlineKeyboardButton(text="✅ Aynı Derse Devam Et", callback_data="continue_same_subject")])
    buttons.append([InlineKeyboardButton(text="🔙 Geri", callback_data="back_to_subjects")])
    buttons.append([InlineKeyboardButton(text="🏠 Ana Menu", callback_data="main_menu")])
    buttons.append([InlineKeyboardButton(text="❌ Iptal", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def score_range_menu(subject: str, topic: str, current_score: int = None):
    buttons = []
    ranges = [
        ("0_30", "15", "🔴 Baslangic / Hic bilmiyorum"),
        ("30_50", "40", "🟠 Biraz biliyorum, calismaliyim"),
        ("50_70", "60", "🟡 Orta seviyedeyim"),
        ("70_90", "80", "🟢 Iyi seviyedeyim"),
        ("100", "100", "✅ Cok iyi, konuyu bitirdim")
    ]
    for range_key, score_value, description in ranges:
        marker = " ✅" if current_score and int(score_value) == current_score else ""
        text = f"{range_key.replace('_', '-')}  {description}{marker}"[:40]
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"score_range_{subject}_{topic}_{range_key}")])
    buttons.append([InlineKeyboardButton(text="🔙 Geri", callback_data=f"back_to_topics_{subject}")])
    buttons.append([InlineKeyboardButton(text="🏠 Ana Menu", callback_data="main_menu")])
    buttons.append([InlineKeyboardButton(text="❌ Iptal", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def cancel_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Iptal", callback_data="cancel")]
    ])
