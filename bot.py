import logging
import asyncio
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from asgiref.sync import sync_to_async
import os
from dotenv import load_dotenv
import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

# Настройка окружения Django для работы с базой данных
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
import django
django.setup()

from courses.models import Course, Enrollment, UserProfile
from django.contrib.auth.models import User

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# Определение состояний для FSM
class Form(StatesGroup):
    name = State()
    age = State()
    city = State()
    waiting_for_answer = State()

# Обработчик команды /start и /help
@router.message(CommandStart())
async def send_welcome(message: Message):
    welcome_text = (
        "<b>🎉 Добро пожаловать в наш бот! 🎉</b>\n"
        "Используйте <a href='/register'>/register</a> для регистрации, <a href='/courses'>/courses</a> для поиска курсов.\n\n"
        "<b>Доступные команды:</b>\n"
        "<b>/start</b> - Начать работу с ботом\n"
        "<b>/help</b> - Получить помощь\n"
        "<b>/echo</b> - Эхо команда\n"
        "<b>/photo</b> - Отправить фото\n"
        "<b>/inline</b> - Показать inline кнопки\n"
        "<b>/setname</b> - Установить имя и возраст\n"
        "<b>/users</b> - Показать пользователей\n"
        "<b>/weather</b> - Получить погоду\n"
        "<b>/ask</b> - Спросить, как дела"
    )
    await message.reply(welcome_text, parse_mode=ParseMode.HTML)

@router.message(Command(commands=["help"]))
async def send_help(message: Message):
    help_text = (
        "<b>💡 Доступные команды:</b>\n"
        "<b>/start</b> - Начать работу с ботом\n"
        "<b>/help</b> - Получить помощь\n"
        "<b>/echo</b> - Эхо команда\n"
        "<b>/photo</b> - Отправить фото\n"
        "<b>/inline</b> - Показать inline кнопки\n"
        "<b>/setname</b> - Установить имя и возраст\n"
        "<b>/users</b> - Показать пользователей\n"
        "<b>/weather</b> - Получить погоду\n"
        "<b>/ask</b> - Спросить, как дела"
    )
    await message.reply(help_text, parse_mode=ParseMode.HTML)

# Обработчик команды /register
@router.message(Command(commands=["register"]))
async def register(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username

    # Проверяем, существует ли пользователь
    user, created = await sync_to_async(User.objects.get_or_create)(username=username)

    if created:
        # Создаем профиль пользователя с telegram_id
        user_profile = await sync_to_async(UserProfile.objects.create)(user=user, telegram_id=user_id)
        await message.reply("Вы <b>успешно зарегистрированы</b>! 🎉", parse_mode=ParseMode.HTML)
    else:
        # Проверяем существование профиля пользователя и обновляем telegram_id
        try:
            user_profile = await sync_to_async(UserProfile.objects.get)(user=user)
            if user_profile.telegram_id != user_id:
                user_profile.telegram_id = user_id
                await sync_to_async(user_profile.save)()
        except UserProfile.DoesNotExist:
            user_profile = await sync_to_async(UserProfile.objects.create)(user=user, telegram_id=user_id)
        await message.reply(
            "Вы <b>уже зарегистрированы</b>! 🎉 Вы можете использовать команды:\n"
            "<a href='/courses'>/courses</a> - Для просмотра курсов\n"
            "<a href='/setname'>/setname</a> - Для обновления имени и возраста\n"
            "<a href='/weather'>/weather</a> - Для получения информации о погоде",
            parse_mode=ParseMode.HTML
        )

# Обработчик команды /courses
@router.message(Command(commands=["courses"]))
async def list_courses(message: Message):
    courses = await sync_to_async(list)(Course.objects.all())
    response = "<b>📚 Доступные курсы:</b>\n"
    for course in courses:
        response += f"• {course.title}\n"
    await message.reply(response, parse_mode=ParseMode.HTML)

# Обработчик команды /echo
@router.message(Command(commands=["echo"]))
async def echo(message: Message):
    text_to_echo = message.text[len("/echo "):].strip()
    if text_to_echo:
        await message.reply(text_to_echo)
    else:
        await message.reply("Пожалуйста, введите текст после команды /echo.")

# Обработчик команды /inline
@router.message(Command(commands=["inline"]))
async def send_inline_buttons(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбор 1", callback_data="choice_1")],
        [InlineKeyboardButton(text="Выбор 2", callback_data="choice_2")]
    ])
    await message.reply("Сделайте выбор:", reply_markup=keyboard, parse_mode=ParseMode.HTML)

# Обработчик коллбеков
@router.callback_query(F.data.in_({"choice_1", "choice_2"}))
async def process_callback(callback_query: types.CallbackQuery):
    if callback_query.data == "choice_1":
        await bot.send_message(callback_query.from_user.id, "Вы выбрали <b>Выбор 1</b>", parse_mode=ParseMode.HTML)
    elif callback_query.data == "choice_2":
        await bot.send_message(callback_query.from_user.id, "Вы выбрали <b>Выбор 2</b>", parse_mode=ParseMode.HTML)
    await callback_query.answer()

# FSM: Обработчик команды /setname
@router.message(Command(commands=["setname"]))
async def set_name(message: Message, state: FSMContext):
    try:
        user_profile = await sync_to_async(UserProfile.objects.get)(user__username=message.from_user.username)
    except UserProfile.DoesNotExist:
        await message.reply("Вы не зарегистрированы. Пожалуйста, используйте команду /register для регистрации.",
                            parse_mode=ParseMode.HTML)
        return

    await message.reply("Как вас зовут?", parse_mode=ParseMode.HTML)
    await state.set_state(Form.name)

