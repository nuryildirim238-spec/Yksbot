from aiogram import Router, F
from aiogram.types import CallbackQuery

from services.user_service import UserService
from services.analysis_service import AnalysisService
from services.stats_service import StatsService
from keyboards.inline import nav_buttons
from utils.formatters import progress_bar, format_hours, format_questions, get_score_level

router = Router()

@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    """Kullanıcı profilini göster"""
    user_id = callback.from_user.id
    
    # Kullanıcı bilgilerini al
    user = await UserService.get_user(user_id)
    if not user:
        await callback.message.edit_text(
            "❌ Kullanıcı bulunamadı. Lütfen /start ile yeniden başlayın.",
            reply_markup=nav_buttons(home_callback="main_menu")
        )
        await callback.answer()
        return
    
    # İstatistikleri al
    averages = await AnalysisService.get_subject_averages(user_id)
    overall_avg = await AnalysisService.get_overall_average(user_id)
    weak_topics = await AnalysisService.get_weak_topics(user_id)
    strong_topics = await AnalysisService.get_strong_topics(user_id)
    stats = await StatsService.get_total_stats(user_id)
    daily_avg = await StatsService.get_daily_average(user_id)
    last_7_days = await AnalysisService.get_last_7_days_logs(user_id)
    
    # Profil metnini oluştur
    profile_text = f"👤 **{user['name']}**\n\n"
    
    # Genel başarı
    profile_text += f"📊 **Genel Başarı:** {overall_avg}% {progress_bar(overall_avg)}\n\n"
    
    # Ders başarıları
    profile_text += "📚 **Ders Başarıları:**\n"
    if averages:
        for subject, avg in averages.items():
            subject_name = subject.title()
            profile_text += f"  • {subject_name}: {avg}% {progress_bar(avg, 5)}\n"
    else:
        profile_text += "  • Henüz konu güncellemesi yapılmadı\n"
    
    # Zayıf/Orta/Güçlü konular
    profile_text += "\n📉 **Zayıf Konular (0-40):**\n"
    weak = [t for t in weak_topics if t["score"] < 40]
    if weak:
        for w in weak[:3]:
            profile_text += f"  • {w['subject'].title()} - {w['topic'].title()}: {w['score']}%\n"
    else:
        profile_text += "  • Zayıf konu bulunmuyor 🎉\n"
    
    profile_text += "\n📊 **Orta Konular (40-70):**\n"
    medium = [t for t in weak_topics if 40 <= t["score"] < 70] + \
             [t for t in strong_topics if 40 <= t["score"] < 70]
    if medium:
        for m in medium[:3]:
            profile_text += f"  • {m['subject'].title()} - {m['topic'].title()}: {m['score']}%\n"
    else:
        profile_text += "  • Orta konu bulunmuyor\n"
    
    profile_text += "\n🔥 **Güçlü Konular (70-100):**\n"
    strong = [t for t in strong_topics if t["score"] >= 70]
    if strong:
        for s in strong[:3]:
            profile_text += f"  • {s['subject'].title()} - {s['topic'].title()}: {s['score']}%\n"
    else:
        profile_text += "  • Henüz güçlü konu bulunmuyor\n"
    
    # Çalışma istatistikleri
    profile_text += f"\n⏱️ **Çalışma İstatistikleri:**\n"
    profile_text += f"  • Toplam Çalışma: {format_hours(stats.get('total_study_hours', 0))}\n"
    profile_text += f"  • Günlük Ortalama: {format_hours(daily_avg)}\n"
    profile_text += f"  • Toplam Soru: {format_questions(stats.get('total_questions', 0))}\n"
    profile_text += f"  • Aktif Gün: {stats.get('total_days', 0)} gün\n"
    
    # Son 7 gün
    profile_text += f"\n📅 **Son 7 Gün Özeti:**\n"
    if last_7_days:
        for log in last_7_days[:5]:
            profile_text += f"  • {log['date']}: {format_hours(log['study_hours'])} | {format_questions(log['questions'])}\n"
    else:
        profile_text += "  • Henüz günlük giriş yapılmadı\n"
    
    await callback.message.edit_text(
        profile_text,
        reply_markup=nav_buttons(home_callback="main_menu"),
        parse_mode="Markdown"
    )
    await callback.answer()
