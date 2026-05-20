import os
import asyncio
from aiohttp import web
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
Sizning_Tel = os.getenv("MY_PHONE")
Sizning_User = os.getenv("MY_USERNAME")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_surname = State()


SPECIAL_USERS = [
    {"name": "sabrina", "surname": "nuraliyeva"},
    {"name": "hosila", "surname": "bo'riyeva"},
    {"name": "hosila", "surname": "boriyeva"}
]


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()  # Start bosilganda eski qolib ketgan statelarni tozalaydi
    await message.answer(
        "Xush kelibsiz! Botdan foydalanish uchun roʻyxatdan oʻtishingiz kerak.\n\n"
        "Iltimos, ismingizni kiriting:"
    )
    await state.set_state(Registration.waiting_for_name)


@dp.message(Registration.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Rahmat. Endi familiyangizni kiriting:")
    await state.set_state(Registration.waiting_for_surname)


@dp.message(Registration.waiting_for_surname)
async def process_surname(message: types.Message, state: FSMContext):
    await state.update_data(surname=message.text.strip())

    # Ma'lumotlarni olish
    user_data = await state.get_data()
    await state.clear()

    input_name = str(user_data.get('name', '')).strip().lower()
    input_surname = str(user_data.get('surname', '')).strip().lower()

    # Tugmalarni yasash
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📞 Telefon orqali bog'lanish", url=f"tel:{Sizning_Tel}"))
    builder.row(types.InlineKeyboardButton(text="✈️ Telegram orqali bog'lanish", url=f"https://t.me/{Sizning_User}"))

    # Tekshirish
    is_special = False
    for user in SPECIAL_USERS:
        if user['name'] == input_name and user['surname'] == input_surname:
            is_special = True
            break

    if is_special:
        love_message = (
            "Men seni doimo sevganman bu bizning botimiz bu botni sen uchun ochganman \n"
            "Menga sendan boshqasi kerakmas iltimos menga qayt 🥺\n\n"
            "👉 Bot egasidan"
        )
        await message.answer(text=love_message, reply_markup=builder.as_markup())
    else:
        await message.answer(
            text="Xush kelibsiz! Siz muvaffaqiyatli ro'yxatdan o'tdingiz. Bot administratorlari tez orada siz bilan bog'lanishadi.",
            reply_markup=builder.as_markup()
        )


async def main():
    app = web.Application()
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    print("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())