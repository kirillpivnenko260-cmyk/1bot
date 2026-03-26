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
from datetime import datetime, timedelta
import threading

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher()

# Словарь для хранения напоминаний {user_id: [{"text": text, "time": datetime, "chat_id": chat_id}]}
reminders = []

# Обычные кнопки
kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Создать напоминание")],
        [KeyboardButton(text="📋 Мои напоминания")],
        [KeyboardButton(text="❌ Отменить напоминание")],
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="🆘 Помощь")]
    ],
    resize_keyboard=True
)

# Клавиатура отмены
cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌ Отмена")]
    ],
    resize_keyboard=True
)

# Словарь для хранения состояний пользователей
user_states = {}
user_reminders = {}


def parse_time(time_str):
    """Парсит время в datetime"""
    time_str = time_str.lower().strip()
    now = datetime.now()

    # Если просто число (минуты)
    if time_str.isdigit():
        return now + timedelta(minutes=int(time_str))

    # Через X минут/часов
    if "через" in time_str:
        parts = time_str.split()
        if len(parts) >= 3:
            value = int(parts[1])
            if "минут" in parts[2]:
                return now + timedelta(minutes=value)
            elif "час" in parts[2]:
                return now + timedelta(hours=value)

    # Завтра в HH:MM
    if "завтра" in time_str:
        import re
        time_match = re.search(r'(\d{1,2}):(\d{2})', time_str)
        if time_match:
            hour, minute = int(time_match.group(1)), int(time_match.group(2))
            tomorrow = now + timedelta(days=1)
            return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)

    try:
        return datetime.strptime(time_str, '%d.%m.%Y %H:%M')
    except:
        pass

    return None


async def check_reminders():
    """Фоновая проверка напоминаний"""
    while True:
        try:
            now = datetime.now()
            to_remove = []

            for i, reminder in enumerate(reminders):
                if reminder["time"] <= now:
                    # Отправляем напоминание
                    try:
                        await bot.send_message(
                            reminder["chat_id"],
                            f"🔔 НАПОМИНАНИЕ! 🔔\n\n📝 {reminder['text']}\n\n⏰ Время: {reminder['time'].strftime('%d.%m.%Y %H:%M')}"
                        )
                    except:
                        pass
                    to_remove.append(i)

            # Удаляем отправленные напоминания
            for i in reversed(to_remove):
                reminders.pop(i)

            await asyncio.sleep(60)  # Проверяем каждую минуту
        except Exception as e:
            print(f"Ошибка в check_reminders: {e}")
            await asyncio.sleep(60)


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Привет! Я бот", reply_markup=kb)


# Кнопка Создать напоминание
@dp.message(lambda message: message.text == "📝 Создать напоминание")
async def create_reminder(message: types.Message):
    user_id = message.from_user.id
    user_states[user_id] = "waiting_for_text"
    await message.answer(
        " Введите текст напоминания:",
        reply_markup=cancel_kb
    )


# Кнопка Мои напоминания
@dp.message(lambda message: message.text == "📋 Мои напоминания")
async def my_reminders(message: types.Message):
    user_id = message.from_user.id
    user_reminders_list = [r for r in reminders if r["user_id"] == user_id]

    if not user_reminders_list:
        await message.answer(" У вас нет активных напоминаний")
        return

    text = " Ваши напоминания:\n\n"
    for i, r in enumerate(user_reminders_list, 1):
        text += f"{i}. {r['text']}\n    {r['time'].strftime('%d.%m.%Y %H:%M')}\n\n"

    await message.answer(text)


