from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from services.user_service import UserService
from keyboards.inline import main_menu, cancel_button

router = Router()

class RegisterState(StatesGroup):
    waiting_for_name = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    # Kullanıcı kayıtlı mı kontrol et
    user = await UserService.get_user(user_id)
    
    if user:
        # Kayıtlı kullanıcı - direkt ana menü
        await message.answer(
            f"✨ Hoş geldiniz {user['name']}! ✨\n\n"
            f"🎯 YKS Koç Bot'a hoş geldiniz.\n"
            f"Günlük takiplerinizi yaparak hedeflerinize ulaşın!",
            reply_markup=main_menu()
        )
    else:
        # Yeni kullanıcı - isim al
        await state.set_state(RegisterState.waiting_for_name)
        await message.answer(
            "🎉 YKS Koç Bot'a hoş geldiniz! 🎉\n\n"
            "Öncelikle sizi tanımak istiyorum.\n"
            "📝 **Lütfen adınızı girin:**",
            reply_markup=cancel_button()
        )

@router.message(RegisterState.waiting_for_name)
async def get_name(message: Message, state: FSMContext):
    name = message.text.strip()
    
    if len(name) < 2 or len(name) > 50:
        await message.answer(
            "❌ Lütfen geçerli bir isim girin (2-50 karakter):",
            reply_markup=cancel_button()
        )
        return
    
    user_id = message.from_user.id
    await UserService.register_or_update(user_id, name)
    
    await state.clear()
    await message.answer(
        f"✅ Harika! {name}, kaydınız tamamlandı!\n\n"
        f"🎯 Şimdi ana menüden günlük takiplerinizi yapabilirsiniz.",
        reply_markup=main_menu()
    )

@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❌ İşlem iptal edildi.\n"
        "Ana menüye döndünüz.",
        reply_markup=main_menu()
    )
    await callback.answer()
