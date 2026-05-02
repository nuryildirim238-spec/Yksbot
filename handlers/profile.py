from aiogram import Router, F
from aiogram.types import CallbackQuery

from services.user_service import UserService
from services.analysis_service import AnalysisService
from services.stats_service import StatsService
from keyboards.inline import nav_buttons
from utils.formatters import format_hours, format_questions

router = Router()

def clean_text(text: str) -> str:
    """Markdown karakterlerini temizle"""
    chars_to_remove = ['*', '_', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for ch in chars_to_remove:
        text = text.replace(ch, '')
    return text

@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        
        user = await UserService.get_user(user_id)
        if not user:
            await callback.message.edit_text(
                clean_text("❌ Kullanici bulunamadi. Lutfen /start ile yeniden baslayin."),
                reply_markup=nav_buttons(home_callback="main_menu")
            )
            await callback.answer()
            return
        
        has_subjects = user.get("subjects") and any(user["subjects"].values())
        
        averages = await AnalysisService.get_subject_averages(user_id)
        overall_avg = await AnalysisService.get_overall_average(user_id)
        weak_topics = await AnalysisService.get_weak_topics(user_id)
        strong_topics = await AnalysisService.get_strong_topics(user_id)
        stats = await StatsService.get_total_stats(user_id)
        daily_avg = await StatsService.get_daily_average(user_id)
        last_7_days = await AnalysisService.get_last_7_days_logs(user_id)
        
        profile_text = f"👤 {user['name']}\n\n"
        
        if has_subjects:
            profile_text += f"📊 Genel Basari: %{overall_avg}\n\n"
            
            profile_text += "📚 Ders Basarilari:\n"
            if averages:
                for subject, avg in list(averages.items())[:5]:
                    display_name = subject.replace("_", " ").title()
                    profile_text += f"  • {display_name}: %{avg}\n"
            else:
                profile_text += "  • Henuz konu guncellemesi yapilmadi\n"
            
            profile_text += "\n📉 Zayif Konular (0-40):\n"
            weak = [t for t in weak_topics if t["score"] < 40]
            if weak:
                for w in weak[:3]:
                    subject_name = w['subject'].replace("_", " ").title()
                    profile_text += f"  • {subject_name} - {w['topic'].title()}: %{w['score']}\n"
            else:
                profile_text += "  • Zayif konu bulunmuyor\n"
            
            profile_text += "\n🔥 Guclu Konular (70-100):\n"
            strong = [t for t in strong_topics if t["score"] >= 70]
            if strong:
                for s in strong[:3]:
                    subject_name = s['subject'].replace("_", " ").title()
                    profile_text += f"  • {subject_name} - {s['topic'].title()}: %{s['score']}\n"
            else:
                profile_text += "  • Guclu konu bulunmuyor\n"
        else:
            profile_text += "📝 Henuz hic konu guncellemesi yapilmadi.\n"
            profile_text += "📚 Konularimi Guncelle butonunu kullanarak baslayabilirsin.\n"
        
        profile_text += f"\n⏱️ Calisma Istatistikleri:\n"
        profile_text += f"  • Toplam Calisma: {format_hours(stats.get('total_study_hours', 0))}\n"
        profile_text += f"  • Gunluk Ortalama: {format_hours(daily_avg)}\n"
        profile_text += f"  • Toplam Soru: {format_questions(stats.get('total_questions', 0))}\n"
        profile_text += f"  • Aktif Gun: {stats.get('total_days', 0)} gun\n"
        
        profile_text += f"\n📅 Son 7 Gun Ozeti:\n"
        if last_7_days:
            for log in last_7_days[:3]:
                profile_text += f"  • {log['date']}: {format_hours(log['study_hours'])} | {format_questions(log['questions'])}\n"
        else:
            profile_text += "  • Henuz gunluk giris yapilmadi\n"
        
        await callback.message.edit_text(
            clean_text(profile_text),
            reply_markup=nav_buttons(home_callback="main_menu")
        )
        await callback.answer()
        
    except Exception as e:
        print(f"Profil hatasi: {e}")
        await callback.message.edit_text(
            clean_text("❌ Profil yuklenirken bir hata olustu. Daha sonra tekrar deneyin."),
            reply_markup=nav_buttons(home_callback="main_menu")
        )
        await callback.answer()
