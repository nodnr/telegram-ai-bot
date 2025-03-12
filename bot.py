import openai
import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()  # <-- Добавлено

# Настраиваем логирование
logging.basicConfig(
    filename="logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

def log_message(user_id, message_text, response_text):
    log_entry = f"User {user_id}: {message_text}\nBot: {response_text}\n{'-'*40}\n"
    with open("logs.txt", "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)

# Создаём клавиатуру с кнопками
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Задать вопрос"), KeyboardButton(text="Сбросить диалог")]
    ],
    resize_keyboard=True
)

# Храним историю сообщений
user_sessions = {}

@dp.message()
async def ai_response(message: Message):
    user_id = message.from_user.id

    # Проверяем кнопки
    if message.text == "Сбросить диалог":
        user_sessions[user_id] = []
        await message.answer("История диалога сброшена.", reply_markup=keyboard)
        return

    if message.text == "Задать вопрос":
        await message.answer("Напишите ваш вопрос.", reply_markup=keyboard)
        return

    # Проверяем, есть ли у пользователя история диалога
    if user_id not in user_sessions:
        user_sessions[user_id] = []

    # Добавляем сообщение пользователя в историю
    user_sessions[user_id].append({"role": "user", "content": message.text})

    try:
        # Отправляем запрос в OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=user_sessions[user_id]
        )
        answer = response["choices"][0]["message"]["content"]

        # Добавляем ответ в историю
        user_sessions[user_id].append({"role": "assistant", "content": answer})

        # Логируем запрос
        log_message(user_id, message.text, answer)

        await message.answer(answer, reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"Ошибка! Проверь API-ключ.\n\n{e}", reply_markup=keyboard)

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
