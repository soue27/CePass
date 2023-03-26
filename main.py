from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, filters
from aiogram.utils import executor
from aiogram.types import ContentType, Message
from keyboard import kb_client
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config


storage = MemoryStorage()
bot = Bot(config.BotToken)
dp = Dispatcher(bot, storage=MemoryStorage())


async def on_startup(_):
    print('Готов к работе! Данные обновлены')
    await bot.send_message(317076591, "Готов к работе! Данные обновлены")


@dp.message_handler(commands=['start', 'help'])
async def commands_start(message: types.Message) -> None:
    await bot.send_message(message.from_user.id, f'Доброго дня! {message.from_user.first_name} '
                                                 f'{message.from_user.last_name},'
                                                 f' Я помогу найти пароль к прибору учета СЕ. '
                                                 f'Введите номер, можно не полностью',
                           reply_markup=kb_client)
    await message.delete()


@dp.message_handler(filters.Text(startswith='add', ignore_case=True))
async def search_by_number(message: types.Message):
    print(message.text)
    await message.reply('Можно добавлять номер и пароль')


@dp.message_handler(lambda message: not message.text.isdigit())
async def search_by_number(message: types.Message):
    print(message.text)
    await message.reply('Вы ввели не правильный номер')


@dp.message_handler(lambda message: message.text.isdigit())
async def search_by_number(message: types.Message):
    print(message.text)
    await message.reply('Вы ввели правильный номер')


async def on_shutdown(_):
    await bot.send_message(317076591, "Бот отключился, надо что то делать")

# , on_startup=on_startup, on_shutdown=on_shutdown
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)






