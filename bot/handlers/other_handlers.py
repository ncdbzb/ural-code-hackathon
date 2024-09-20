from aiogram import Router
from aiogram.types import Message
from bot.lexicon.lexicon_ru import LEXICON_RU


router = Router()


@router.message()
async def send_echo(message: Message):
    await message.answer(text=LEXICON_RU['error'])