@router.message(Form.name)
async def process_name(message: Message, state: FSMContext):
    if not message.text.isalpha():
        await message.reply("Имя должно содержать только буквы. Попробуйте еще раз.", parse_mode=ParseMode.HTML)
        return
    await state.update_data(name=message.text)
    await message.reply("Сколько вам лет?", parse_mode=ParseMode.HTML)
    await state.set_state(Form.age)

@router.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.reply("Возраст должен быть числом. Попробуйте еще раз.", parse_mode=ParseMode.HTML)
        return
    await state.update_data(age=int(message.text))
    user_data = await state.get_data()
    user, created = await sync_to_async(User.objects.get_or_create)(username=message.from_user.username)
    user_profile, _ = await sync_to_async(UserProfile.objects.get_or_create)(user=user)
    user.first_name = user_data['name']
    user_profile.age = user_data['age']
    await sync_to_async(user.save)()
    await sync_to_async(user_profile.save)()
    await message.reply(f"Вас зовут <b>{user_data['name']}</b> и вам <b>{user_data['age']}</b> лет.",
                        parse_mode=ParseMode.HTML)
    await state.clear()

# Обработчик загрузки изображений
@router.message(F.photo)
async def handle_photo(message: Message):
    photo = message.photo[-1]
    width, height = photo.width, photo.height
    await message.reply(f"Размер изображения: <b>{width}x{height}</b>", parse_mode=ParseMode.HTML)

# Обработчик команды /users для PostgreSQL
@router.message(Command(commands=["users"]))
async def list_users(message: Message):
    users = await sync_to_async(list)(User.objects.all())
    response = "<b>👥 Зарегистрированные пользователи:</b>\n"
    for user in users:
        try:
            user_profile = await sync_to_async(UserProfile.objects.get)(user=user)
            response += f"Username: <b>{user.username}</b>\nName: <b>{user.first_name}</b>\nAge: <b>{user_profile.age}</b>\n"
        except UserProfile.DoesNotExist:
            response += f"Username: <b>{user.username}</b>, Name: <b>{user.first_name}</b>, Age: <b>Не указан</b>\n"
    await message.reply(response, parse_mode=ParseMode.HTML)

# Обработчик команды /weather
@router.message(Command(commands=["weather"]))
async def weather(message: Message, state: FSMContext):
    await message.reply("Введите название города:", parse_mode=ParseMode.HTML)
    await state.set_state(Form.city)

@router.message(Form.city)
async def get_weather(message: Message, state: FSMContext):
    city = message.text
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric") as resp:
            data = await resp.json()
            if resp.status == 200:
                weather_description = data['weather'][0]['description']
                temperature = data['main']['temp']
                await message.reply(
                    f"Погода в <b>{city}</b>: {weather_description}, температура: <b>{temperature}°C</b>",
                    parse_mode=ParseMode.HTML)
            else:
                await message.reply("Город не найден, попробуйте еще раз.", parse_mode=ParseMode.HTML)
    await state.clear()

# Обработка исключений
@dp.errors()
async def handle_errors(update, error):
    if isinstance(error, Exception):
        if update.message:
            await update.message.reply("Произошла ошибка, попробуйте позже", parse_mode=ParseMode.HTML)
        return True
    return False

# Уведомления каждый день в 12:00 по московскому времени
async def send_notifications():
    users = await sync_to_async(list)(UserProfile.objects.all())
    for user_profile in users:
        if user_profile.telegram_id:
            try:
                await bot.send_message(user_profile.telegram_id, "Не забудьте проверить уведомления, Дарья в 12:00! 🔔",
                                       parse_mode=ParseMode.HTML)
            except Exception as e:
                logging.error(f"Error sending notification to {user_profile.user.username}: {e}")

async def scheduler_start():
    scheduler = AsyncIOScheduler()
    moscow_tz = pytz.timezone('Europe/Moscow')
    scheduler.add_job(send_notifications, CronTrigger(hour=12, minute=0, timezone=moscow_tz))
    scheduler.start()

# Новый функционал: Напоминание о необходимости ответа через 15 минут
@router.message(Command(commands=["ask"]))
async def ask_user(message: Message, state: FSMContext):
    user_profile = await sync_to_async(UserProfile.objects.get)(user__username=message.from_user.username)
    if not user_profile:
        await message.reply("Вы не зарегистрированы. Пожалуйста, используйте команду /register для регистрации.", parse_mode=ParseMode.HTML)
        return

    user_first_name = await sync_to_async(lambda: user_profile.user.first_name)()
    await message.reply(f"Привет, {user_first_name}! Как ты сегодня?", parse_mode=ParseMode.HTML)
    await state.set_state(Form.waiting_for_answer)
    await state.update_data(answer_received=False, timer_active=True)

    # Запускаем таймер на 15 минут
    asyncio.create_task(remind_to_answer(message.chat.id, state))

async def remind_to_answer(chat_id: int, state: FSMContext):
    await asyncio.sleep(900)
    user_data = await state.get_data()
    if user_data.get("timer_active") and not user_data.get("answer_received"):
        await bot.send_message(chat_id, "Вы забыли ответить.")
        await state.update_data(timer_active=False)

@router.message(Form.waiting_for_answer)
async def process_user_answer(message: Message, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get("timer_active"):
        await state.update_data(answer_received=True, timer_active=False)
        await message.reply("Спасибо за ответ!", parse_mode=ParseMode.HTML)
        await state.clear()

async def main():
    dp.include_router(router)
    await scheduler_start()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
