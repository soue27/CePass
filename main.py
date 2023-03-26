from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, filters
from aiogram.utils import executor
from aiogram.types import ContentType, Message
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config
import mybase

storage = MemoryStorage()
bot = Bot(config.BotToken)
dp = Dispatcher(bot, storage=MemoryStorage())


async def on_startup(_):
    print('Готов к работе! Данные обновлены')
    await bot.send_message(317076591, "Готов к работе! Данные обновлены")
    await mybase.open_db()


@dp.message_handler(commands=['start', 'help'])
async def commands_start(message: types.Message) -> None:
    await bot.send_message(message.from_user.id, f'Доброго дня! {message.from_user.first_name} '
                                                 f'{message.from_user.last_name},'
                                                 f' Я помогу найти пароль к прибору учета СЕ. '
                                                 f'Введите номер, можно не полностью',
                           reply_markup=kb_client)
    await message.delete()


# add 666666 777777 000000
@dp.message_handler(filters.Text(startswith='add', ignore_case=True))
async def search_by_number(message: types.Message):
    pair = message.text.split()[1:3]
    if pair[0].isdigit() and pair[0].isdigit():
        try:
            mybase.add_to_bd(pair)
        except:
            await message.reply('данные не сохранены, обратитесь к разработчику')
        finally:
            await message.reply('данные добавлены')
    else:
        await message.reply('ошибка во вводе данных')


@dp.message_handler(lambda message: not message.text.isdigit())
async def search_by_number(message: types.Message):
    await message.reply('Вы ввели неправильный номер')


@dp.message_handler(lambda message: message.text.isdigit())
async def search_by_number(message: types.Message):
    print(message.from_user.first_name, message.from_user.last_name, message.from_user.id)
    try:
        passw = mybase.search_by_number(message.text)
        if passw:
            for qw in passw:
                await message.reply(
                    f'№ ПУ <b>{qw[0]} </b>\n'
                    f'Пароль <b>{qw[1]} </b>\n', parse_mode='HTML')
        else:
            await message.reply(f'Пароль для прибора учета <b>{message.text}</b> отсутствует', parse_mode='HTML')
    except:
        await message.reply('ошибка базы данных, обратитесь к разработчику')


async def on_shutdown(_):
    await bot.send_message(317076591, "Бот отключился, надо что то делать")
    mybase.close_db()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
