import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from asgiref.sync import sync_to_async
import os
from dotenv import load_dotenv

# Настройка окружения Django для работы с базой данных
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
django.setup()

from courses.models import Course, Enrollment
from django.contrib.auth.models import User

API_TOKEN = os.getenv('API_TOKEN')
# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Обработчик команды /start и /help
@dp.message(CommandStart())
async def send_welcome(message: Message):
    await message.reply("Привет! Я ваш EdTech бот. Используйте /register для регистрации, /courses для поиска курсов.")

# Обработчик команды /register
@dp.message(Command(commands=["register"]))
async def register(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username

    # Проверяем, существует ли пользователь
    user, created = await sync_to_async(User.objects.get_or_create)(username=username)

    if created:
        await message.reply("Вы успешно зарегистрированы!")
    else:
        await message.reply("Вы уже зарегистрированы!")

# Обработчик команды /courses
@dp.message(Command(commands=["courses"]))
async def list_courses(message: Message):
    courses = await sync_to_async(list)(Course.objects.all())
    response = "Доступные курсы:\n"
    for course in courses:
        response += f"{course.title}\n"
    await message.reply(response)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
