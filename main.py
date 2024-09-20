import asyncio
import logging

from aiogram import Bot, Dispatcher
from config_data.config import BOT_TOKEN
from bot.handlers import user_handlers, other_handlers
from bot.keyboards.set_main_menu import set_main_menu


# Функция конфигурирования и запуска бота
async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    # Инициализируем бот и диспетчер
    bot = Bot(token=str(BOT_TOKEN), parse_mode='HTML')
    dp = Dispatcher()

    await set_main_menu(bot)

    dp.include_routers(user_handlers.router, other_handlers.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
