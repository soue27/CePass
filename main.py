import os
import config
import mybase
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, filters
from aiogram.utils import executor
from loguru import logger


bot = Bot(config.BotToken)
dp = Dispatcher(bot)
logger.add("debug.log", format="{time} {level} {message}",
           level="DEBUG", rotation="1 week", compression="zip")


async def on_startup(_):
    """При запуске бота: Записывается лог, Открывается БД, сообщение разработчику"""
    print('Готов к работе! Данные обновлены')
    logger.info("Успешный запуск")
    await bot.send_message(317076591, "Готов к работе! Данные обновлены")
    await mybase.open_db()


@dp.message_handler(commands=['start', 'help'])
async def commands_start(message: types.Message) -> None:
    """Обработка команд старт и хелп
    Пользователю выводится справочная информация"""
    await bot.send_message(message.from_user.id, f'Доброго дня! {message.from_user.first_name} '
                                                 f'{message.from_user.last_name},\n'
                                                 f' Я помогу найти пароль к прибору учета СЕ.\n '
                                                 f'Для поиска введите номер, можно не полностью \n\n'
                                                 f'Чтобы добавить новый ПУ необходимо написать команду\n'
                                                 f'add номер пароль, через пробел')

    await message.delete()


@dp.message_handler(filters.Text(startswith='add', ignore_case=True))
async def add(message: types.Message):
    """Добавление пары номер ПУ - пароль в БД
    Проверяется подключение к БД, правильность введенного номера и пароля"""
    pair = message.text.split()[1:3]
    if pair[0].isdigit() and len(pair[0]) > 7 and pair[0].isdigit() and not mybase.search_by_number(pair[0]):
        try:
            mybase.add_to_bd(pair)
        except:
            await message.reply('данные не сохранены, обратитесь к разработчику')
            logger.error("Ошибка с базой данных")
        finally:
            await message.reply('данные добавлены')
            logger.info("Данные добавлены")
    else:
        await message.reply(f'Ошибка: \n'
                            f'В номере и пароле введены не только цифры \n'
                            f'Введен короткий номер (менее 7 цифр) \n'
                            f'Прибор учета с таким номером уже есть в базе')
        logger.info("Ошибка ввода пользователя")


@dp.message_handler(lambda message: message.text.isdigit())
async def search_by_number(message: types.Message):
    """Поиск пары номер ПУ - пароль в БД
    Проверяется подключение к БД, правильность введенного номера и пароля
    Записываются логи, при большом количества найденных номеров > 10 предлагается увеличить длину строки поиска"""
    try:
        passw = mybase.search_by_number(message.text)
        if passw:
            logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                        f' нашел что искал')
            if len(passw) < 10:
                for qw in passw:
                    await message.reply(
                        f'№ ПУ <b>{qw[0]} </b>\n'
                        f'Пароль <b>{qw[1]} </b>\n', parse_mode='HTML')
            else:
                await message.reply(f'Выявлено больше 10 ПУ с номером <b>{message.text}</b> '
                                    f'уточните номер', parse_mode='HTML')
        else:
            await message.reply(f'Пароль для прибора учета <b>{message.text}</b> отсутствует', parse_mode='HTML')
    except:
        await message.reply('ошибка базы данных, обратитесь к разработчику')
        logger.error("Ошибка с базой данных")


@dp.message_handler(content_types='document')
async def my_file(message: types.Message) -> None:
    """Загрузка файла в БД
    Получаются реквизиты файла, сохраняются на диск, запускается функция добавления данных в БД
    Результата логируется
    Если функция add_fromfile() возращает 0, то пользователю выводится сообщение о неверном формате файла"""
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, 'files\\forload.xlsx')
    count, error = mybase.add_fromfile()
    logger.info(f'{message.from_user.first_name} {message.from_user.last_name} {message.from_user.id}'
                f' загрузил файл')
    if count != 0:
        await bot.send_message(message.from_user.id,
                               f"Добавлено: {count} записей; {error} не записано (ошибки в номерах)")
    else:
        await bot.send_message(message.from_user.id, f'Не верный формат файла')
    os.remove('files\\forload.xlsx')


@dp.message_handler(lambda message: not message.text.isdigit())
async def wrong_number(message: types.Message):
    """Обработка неправильно введенного номера ПУ"""
    await message.reply('Вы ввели неправильный номер')
    logger.info("Ошибка ввода номера пользователем")


async def on_shutdown(_):
    """При остановке бота: Закрывается БД
    направляется сообщение разработчику"""
    await bot.send_message(317076591, "Бот отключился, надо что то делать")
    mybase.close_db()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
