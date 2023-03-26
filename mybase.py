import sqlite3
import os

global connect, cursor


async def open_db():
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


# async def create_db(base_name: str, spisok: list):
#     # Создание таблицы базы данных, на основании полученного списка из парсинга эксель файла.
#     # На входе имя базы данных и список загрузки
#     connect = sqlite3.connect(base_name)
#     cursor = connect.cursor()
#     cursor.execute('CREATE TABLE IF NOT EXISTS dis (contract, counterparty, city, point, street, house, tp)')
#     sqlite_insert_query = """INSERT INTO dis
#                                  (contract, counterparty, city, point, street, house, tp)
#                                  VALUES (?, ?, ?, ?, ?, ?, ?);"""
#     cursor.executemany(sqlite_insert_query, spisok)
#     connect.commit()
#     connect.close()


def search_by_number(number: str):
    # Функция поиска по ноиеру прибора учета: str,
    results = cursor.execute(f"SELECT * FROM pass WHERE number LIKE '%{number.lower()}%'").fetchall()
    return results


def add_to_bd(newpass: list):
    # Добавляет новую пару №ПУ- Пароль в базу данных
    cursor.execute("INSERT INTO pass VALUES (?, ?);",
                   (newpass[0], newpass[1]))
    connect.commit()
