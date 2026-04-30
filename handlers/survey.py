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
    
    # Konu güncellemesi var mı?
    has_subjects = len(weak_topics) > 0 or len(strong_topics) > 0
    
    # Analiz metnini oluştur
    analysis_text = "📈 **Detaylı Analiz Raporu** 📈\n\n"
    
    if not has_subjects:
        analysis_text += "⚠️ **Henüz konu güncellemesi yapılmadı!** ⚠️\n\n"
        analysis_text += "Daha doğru analiz için lütfen önce **Konularımı Güncelle** bölümünden "
        analysis_text += "derslerinizi ve konularınızı puanlayın.\n\n"
        analysis_text += "📚 **Konularımı Güncelle** butonuna tıklayarak başlayabilirsiniz."
        
        await callback.message.edit_text(
            analysis_text,
            reply_markup=nav_buttons(home_callback="main_menu"),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
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
        # En yüksek ve en düşük dersi bul
        sorted_by_score = sorted(averages.items(), key=lambda x: x[1])
        lowest_subject = sorted_by_score[0] if sorted_by_score else None
        highest_subject = sorted_by_score[-1] if sorted_by_score else None
        
        for subject, avg in list(averages.items())[:5]:  # İlk 5 dersi göster
            display_name = subject.replace("_", " ").title()
            analysis_text += f"• {display_name}: {avg}% {progress_bar(avg, 8)}\n"
        
        if len(averages) > 5:
            analysis_text += f"  ...ve {len(averages) - 5} ders daha\n"
        
        analysis_text += "\n"
        
        # En zayıf ve en güçlü ders önerisi
        if lowest_subject:
            lowest_name = lowest_subject[0].replace("_", " ").title()
            analysis_text += f"💡 **Öneri:** En çok {lowest_name} dersine çalışmalısın. (%{lowest_subject[1]})\n"
        if highest_subject:
            highest_name = highest_subject[0].replace("_", " ").title()
            analysis_text += f"🎯 **Güçlü yönün:** {highest_name} dersinde iyisin. (%{highest_subject[1]})\n"
        
        analysis_text += "\n"
    
    # Zayıf konular (detaylı + öneri)
    analysis_text += f"⚠️ **Geliştirilmesi Gereken Konular** (0-40):\n"
    if weak_topics:
        for w in weak_topics[:5]:
            subject_name = w['subject'].replace("_", " ").title()
            analysis_text += f"• {subject_name} - {w['topic'].title()}: {w['score']}%\n"
        
        if len(weak_topics) > 5:
            analysis_text += f"  ...ve {len(weak_topics) - 5} konu daha\n"
        
        # Öneri - en düşük 3 konuyu söyle
        lowest_3 = weak_topics[:3]
        if lowest_3:
            analysis_text += f"\n💪 **Çalışma Önerisi:** En düşük puanlı konularına odaklan:\n"
            for w in lowest_3:
                subject_name = w['subject'].replace("_", " ").title()
                analysis_text += f"  • {subject_name} - {w['topic'].title()} (%{w['score']})\n"
            analysis_text += f"  Bu konulara **haftada 3-4 saat** ayırmanı öneririm.\n"
    else:
        analysis_text += "• Hiç zayıf konun yok! Harikasın! 🎉\n"
    
    # Güçlü konular
    analysis_text += f"\n🔥 **Güçlü Olduğun Konular** (70-100):\n"
    if strong_topics:
        for s in strong_topics[:5]:
            subject_name = s['subject'].replace("_", " ").title()
            analysis_text += f"• {subject_name} - {s['topic'].title()}: {s['score']}%\n"
        
        if len(strong_topics) > 5:
            analysis_text += f"  ...ve {len(strong_topics) - 5} konu daha\n"
        
        analysis_text += "\n💡 **Öneri:** Güçlü konularını haftada **1-2 saat tekrarla**.\n"
    else:
        analysis_text += "• Henüz güçlü konu bulunmuyor. Çalışmaya devam! 💪\n"
    
    # Çalışma alışkanlıkları
    analysis_text += f"\n⏱️ **Çalışma Alışkanlıkları:**\n"
    analysis_text += f"• Toplam Çalışma: {format_hours(stats.get('total_study_hours', 0))}\n"
    analysis_text += f"• Günlük Ortalama: {format_hours(daily_avg)}\n"
    analysis_text += f"• Toplam Soru: {format_questions(stats.get('total_questions', 0))}\n"
    analysis_text += f"• Aktif Gün: {stats.get('total_days', 0)} gün\n"
    
    # Çalışma önerisi
    if daily_avg >= 4:
        analysis_text += "\n🌟 **Harika çalışma disiplinin var!** Bu tempoda devam et.\n"
    elif daily_avg >= 2:
        analysis_text += "\n📌 **İyi gidiyorsun!** Hedefini günde 4 saate çıkarabilirsin.\n"
    else:
        analysis_text += "\n💪 **Çalışma süreni artırmalısın!** Günde 2-3 saat ile başlayabilirsin.\n"
    
    # Motivasyon kapanış
    if overall_avg >= 70:
        analysis_text += f"\n🎯 Hedefine çok yaklaştın! Son virajda hız kesme!"
    elif overall_avg >= 40:
        analysis_text += f"\n🎯 Yolun yarısını geçtin! Hedefine doğru ilerliyorsun."
    else:
        analysis_text += f"\n🎯 Başlangıçtayız! Düzenli çalışmayla hedefine ulaşabilirsin."
    
    await callback.message.edit_text(
        analysis_text,
        reply_markup=nav_buttons(home_callback="main_menu"),
        parse_mode="Markdown"
    )
    await callback.answer()