# Кнопка Отменить напоминание
@dp.message(lambda message: message.text == "❌ Отменить напоминание")
async def cancel_reminder(message: types.Message):
    user_id = message.from_user.id
    user_reminders_list = [r for r in reminders if r["user_id"] == user_id]

    if not user_reminders_list:
        await message.answer(" У вас нет активных напоминаний")
        return

    # Создаем инлайн кнопки для выбора
    buttons = []
    for r in user_reminders_list:
        buttons.append([InlineKeyboardButton(
            text=f"{r['text'][:20]} - {r['time'].strftime('%d.%m %H:%M')}",
            callback_data=f"cancel_{r['id']}"
        )])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(" Выберите напоминание для отмены:", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data.startswith("cancel_"))
async def cancel_reminder_callback(callback: types.CallbackQuery):
    reminder_id = int(callback.data.split("_")[1])

    for i, r in enumerate(reminders):
        if r["id"] == reminder_id:
            reminders.pop(i)
            await callback.message.edit_text("✅ Напоминание отменено!")
            break

    await callback.answer()


# Кнопка Статистика
@dp.message(lambda message: message.text == "📊 Статистика")
async def statistics(message: types.Message):
    user_id = message.from_user.id
    user_reminders_list = [r for r in reminders if r["user_id"] == user_id]
    await message.answer(f"📊 Статистика:\n\nАктивных напоминаний: {len(user_reminders_list)}")


# Кнопка Помощь
@dp.message(lambda message: message.text == " Помощь")
async def help_message(message: types.Message):
    await message.answer(
        '📋 Мои напоминания: посмотреть свои напоминания\n\n'
        '➕ Создать напоминание: создать новое напоминание\n\n'
        '❌ Отменить напоминание: отменить активное напоминание\n\n'
        '📊 Статистика: посмотреть статистику напоминаний'
    )


# Получаем текст напоминания
@dp.message(lambda message: user_states.get(message.from_user.id) == "waiting_for_text")
async def get_reminder_text(message: types.Message):
    user_id = message.from_user.id

    if message.text == " Отмена":
        del user_states[user_id]
        await message.answer(
            " Создание напоминания отменено",
            reply_markup=kb
        )
        return

    user_reminders[user_id] = {"text": message.text}
    user_states[user_id] = "waiting_for_time"

    await message.answer(
        " Введите время напоминания:\n\n"
        "Примеры:\n"
        "• 30 (минут)\n"
        "• через 2 часа\n"
        "• завтра в 15:30\n"
        "• 26.03.2026 14:00",
        reply_markup=cancel_kb
    )


# Получаем время напоминания
@dp.message(lambda message: user_states.get(message.from_user.id) == "waiting_for_time")
async def get_reminder_time(message: types.Message):
    user_id = message.from_user.id

    if message.text == " Отмена":
        del user_states[user_id]
        if user_id in user_reminders:
            del user_reminders[user_id]
        await message.answer(
            " Создание напоминания отменено",
            reply_markup=kb
        )
        return

    reminder_time = parse_time(message.text)

    if reminder_time is None:
        await message.answer(
            " Неверный формат времени!\n\n"
            "Примеры:\n"
            "• 30\n"
            "• через 2 часа\n"
            "• завтра в 15:30\n"
            "• 26.03.2026 14:00"
        )
        return

    if reminder_time < datetime.now():
        await message.answer(" Время не может быть в прошлом! Введите другое время:")
        return

    reminder_text = user_reminders[user_id]["text"]

    # Сохраняем напоминание
    reminders.append({
        "id": len(reminders),
        "user_id": user_id,
        "chat_id": message.chat.id,
        "text": reminder_text,
        "time": reminder_time
    })

    del user_states[user_id]
    del user_reminders[user_id]

    await message.answer(
        f"✅ Напоминание создано!\n\n"
        f"📝 {reminder_text}\n"
        f"⏰ {reminder_time.strftime('%d.%m.%Y %H:%M')}",
        reply_markup=kb
    )


# Обработчик остальных сообщений
@dp.message()
async def other_messages(message: types.Message):
    await message.answer(
        "Используйте кнопки меню:",
        reply_markup=kb
    )


async def main():
    # Запускаем фоновую проверку напоминаний
    asyncio.create_task(check_reminders())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
