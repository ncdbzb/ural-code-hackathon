import os
from aiogram import Router, F, types
from aiogram.types import Message, ContentType, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, StateFilter
from bot.lexicon.lexicon_ru import LEXICON_RU
from bot.utils.parse_docx import get_parsing_result, check_structure
from bot.utils.fill_output import get_output_docx
from bot.llm.llm import analyze_introduction, analyze_conclusion, analyze_relationship, questions_introduction, questions_conclusion, que_int_con


router = Router()


class FSMGame(StatesGroup):
    search_message = State()

# Команда /start
@router.message(CommandStart())
async def start(message: types.Message):
    await message.answer(LEXICON_RU['/start'])


@router.message(F.content_type == ContentType.DOCUMENT)
async def handle_file(message: Message):
    document = message.document

    # Проверяем расширение файла
    if document.mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        # Получаем уникальный ID пользователя
        user_id = message.from_user.id

        # Создаем директорию с уникальным ID пользователя, если её нет
        user_dir = f"bot/data/{user_id}"
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        # Задаем путь для сохранения файла
        input_path = os.path.join(user_dir, document.file_name)

        # Получаем информацию о файле и скачиваем его
        file_info = await message.bot.get_file(document.file_id)
        await message.bot.download_file(file_info.file_path, destination=input_path)

        result_dict = get_parsing_result(input_path)
        # await message.answer(f"result: {result_dict.keys()}")
        introduction = result_dict['введение']
        concl = result_dict['заключение']
        lit_list = result_dict['список использованных источников'].split('\n')

        structure_dict = check_structure(input_path)
        # await message.answer(f'result: {structure_dict}')
        comment_list = list()
        # Получение ответов для введения
        intro_answers = await analyze_introduction(introduction)
        # await message.answer(F"Ответы для Введения:\n{intro_answers}")
        intro_dict = {}
        for idx, que in enumerate(questions_introduction):
            intro_dict[que[:-6]] = '+' if intro_answers[idx][0].lower() in ('да', 'да.') else '-'

        for answer, help_inf in intro_answers:
            if answer.lower() in ('да', 'да.'):
                comment_list.append(('введение', help_inf))

        # Получение ответов для заключения
        concl_answers = await analyze_conclusion(concl)
        # await message.answer(f"Ответы для Заключения:\n{concl_answers}")
        concl_dict = {}
        for idx, que in enumerate(questions_conclusion):
            concl_dict[que[:-6]] = '+' if concl_answers[idx][0].lower() in ('да', 'да.') else '-'

        for answer, help_inf in concl_answers:
            if answer.lower() in ('да', 'да.'):
                comment_list.append(('заключение', help_inf))

        # Получение ответов для соотношения введения и заключения
        relationship_answers = await analyze_relationship(introduction, concl)
        # await message.answer(f"Ответы на соотношение Введения и Заключения: {relationship_answers}")
        rel_dict = {}
        for idx, que in enumerate(que_int_con):
            rel_dict[que[:-6]] = '+' if relationship_answers[idx][0].lower() in ('да', 'да.') else '-'
        concl_dict.update(rel_dict)
        if relationship_answers[0][0].lower() in ('да', 'да.'):
            comment_list.append(('заключение', relationship_answers[0][1]))

        output_path = os.path.join(user_dir, f'output_{document.file_name}')
        get_output_docx(structure_dict, intro_dict, concl_dict, {'fake': 'fake', 'fake2': 'fake'}, output_path, comment_list)

        docx_file = FSInputFile(output_path)

        await message.bot.send_document(chat_id=message.chat.id, document=docx_file)
        os.remove(input_path)
        os.remove(output_path)
    else:
        # Отправляем сообщение, что формат не поддерживается
        await message.answer("Я могу обрабатывать только файлы с расширением .docx.")