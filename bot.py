# bot.py
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import config
from database import Database
from stages import get_stage_text, get_stage_location, STAGES
from utils import generate_diploma
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация
bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
db = Database()

# Класс для состояний (не обязателен, но удобен)
class QuestStates(StatesGroup):
    waiting_location = State()

# Клавиатуры
def get_main_keyboard(lang='ru'):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Я на месте" if lang=='ru' else "📍 I'm here")],
            [KeyboardButton(text="❓ Подсказка" if lang=='ru' else "❓ Hint")],
            [KeyboardButton(text="🏴‍☠️ Мой прогресс" if lang=='ru' else "🏴‍☠️ My progress")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_language_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
        ]
    )
    return keyboard
    def get_payment_keyboard(lang='ru'):
      keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить 20€" if lang=='ru' else "💳 Pay 20€", callback_data="pay")],
            [InlineKeyboardButton(text="❓ Что я получу?" if lang=='ru' else "❓ What I get?", callback_data="info")]
        ]
    )
    return keyboard

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""

    db.add_user(user_id, username, first_name)
    db.update_activity(user_id)

    await message.answer(
        "🏴‍☠️ *Добро пожаловать в охоту за сокровищами капитана Тейлора!*\n\n"
        "Выбери язык / Choose language:",
        parse_mode="Markdown",
        reply_markup=get_language_keyboard()
    )

# Выбор языка
@dp.callback_query(lambda c: c.data.startswith('lang_'))
async def process_language(callback: CallbackQuery):
    lang = callback.data.split('_')[1]
    user_id = callback.from_user.id

    db.set_language(user_id, lang)
    db.update_activity(user_id)

    # Проверяем, оплатил ли пользователь
    if db.check_paid(user_id):
        # Если уже оплатил, отправляем на текущий этап
        current_stage = db.get_stage(user_id)
        if current_stage == 0:
            current_stage = 1
            db.set_stage(user_id, 1)

        stage_text = get_stage_text(lang, current_stage, 'description')
        stage_task = get_stage_text(lang, current_stage, 'task')

        # Отправляем фото места, если есть
        photo_name = get_stage_text(lang, current_stage, 'photo')
        if photo_name and os.path.exists(f"photos/{photo_name}"):
            photo = FSInputFile(f"photos/{photo_name}")
            await bot.send_photo(
                chat_id=user_id,
                photo=photo,
                caption=f"*{get_stage_text(lang, current_stage, 'title')}*\n\n{stage_text}\n\n*Задание:* {stage_task}",
                parse_mode="Markdown",
                reply_markup=get_main_keyboard(lang)
            )
        else:
            await bot.send_message(
                chat_id=user_id,
                text=f"*{get_stage_text(lang, current_stage, 'title')}*\n\n{stage_text}\n\n*Задание:* {stage_task}",
                parse_mode="Markdown",
                reply_markup=get_main_keyboard(lang)
            )
    else:
        # Если не оплатил, предлагаем купить
        await bot.send_message(
            chat_id=user_id,
            text=("Чтобы начать охоту, нужно купить карту за 20€.\n\n"
                  "Ты получишь доступ к 5 этапам, в конце - именной диплом и подсказку, где найти сувенир."
                  if lang=='ru' else
                  "To start the hunt, you need to buy the map for 20€.\n\n"
                  "You'll get access to 5 stages, a personalized diploma, and a hint where to find a souvenir."),
            reply_markup=get_payment_keyboard(lang)
        )

    await callback.answer()

