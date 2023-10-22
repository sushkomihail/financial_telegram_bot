import sqlite3
import datetime

# подключение к базе данных
con = sqlite3.connect('scopes.db')
cur = con.cursor()

DAY = 'costs'
ALL_TIME = 'alltime'


# получение расходов
def expenses_stat(days_count: int):
    cur.execute(f"SELECT * FROM costs WHERE date >= '{start_date(days_count)}'")
    res = []
    while True:
        row = cur.fetchone()
        if row is None:
            break
        res.append([row[0], row[1], row[2]])
    con.commit()
    return res


# получение даты начала отсчета для статистики
def start_date(days_count: int):
    date = datetime.date.today()
    end = date - datetime.timedelta(days_count)
    return end


# получение текущей даты
def date_now():
    time = datetime.date.today()
    return time


# создание таблицы для расходов за текущий день
def create_table():
    cur.execute("""CREATE TABLE IF NOT EXISTS costs (
        name STRING,
        money FLOAT,
        date NUMERIC
    )""")
    con.commit()


# создание таблицы для расходов за все время
def create_table_for_all_time():
    cur.execute("""CREATE TABLE IF NOT EXISTS alltime (
        name STRING,
        money FLOAT
    )""")
    con.commit()


# внесение нового расхода в таблицу расходов за день
def inset_column(name, money):
    date = date_now()
    insert_values = f"INSERT INTO costs VALUES (?, ?, ?)"
    cur.execute(insert_values, (name, money, date))
    con.commit()


# проверка на то, существует ли такой тип расходов в таблице расходов за день
def execute_columns(name):
    date = date_now()
    cur.execute("SELECT name, date FROM costs")
    res = cur.fetchall()
    if res is None:
        return False
    else:
        if (name, f'{date}') in res:
            return True
        else:
            return False


# внесение нового расхода в таблицу расходов за все время
def inset_column_for_all_time(name, money):
    insert_values = f"INSERT INTO alltime VALUES (?, ?)"
    cur.execute(insert_values, (name, money))
    con.commit()


# проверка на то, существует ли такой тип расходов в таблице расходов за все время
def execute_columns_for_all_time(name):
    cur.execute("SELECT name FROM alltime")
    res = cur.fetchall()
    if res is None:
        return False
    else:
        if (name,) in res:
            return True
        else:
            return False


# прибавление значения расходов в таблице расходов
def plus_money(money: float, name: str, period: str):
    cur.execute(f"SELECT money FROM {period} WHERE name = '{name}'")
    res = cur.fetchone()
    new_money = res[0] + money
    new_value = f"UPDATE {period} SET money = '{new_money}' WHERE name = '{name}'"
    cur.execute(new_value)
    con.commit()


# удаление информации из базы данных
def delete_data():
    cur.execute("DELETE FROM costs")
    cur.execute("DELETE FROM alltime")
    con.commit()


# максимальная сумма расходов за все время
def max_costs():
    maxc = 0
    name = ''
    cur.execute("SELECT * FROM alltime")
    res = cur.fetchall()
    for i in res:
        if i[1] > maxc:
            maxc = i[1]
            name = i[0]
    return name
