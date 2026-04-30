from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    """Ana menü butonları"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Profilim", callback_data="profile")],
        [InlineKeyboardButton(text="📝 Günlük Giriş", callback_data="daily")],
        [InlineKeyboardButton(text="📚 Konularımı Güncelle", callback_data="update_subjects")],
        [InlineKeyboardButton(text="📈 Analiz", callback_data="analysis")],
        [InlineKeyboardButton(text="⚙️ Ayarlar", callback_data="settings")],
    ])

def nav_buttons(back_callback: str = None, home_callback: str = "main_menu"):
    """Navigasyon butonları (Geri/Ana Menü/İptal)"""
    buttons = []
    
    if back_callback:
        buttons.append(InlineKeyboardButton(text="🔙 Geri", callback_data=back_callback))
    
    buttons.append(InlineKeyboardButton(text="🏠 Ana Menü", callback_data=home_callback))
    buttons.append(InlineKeyboardButton(text="❌ İptal", callback_data="cancel"))
    
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

def subject_menu(subjects: list):
    """Ders listesi menüsü"""
    buttons = []
    for subject in subjects:
        buttons.append([InlineKeyboardButton(
            text=f"📚 {subject['name'].title()}",
            callback_data=f"subject_{subject['name']}"
        )])
    
    # Navigasyon butonları
    buttons.append([InlineKeyboardButton(text="🏠 Ana Menü", callback_data="main_menu")])
    buttons.append([InlineKeyboardButton(text="❌ İptal", callback_data="cancel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def topic_menu(subject: str, topics: list):
    """Konu listesi menüsü"""
    buttons = []
    for topic in topics:
        buttons.append([InlineKeyboardButton(
            text=f"📖 {topic.title()}",
            callback_data=f"topic_{subject}_{topic}"
        )])
    
    buttons.append([InlineKeyboardButton(text="🔙 Geri", callback_data="back_to_subjects")])
    buttons.append([InlineKeyboardButton(text="🏠 Ana Menü", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def score_buttons(subject: str, topic: str):
    """Puanlama butonları (0-100)"""
    scores = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0]
    buttons = []
    row = []
    
    for score in scores:
        row.append(InlineKeyboardButton(
            text=str(score),
            callback_data=f"score_{subject}_{topic}_{score}"
        ))
        if len(row) == 5:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton(text="🔙 Geri", callback_data=f"back_to_topics_{subject}")])
    buttons.append([InlineKeyboardButton(text="🏠 Ana Menü", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def cancel_button():
    """Sadece iptal butonu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ İptal", callback_data="cancel")]
    ])