# Информация о квесте
@dp.callback_query(lambda c: c.data == "info")
async def quest_info(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = db.get_language(user_id)

    text_ru = (
        "🏴‍☠️ *Что тебя ждёт?*\n\n"
        "Ты отправишься по следам пирата Джона Тейлора, который в 1721 году спрятал сокровища на Мадейре.\n\n"
        "🔹 5 исторических мест в Фуншале и окрестностях\n"
        "🔹 Загадки и задания на каждом этапе\n"
        "🔹 Аудиорассказы от лица капитана\n"
        "🔹 Именной диплом в конце\n"
        "🔹 Подсказка, где получить сувенир\n\n"
        "*Время прохождения:* 3-4 часа\n"
        "*Сложность:* лёгкая (всё в пешей доступности + фуникулёр)"
    )
    text_en = (
        "🏴‍☠️ *What awaits you?*\n\n"
        "You will follow the trail of pirate John Taylor, who hid treasure on Madeira in 1721.\n\n"
        "🔹 5 historical places in Funchal and surroundings\n"
        "🔹 Riddles and tasks at each stage\n"
        "🔹 Audio stories from the captain\n"
        "🔹 Personalized diploma at the end\n"
        "🔹 Hint where to get a souvenir\n\n"
        "*Duration:* 3-4 hours\n"
        "*Difficulty:* easy (walking + cable car)"
    )

    await bot.send_message(
        chat_id=user_id,
        text=text_ru if lang=='ru' else text_en,
        parse_mode="Markdown",
        reply_markup=get_payment_keyboard(lang)
    )
    await callback.answer()

# Оплата (имитация для теста)
@dp.callback_query(lambda c: c.data == "pay")
async def process_payment(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = db.get_language(user_id)

    # Здесь должна быть интеграция со Stripe
    # Для теста просто помечаем пользователя как оплатившего

    db.set_paid(user_id, payment_id="test_payment")
    db.set_stage(user_id, 1)

    await bot.send_message(
        chat_id=user_id,
        text=("✅ Оплата прошла успешно! Карта сокровищ твоя.\n\n"
              "Отправляйся к первой точке: *Форт Сан-Лоренсу*.\n"
              "Когда будешь на месте, нажми кнопку «📍 Я на месте»."
              if lang=='ru' else
              "✅ Payment successful! The treasure map is yours.\n\n"
              "Go to the first point: *Fort São Lourenço*.\n"
              "When you're there, press the «📍 I'm here» button."),
        parse_mode="Markdown",
        reply_markup=get_main_keyboard(lang)
    )

    # Отправляем фото первой точки
    photo_name = get_stage_text(lang, 1, 'photo')
    if photo_name and os.path.exists(f"photos/{photo_name}"):
        photo = FSInputFile(f"photos/{photo_name}")
        await bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption=f"*{get_stage_text(lang, 1, 'title')}*\n\n{get_stage_text(lang, 1, 'description')}\n\n*Задание:* {get_stage_text(lang, 1, 'task')}",
            parse_mode="Markdown"
        )

    await callback.answer()

# Обработка кнопки "Я на месте"
@dp.message(lambda message: message.text in ["📍 Я на месте", "📍 I'm here"])
async def i_am_here(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = db.get_language(user_id)

    # Проверяем, оплатил ли
    if not db.check_paid(user_id):
        await message.answer(
            "Сначала нужно оплатить квест." if lang=='ru' else "You need to pay first.",
            reply_markup=get_payment_keyboard(lang)
        )
        return

    current_stage = db.get_stage(user_id)
    if current_stage == 0:
        current_stage = 1
        db.set_stage(user_id, 1)

    # Проверяем, не пройден ли уже этот этап
    if db.is_stage_completed(user_id, current_stage):
        await message.answer(
            "Ты уже прошёл этот этап. Идём дальше!" if lang=='ru' else "You've already completed this stage. Move on!"
        )
        # Отправляем следующий этап
        next_stage = current_stage + 1
        if next_stage <= 5:
            db.set_stage(user_id, next_stage)
            await send_stage(user_id, next_stage, lang)
        else:
            await finish_quest(user_id, lang)
        return

    # Здесь можно добавить проверку геолокации
    # Для теста просто принимаем

    # Отмечаем этап как пройденный
    db.complete_stage(user_id, current_stage)

    # Поздравляем и даём следующий этап
    await message.answer(
        "✅ Отлично! Ты нашёл фрагмент карты." if lang=='ru' else "✅ Great! You found a piece of the map."
    )

    next_stage = current_stage + 1
    if next_stage <= 5:
        db.set_stage(user_id, next_stage)
        await send_stage(user_id, next_stage, lang)
    else:
        await finish_quest(user_id, lang)
        # Отправка этапа пользователю
async def send_stage(user_id, stage_num, lang):
    title = get_stage_text(lang, stage_num, 'title')
    desc = get_stage_text(lang, stage_num, 'description')
    task = get_stage_text(lang, stage_num, 'task')

    text = f"*{title}*\n\n{desc}\n\n*Задание:* {task}"

    photo_name = get_stage_text(lang, stage_num, 'photo')
    if photo_name and os.path.exists(f"photos/{photo_name}"):
        photo = FSInputFile(f"photos/{photo_name}")
        await bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption=text,
            parse_mode="Markdown",
            reply_markup=get_main_keyboard(lang)
        )
    else:
        await bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=get_main_keyboard(lang)
        )

