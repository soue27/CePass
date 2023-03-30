import sqlite3
import os
import openpyxl

global connect, cursor


async def open_db():
    """Функция для открытия базы данных, проверяется наличие файла базы данных
    и наличие таблицы в БД"""
    global connect, cursor
    if os.path.exists('sepass.sqlite3'):
        connect = sqlite3.connect('sepass.sqlite3')
        cursor = connect.cursor()
        cursor.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='pass' ''')
        if cursor.fetchone()[0] == 1:
            print('База данных подключена')
        else:
            print('что то пошло не так')
    else:
        print('что то пошло не так? обратитесь к разработчку, нет файла')


def close_db():
    connect.commit()
    connect.close()


def search_by_number(number: str):
    """Функция поиска по номеру прибора учета"""
    results = cursor.execute(f"SELECT * FROM pass WHERE number LIKE '%{number.lower()}%'").fetchall()
    return results


def add_to_bd(newpass: list):
    """Добавляет новую пару №ПУ- Пароль в базу данных"""
    cursor.execute("INSERT INTO pass VALUES (?, ?);", (newpass[0], newpass[1]))
    connect.commit()


def add_fromfile():
    """Функция добавления данных из файла в базу данных
    Файл ексель проверяется на соответствие формату, на наличие вкладок
    Проверяется наличие столбцов не менее 2
    Значения строк проверяются - явлюятся ли они цифрами, если нет - то данная строка не добавляется в базу данных
    инкрементируется счетчик ошибочных данных
    Фунция возращает 2 значения: Количество добавленных строк в базу данных и количество ошибочных строк
    """
    error_count = 0
    try:
        wb = openpyxl.load_workbook("files\\forload.xlsx")
        ws = wb.active
    except:
        return 0, 0
    if ws.max_column - ws.min_column >= 1:
        for i in range(ws.min_row, ws.max_row + 1):
            if str(ws.cell(i, ws.min_column).value).isdigit() and str(ws.cell(i, ws.min_column + 1).value).isdigit():
                cursor.execute("INSERT INTO pass VALUES (?, ?);",
                               (ws.cell(i, ws.min_column).value, ws.cell(i, ws.min_column + 1).value))
            else:
                error_count += 1
        connect.commit()
    else:
        return 0, 0
    return ws.max_row - ws.min_row + 1 - error_count, error_count


if __name__ == '__main__':
    print(add_fromfile())
