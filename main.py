from pyexpat.errors import messages

import config
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from base import SQL
from aiogram.filters import CommandStart

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher()

buttons2 = [
    [InlineKeyboardButton(text="Помощь", callback_data="help")]
]
kb2 = InlineKeyboardMarkup(inline_keyboard=buttons2)

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Привет! Я бот", reply_markup=kb2)

@dp.callback_query(lambda c: c.data == "help")
async def help_callback(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        '📋 Мои напоминания: вы можете посмотреть свои напоминания\n\n'
        '➕ Создать напоминание: вы можете создать любое напоминание с разными повторениями\n\n'
        '❌ Отменить напоминание: вы можете отменить любое активное напоминание созданное вами\n\n'
        '📊 Статистика: вы можете посмотреть активные и неактивные напоминания созданные вами'
    )

async def main():

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())