# Завершение квеста
async def finish_quest(user_id, lang):
    # Получаем имя пользователя
    user = await bot.get_chat(user_id)
    user_name = user.first_name or "Pirate"

    # Генерируем диплом
    diploma_path = await generate_diploma(user_name, lang)

    # Отправляем диплом
    diploma_file = FSInputFile(diploma_path)
    await bot.send_document(
        chat_id=user_id,
        document=diploma_file,
        caption=(
            "🏴‍☠️ *Ты настоящий охотник за сокровищами!*\n\n"
            "Твоё имя внесено в список легендарных пиратов Мадейры.\n\n"
            "Приходи в бар *«O Avô»* (Rua de Santa Maria, 103) и покажи этот диплом, чтобы получить бесплатный бокал мадеры!"
            if lang=='ru' else
            "🏴‍☠️ *You are a true treasure hunter!*\n\n"
            "Your name is added to the list of legendary pirates of Madeira.\n\n"
            "Come to *«O Avô»* bar (Rua de Santa Maria, 103) and show this diploma to get a free glass of Madeira wine!"
        ),
        parse_mode="Markdown"
    )

    # Очищаем временный файл
    os.remove(diploma_path)

    # Предлагаем поделиться
    share_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📱 Поделиться в Instagram" if lang=='ru' else "📱 Share on Instagram", url="https://instagram.com")],
            [InlineKeyboardButton(text="🔄 Пройти другой квест" if lang=='ru' else "🔄 Try another quest", callback_data="other_quest")]
        ]
    )

    await bot.send_message(
        chat_id=user_id,
        text=(
            "Расскажи друзьям о своём приключении! Отметь нас @MadeiraTreasureHunter."
            if lang=='ru' else
            "Tell your friends about your adventure! Tag us @MadeiraTreasureHunter."
        ),
        reply_markup=share_keyboard
    )

# Обработка кнопки "Подсказка"
@dp.message(lambda message: message.text in ["❓ Подсказка", "❓ Hint"])
async def send_hint(message: Message):
    user_id = message.from_user.id
    lang = db.get_language(user_id)

    if not db.check_paid(user_id):
        return

    current_stage = db.get_stage(user_id)
    if current_stage < 1 or current_stage > 5:
        return

    hint = get_stage_text(lang, current_stage, 'hint')
    if hint:
        await message.answer(
            f"💡 *Подсказка:* {hint}" if lang=='ru' else f"💡 *Hint:* {hint}",
            parse_mode="Markdown"
        )

# Обработка кнопки "Мой прогресс"
@dp.message(lambda message: message.text in ["🏴‍☠️ Мой прогресс", "🏴‍☠️ My progress"])
async def show_progress(message: Message):
    user_id = message.from_user.id
    lang = db.get_language(user_id)

    if not db.check_paid(user_id):
        await message.answer(
            "Сначала нужно оплатить квест." if lang=='ru' else "You need to pay first."
        )
        return

    current_stage = db.get_stage(user_id)
    completed = []
    for i in range(1, current_stage):
        if db.is_stage_completed(user_id, i):
            completed.append(i)

    progress_text = ""
    if lang == 'ru':
        progress_text = f"🏴‍☠️ *Твой прогресс:*\n\n"
        for i in range(1, 6):
            if i in completed:
                progress_text += f"✅ Этап {i}: пройден\n"
            elif i == current_stage:
                progress_text += f"⚡️ Этап {i}: текущий\n"
            else:
                progress_text += f"⏳ Этап {i}: ожидание\n"
    else:
        progress_text = f"🏴‍☠️ *Your progress:*\n\n"
        for i in range(1, 6):
            if i in completed:
                progress_text += f"✅ Stage {i}: completed\n"
            elif i == current_stage:
                progress_text += f"⚡️ Stage {i}: current\n"
            else:
                progress_text += f"⏳ Stage {i}: pending\n"

    await message.answer(progress_text, parse_mode="Markdown")

# Админ-команда /stats
@dp.message(Command("stats"))
async def show_stats(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        return

    stats = db.get_stats()
    await message.answer(
        f"📊 *Статистика*\n\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"💰 Оплативших: {stats['total_paid']}\n"
        f"🏁 Завершивших квест: {stats['completed']}",
        parse_mode="Markdown"
    )

# Запуск бота
async def main():
    # Создаём папку для фото, если её нет
    os.makedirs('photos', exist_ok=True)
    os.makedirs('temp', exist_ok=True)

    # Здесь можно загрузить фото точек в папку photos
    # Например: fort_sao_lorenzo.jpg, zona_velha_door.jpg и т.д.

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())