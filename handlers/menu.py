from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.inline import main_menu, nav_buttons

router = Router()

@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Ana menüye dön"""
    await state.clear()
    
    await callback.message.edit_text(
        "🎯 **Ana Menü** 🎯\n\n"
        "Lütfen yapmak istediğiniz işlemi seçin:",
        reply_markup=main_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "cancel")
async def cancel_and_menu(callback: CallbackQuery, state: FSMContext):
    """İptal et ve ana menüye dön"""
    await state.clear()
    
    await callback.message.edit_text(
        "❌ İşlem iptal edildi.\n\n"
        "🎯 **Ana Menü**'ye döndünüz:",
        reply_markup=main_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "settings")
async def settings_menu(callback: CallbackQuery):
    """Ayarlar menüsü"""
    await callback.message.edit_text(
        "⚙️ **Ayarlar** ⚙️\n\n"
        "Bu bölüm yakında aktif olacak.\n\n"
        "🏠 Ana menüden devam edebilirsiniz.",
        reply_markup=nav_buttons(home_callback="main_menu")
    )
    await callback.answer()

@router.message()
async def unknown_message(message: Message):
    """Bilinmeyen mesajlar için"""
    await message.answer(
        "❓ Anlamadım.\n"
        "Lütfen menüden bir seçenek kullanın:",
        reply_markup=main_menu()
    )
