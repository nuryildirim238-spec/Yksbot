from aiogram import Router, F
from aiogram.types import CallbackQuery

from services.analysis_service import AnalysisService
from services.stats_service import StatsService
from keyboards.inline import nav_buttons
from utils.formatters import progress_bar, format_hours, format_questions

router = Router()

@router.callback_query(F.data == "analysis")
async def show_analysis(callback: CallbackQuery):
    """Detaylı analiz raporu göster"""
    user_id = callback.from_user.id
    
    # Analiz verilerini al
    averages = await AnalysisService.get_subject_averages(user_id)
    overall_avg = await AnalysisService.get_overall_average(user_id)
    weak_topics = await AnalysisService.get_weak_topics(user_id)
    strong_topics = await AnalysisService.get_strong_topics(user_id)
    stats = await StatsService.get_total_stats(user_id)
    daily_avg = await StatsService.get_daily_average(user_id)
    
    # Analiz metnini oluştur
    analysis_text = "📈 **Detaylı Analiz Raporu** 📈\n\n"
    
    # Genel durum
    if overall_avg >= 70:
        status = "🔥 Mükemmel gidiyorsun! 🔥"
    elif overall_avg >= 40:
        status = "📌 İyi gidiyorsun, devam et! 📌"
    else:
        status = "⚠️ Başlangıç seviyesindesin, çalışmaya başla! ⚠️"
    
    analysis_text += f"**Genel Başarı:** {overall_avg}% {progress_bar(overall_avg)}\n"
    analysis_text += f"*{status}*\n\n"
    
    # Ders bazlı analiz
    analysis_text += "📚 **Ders Bazlı Analiz:**\n"
    if averages:
        for subject, avg in averages.items():
            subject_name = subject.title()
            analysis_text += f"• {subject_name}: {avg}% {progress_bar(avg, 8)}\n"
    else:
        analysis_text += "• Henüz konu güncellemesi yapılmadı\n"
    
    # Zayıf konular (detaylı)
    analysis_text += f"\n⚠️ **Geliştirilmesi Gereken Konular** (0-40):\n"
    if weak_topics:
        for w in weak_topics[:5]:
            analysis_text += f"• {w['subject'].title()} - {w['topic'].title()}: {w['score']}%\n"
        
        if len(weak_topics) > 5:
            analysis_text += f"  ...ve {len(weak_topics) - 5} konu daha\n"
        
        analysis_text += "\n💡 **Öneri:** Zayıf konulara haftada 3-4 saat ayırın.\n"
    else:
        analysis_text += "• Hiç zayıf konun yok! Harikasın! 🎉\n"
    
    # Güçlü konular
    analysis_text += f"\n🔥 **Güçlü Olduğun Konular** (70-100):\n"
    if strong_topics:
        for s in strong_topics[:5]:
            analysis_text += f"• {s['subject'].title()} - {s['topic'].title()}: {s['score']}%\n"
        
        analysis_text += "\n💡 **Öneri:** Güçlü konuları haftada 1-2 saat tekrarla.\n"
    else:
        analysis_text += "• Henüz güçlü konu bulunmuyor. Çalışmaya devam! 💪\n"
    
    # Çalışma alışkanlıkları
    analysis_text += f"\n⏱️ **Çalışma Alışkanlıkları:**\n"
    analysis_text += f"• Toplam Çalışma: {format_hours(stats.get('total_study_hours', 0))}\n"
    analysis_text += f"• Günlük Ortalama: {format_hours(daily_avg)}\n"
    analysis_text += f"• Toplam Soru: {format_questions(stats.get('total_questions', 0))}\n"
    analysis_text += f"• Aktif Gün: {stats.get('total_days', 0)} gün\n"
    
    # Motivasyon mesajı
    if daily_avg >= 4:
        analysis_text += "\n🌟 **Harika çalışma disiplinin var!** 🌟\n"
    elif daily_avg >= 2:
        analysis_text += "\n📌 **İyi gidiyorsun, hedefini yükseltebilirsin!** 📌\n"
    else:
        analysis_text += "\n💪 **Daha fazla çalışarak hedefine ulaşabilirsin!** 💪\n"
    
    analysis_text += f"\n🎯 Hedefine bir gün daha yaklaştın!"
    
    await callback.message.edit_text(
        analysis_text,
        reply_markup=nav_buttons(home_callback="main_menu"),
        parse_mode="Markdown"
    )
    await callback.answer()
