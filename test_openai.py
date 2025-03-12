import openai
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Создаём клавиатуру с кнопками
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("Задать вопрос"), KeyboardButton("Сбросить диалог"))

# Храним историю сообщений
user_sessions = {}

@dp.message()
async def ai_response(message: Message):
    user_id = message.from_user.id

    # Если нажата кнопка "Сбросить диалог"
    if message.text == "Сбросить диалог":
        user_sessions[user_id] = []
        await message.answer("История диалога сброшена.", reply_markup=keyboard)
        return

    # Если нажата кнопка "Задать вопрос"
    if message.text == "Задать вопрос":
        await message.answer("Напишите ваш вопрос.", reply_markup=keyboard)
        return

    # Проверяем, есть ли у пользователя сессия
    if user_id not in user_sessions:
        user_sessions[user_id] = []

    # Добавляем сообщение пользователя в историю
    user_sessions[user_id].append({"role": "user", "content": message.text})

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=user_sessions[user_id]
        )
        answer = response.choices[0].message.content

        # Добавляем ответ AI в историю
        user_sessions[user_id].append({"role": "assistant", "content": answer})

        await message.answer(answer, reply_markup=keyboard)
    except Exception as e:
        await message.answer("Ошибка! Проверь API-ключ.", reply_markup=keyboard)

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


