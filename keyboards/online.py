from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.formatters import progress_bar

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Profilim", callback_data="profile")],
        [InlineKeyboardButton(text="📝 Günlük Giriş", callback_data="daily")],  # ← bu callback daily.py'deki daily_menu'ye gidecek
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

def category_menu(tyt_avg: int = None, ayt_avg: int = None):
    """TYT/AYT kategorilerini gösteren menü (başarı yüzdeleriyle)"""
    buttons = []
    
    # TYT butonu
    if tyt_avg is not None:
        tyt_text = f"📖 TYT Dersleri  {progress_bar(tyt_avg)} %{tyt_avg}"
    else:
        tyt_text = "📖 TYT Dersleri"
    
    # AYT butonu
    if ayt_avg is not None:
        ayt_text = f"📚 AYT Dersleri  {progress_bar(ayt_avg)} %{ayt_avg}"
    else:
        ayt_text = "📚 AYT Dersleri"
    
    buttons.append([InlineKeyboardButton(text=tyt_text, callback_data="category_tyt")])
    buttons.append([InlineKeyboardButton(text=ayt_text, callback_data="category_ayt")])
    buttons.append([InlineKeyboardButton(text="🏠 Ana Menü", callback_data="main_menu")])
    buttons.append([InlineKeyboardButton(text="❌ İptal", callback_data="cancel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def subject_menu(subjects: list, subject_scores: dict = None):
    """Ders listesi menüsü (başarı yüzdeleriyle - 3 sütun)"""
    buttons = []
    row = []
    
    for subject in subjects:
        name = subject["name"]
        display = subject.get("display_name", name.replace("_", " ").title())
        
        # Kısa gösterim için
        if "matematik" in name:
            short = "📐 Matematik"
        elif "geometri" in name:
            short = "📏 Geometri"
        elif "turkce" in name or "edebiyat" in name:
            short = "📖 " + display.split()[-1] if " " in display else "📖 " + display
        elif "fizik" in name:
            short = "⚡ Fizik"
        elif "kimya" in name:
            short = "🧪 Kimya"
        elif "biyoloji" in name:
            short = "🧬 Biyoloji"
        elif "tarih" in name:
            short = "📜 Tarih"
        elif "cografya" in name:
            short = "🌍 Coğrafya"
        elif "felsefe" in name or "psikoloji" in name:
            short = "💭 Felsefe"
        elif "din" in name:
            short = "🕌 Din"
        else:
            short = display
        
        # Puan varsa göster
        score = subject_scores.get(name) if subject_scores else None
        if score is not None:
            text = f"{short} %{score}"
        else:
            text = short
        
        row.append(InlineKeyboardButton(text=text, callback_data=f"subject_{name}"))
        
        if len(row) == 3:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton(text="🔙 Geri", callback_data="back_to_categories")])
    buttons.append([InlineKeyboardButton(text="🏠 Ana Menü", callback_data="main_menu")])
    buttons.append([InlineKeyboardButton(text="❌ İptal", callback_data="cancel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def topic_menu_with_scores(subject: str, topics: list, topic_scores: dict, show_continue: bool = False):
    """Konu listesi menüsü (mevcut puanları göstererek)"""
    buttons = []
    row = []
    
    for topic in topics:
        score = topic_scores.get(topic)
        if score is not None:
            text = f"{topic.title()} {progress_bar(score, 5)} %{score}"
        else:
            text = f"{topic.title()} 📝"
        
        row.append(InlineKeyboardButton(text=text[:30], callback_data=f"topic_{subject}_{topic}"))
        
        if len(row) == 2:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    if show_continue:
        buttons.append([InlineKeyboardButton(text="✅ Aynı Derse Devam Et", callback_data="continue_same_subject")])
    
    buttons.append([InlineKeyboardButton(text="🔙 Geri", callback_data="back_to_subjects")])
    buttons.append([InlineKeyboardButton(text="🏠 Ana Menü", callback_data="main_menu")])
    buttons.append([InlineKeyboardButton(text="❌ İptal", callback_data="cancel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def score_range_menu(subject: str, topic: str, current_score: int = None):
    """5 aralıklı puanlama menüsü"""
    buttons = []
    
    # Puan aralıkları ve açıklamaları
    ranges = [
        ("0-30", "15", "🔴 Başlangıç / Hiç bilmiyorum"),
        ("30-50", "40", "🟠 Biraz biliyorum, çalışmalıyım"),
        ("50-70", "60", "🟡 Orta seviyedeyim"),
        ("70-90", "80", "🟢 İyi seviyedeyim"),
        ("100", "100", "✅ Çok iyi, konuyu bitirdim")
    ]
    
    for range_key, score_value, description in ranges:
        # Mevcut puanı işaretle
        marker = " ✅" if current_score and int(score_value) == current_score else ""
        text = f"{range_key}  {description}{marker}"[:40]
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"score_range_{subject}_{topic}_{range_key.replace('-', '_')}")])
    
    buttons.append([InlineKeyboardButton(text="🔙 Geri", callback_data=f"back_to_topics_{subject}")])
    buttons.append([InlineKeyboardButton(text="🏠 Ana Menü", callback_data="main_menu")])
    buttons.append([InlineKeyboardButton(text="❌ İptal", callback_data="cancel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def cancel_button():
    """Sadece iptal butonu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ İptal", callback_data="cancel")]
    ])

def back_to_categories_button():
    """Kategorilere dönüş butonu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Kategorilere Dön", callback_data="back_to_categories")],
        [InlineKeyboardButton(text="🏠 Ana Menü", callback_data="main_menu")]
    ])

def back_to_categories_button():
    """Kategorilere dönüş butonu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Kategorilere Dön", callback_data="back_to_categories")],
        [InlineKeyboardButton(text="🏠 Ana Menü", callback_data="main_menu")],
        [InlineKeyboardButton(text="❌ İptal", callback_data="cancel")]
    ])

def simple_back_button(back_callback: str):
    """Basit geri butonu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Geri", callback_data=back_callback)],
        [InlineKeyboardButton(text="🏠 Ana Menü", callback_data="main_menu")],
        [InlineKeyboardButton(text="❌ İptal", callback_data="cancel")]
    ])
