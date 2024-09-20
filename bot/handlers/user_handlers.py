import re
from aiogram import Router, F, types
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, StateFilter
from bot.lexicon.lexicon_ru import LEXICON_RU
from llm_agent.agent import Bibliography

router = Router()


class FSMGame(StatesGroup):
    search_message = State()


teachers = [
    {"id": 1, "name": "Иванов Иван Иванович"},
    {"id": 2, "name": "Петров Петр Петрович"},
    {"id": 3, "name": "Сидорова Анна Сергеевна"},
    # Добавь сюда больше преподавателей
]


# Функция для фильтрации преподавателей
def search_teachers(query: str):
    query = query.lower()
    return [teacher for teacher in teachers if query in teacher["name"].lower()]

# Команда /start
@router.message(CommandStart())
async def start(message: types.Message):
    bot_username='@yo_stepik_bot'
    # Кнопка для выбора преподавателя
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="Выбрать преподавателя",
        switch_inline_query_current_chat=bot_username,
        callback_data="select_teacher"
    )
    keyboard.adjust(1)

    await message.answer("Добро пожаловать! Нажмите на кнопку, чтобы выбрать преподавателя:", reply_markup=keyboard.as_markup())

# Обработка нажатия кнопки "Выбрать преподавателя"
@router.callback_query(F.data == "select_teacher")
async def select_teacher(callback: types.CallbackQuery):
    await callback.message.answer("Введите ФИО преподавателя:")

# Обработка инлайн-запросов для поиска преподавателей
@router.inline_query()
async def inline_query(query: types.InlineQuery):
    # Получаем текст, введенный пользователем
    search_text = query.query

    # Фильтруем список преподавателей по введенному тексту
    matched_teachers = search_teachers(search_text)

    # Формируем результаты для инлайн-ответа
    results = [
        InlineQueryResultArticle(
            id=str(teacher["id"]),
            title=teacher["name"],
            input_message_content=InputTextMessageContent(
                message_text=f"Вы выбрали преподавателя: {teacher['name']}"
            )
        )
        for teacher in matched_teachers
    ]

    # Отправляем инлайн-результаты
    await query.answer(results, cache_time=1, is_personal=True)