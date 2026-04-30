def progress_bar(percent: int, length: int = 10) -> str:
    """Progress bar oluşturur. Örn: ▰▰▰▰▱▱▱▱▱▱ %40"""
    filled = int(length * percent / 100)
    empty = length - filled
    return "▰" * filled + "▱" * empty

def format_percent(value: int) -> str:
    """Yüzde formatlar"""
    return f"%{value}"

def format_hours(hours: float) -> str:
    """Saat formatlar"""
    return f"{hours:.1f} saat"

def format_questions(questions: int) -> str:
    """Soru formatlar"""
    return f"{questions:,} soru"

def get_score_level(score: int) -> tuple:
    """Puana göre seviye ve emoji döndürür"""
    if score >= 70:
        return ("🔥 Güçlü", "🔥")
    elif score >= 40:
        return ("📌 Orta", "📌")
    else:
        return ("⚠️ Zayıf", "⚠️")
