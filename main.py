from aiogram import Bot, Dispatcher, executor, types
import logging
import datetime

import config
import db
import analysis as an
import currencies as cur

# задаем уровень логирования(запись логов, которая помогае понять, что происходило во время выполнения кода и позволяет
# избежать множество ошибок). В данном случае уровень логирования - INFO(логирование ошибок, предупреждений и сообщений)
logging.basicConfig(level=logging.INFO)

# инициализируем бота
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

# создаем таблицу для расходов за сегодняшний день
db.create_table()

# создаем таблицу для расходов за все время
db.create_table_for_all_time()

global period, date_start, currency_now


# данная функция проверяет, что в введенном сообщении есть число(целое или дробное), обозначающее сумму расходов
def is_digit(message):
    if message.isdigit():
        return True
    else:
        try:
            float(message)
            return True
        except ValueError:
            return False


# обработка команды "start" для Telegram бота
@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    global date_start
    # удаление информации из базы данных
    db.delete_data()

    # получение текущей даты
    time = datetime.date.today()

    date_start = time
    await message.answer('Привет!\nЯ помогу тебе следить за расходами!\nВведите ваши расходы(в рублях), например: '
                         'продукты 500')
    await message.answer('Чтобы посмотреть команды бота, введите - /help')


# обработка команды "day" для Telegram бота, которая выдает статистику расходов за день
@dp.message_handler(commands=['day'])
async def day_message(message: types.Message):
    # получение наиболее затратной категории товаров за день, общей суммы расходов за день, предположение бота
    # по затратам за неделю и за месяц
    most_expensive, costs_of_day, costs_of_week, costs_of_month = an.analytic_of_day()

    # получение всех расходов за день
    res = db.expenses_stat(1)

    if len(res) != 0:
        for i in res:
            await message.answer(f'{i[0]} - {i[1]}, {i[2]}')
        await message.answer(f'* За сегодняшний день вы потратили - {costs_of_day} руб.\n'
                             f'* Если вы будете тратить деньги с такой же интенсивностью, то к конце недели вы '
                             f'потратите - {costs_of_week} руб., а к концу месяца - {costs_of_month} руб.\n'
                             f'* {most_expensive}')
    else:
        await message.answer('Вы не совершали никаких расходов за сегодня')


# обработка команды "week" для Telegram бота, которая выдает статистику расходов за неделю
@dp.message_handler(commands=['week'])
async def week_message(message: types.Message):
    # получение наиболее затратной категории товаров за неделю, общей суммы расходов за неделю, предположение бота
    # по затратам за месяц
    most_expensive, costs_of_week, costs_of_month = an.analytic_of_week()

    # получение всех расходов за неделю
    res = db.expenses_stat(7)

    if len(res) != 0:
        for i in res:
            await message.answer(f'{i[0]} - {i[1]}, {i[2]}')
        await message.answer(f'* За неделю вы потратили - {costs_of_week} руб.\n'
                             f'* Если вы будете тратить деньги с такой же интенсивностью, то к концу месяца '
                             f'вы потратите - {costs_of_month} руб.\n* {most_expensive}')
    else:
        await message.answer('Вы не совершали никаких расходов за неделю')


# обработка команды "month" для Telegram бота, которая выдает статистику расходов за месяц
@dp.message_handler(commands=['month'])
async def month_message(message: types.Message):
    # получение наиболее затратной категории товаров за месяц, общей суммы расходов за месяц, предположение бота
    # по затратам за год
    most_expensive, costs_of_month, costs_of_year = an.analytic_of_month()

    # получение всех расходов за месяц
    res = db.expenses_stat(30)
    if len(res) != 0:
        for i in res:
            await message.answer(f'{i[0]} - {i[1]}, {i[2]}')
        await message.answer(f'* За месяц вы потратили - {costs_of_month} руб.\n'
                             f'* Если вы будете тратить деньги с такой же интенсивностью, то к концу года '
                             f'вы потратите - {costs_of_year} руб.\n* {most_expensive}')
    else:
        await message.answer('Вы не совершали никаких расходов за месяц')


# обработка команды "help" для Telegram бота, которая выводит все возможные команды Telegram бота
@dp.message_handler(commands=['help'])
async def help_message(message: types.Message):
    await message.answer('* Посмотреть статистику за день - /day\n* Посмотреть статистику за неделю - /week\n'
                         '* Посмотреть статистику за месяц - /month\n* Получить рекомендации от бота - '
                         '/recommendations\n* Узнать курс валют - /currency\n* Расссчитать кредит - /credit\n* '
                         'Удалить данные о платежах - /del\n* Посмотреть категории товаров - /categories')


# обработка команды "categories" для Telegram бота
@dp.message_handler(commands=['categories'])
async def cat_message(message: types.Message):
    await message.answer('* Продукты\n* Такси\n'
                         '* Спорт\n* Общественный транспорт\n* Одежда\n* Развлечения')


# обработка команды "currency" для Telegram бота, которая выводит курс различных валют в рублях
@dp.message_handler(commands=['currency'])
async def currency(message: types.Message):
    await message.answer(f'1 USD = {an.currency(cur.USD)} RUB (доллары в рублях)\n'
                         f'1 EUR = {an.currency(cur.EUR)} RUB (евро в рублях)\n'
                         f'1 BYN = {an.currency(cur.BYN)} RUB (белорусские рубли в рублях)\n'
                         f'1 KZT = {an.currency(cur.KZT)} RUB (теньге в рублях)\n'
                         f'1 GBP = {an.currency(cur.GBP)} RUB (фунты стерлингов в рублях)\n'
                         f'1 CHF = {an.currency(cur.CHF)} RUB (швейцарские франки в рублях)')


# обработка команды "recommendations" для Telegram бота, которая выдает наиболее выгодные предложения на товары или
# услуги на основе затрат пользователя
@dp.message_handler(commands=['recommendations'])
async def recom(message: types.Message):
    # получаем наиболее выгодные цены на продукты
    prod = an.all_prod()

    # получаем наиболее выгодные цены на такси
    taxi = an.sort_taxi()

    # получаем наиболее выгодные цены на одежду
    cl = an.all_clothes()

    # получаем категорию товаров, на которую пользователь потратил наибольшее количество средств
    name = db.max_costs()
    if name != 'продукты' and name != 'такси' and name != 'одежда':
        await bot.send_message(message.chat.id,
                               f'На данный момент бот не может дать каких-либо рекомендаций')
    else:
        await bot.send_message(message.chat.id, f'Был произведен анализ ваших расходов, в результате которого '
                                                f'выявилось, '
                                                f'что вы тратите большое количество денег на {name}. На основе этого '
                                                f'бот '
                                                f'выдаст наиболее выгодные цены на товары или услуги')
        if name == 'продукты':
            await bot.send_message(message.chat.id, f'Самые выгодные продукты по акциям в Барнауле можно приобрести в '
                                                    f'магазине Мария-Ра - '
                                                    f'https://www.maria-ra.ru/aktsii/myaso-ptitsa-kolbasa/:')
            for i in prod:
                await bot.send_photo(message.chat.id, i['image'], f'НАЗВАНИЕ: {i["title"]}\nСТОИМОСТЬ: {i["price"]} руб.')
        elif name == 'такси':
            await bot.send_message(message.chat.id, f'Самые выгодные такси Барнаула:')
            for j in taxi:
                await bot.send_message(message.chat.id, f'* НАЗВАНИЕ: {j["title"]}\n* СТОИМОСТЬ: {j["price"]}\n* ВРЕМЯ '
                                                        f'РАБОТЫ: {j["time"]}\n* СПОСОБ ОПЛАТЫ: {j["pay"]}\n* ТЕЛЕФОН: '
                                                        f'{j["phone"]}')
        elif name == 'одежда':
            await bot.send_message(message.chat.id, f'Наиболее выгодно можно купить одежду в магазине OODJI - '
                                                    f'https://www.oodji.com/')
            for k in cl:
                await bot.send_photo(message.chat.id, k['image'], f'НАЗВАНИЕ: {k["title"]}\nСТОИМОСТЬ: {k["price"]} руб.')


# обработка команды "credit" для Telegram бота
@dp.message_handler(commands=['credit'])
async def credit(message: types.Message):
    await message.answer('Введите: сумму кредита, срок(в годах), процент\nНапример: 1000000 15 20')


# обработка команды "del" для Telegram бота, которая удаляет данные из БД
@dp.message_handler(commands=['del'])
async def delete(message: types.Message):
    # удаление данных из БД
    db.delete_data()
    await message.answer('Данные о платежах удалены')


# обработка введенных значений
@dp.message_handler()
async def add_costs(message: types.Message):
    message.text.replace(',', '.')
    text = message.text.lower().split(' ')
    if is_digit(text[-1]) and len(text) != 3:
        if db.execute_columns_for_all_time(text[0]):
            db.plus_money(float(text[-1]), text[0], db.ALL_TIME)
        else:
            db.inset_column_for_all_time(text[0], float(text[-1]))
    if is_digit(text[-1]) and len(text) != 3:
        if db.execute_columns(text[0]):
            db.plus_money(float(text[-1]), text[0], db.DAY)
        else:
            db.inset_column(text[0], float(text[-1]))
        await bot.send_message(message.chat.id, 'Расходы занесены в базу данных')
        await bot.send_message(message.chat.id, 'Введите ваши расходы(в рублях), например: продукты 500')
    elif is_digit(text[0]) and is_digit(text[1]) and is_digit(text[2]) and len(text) == 3:
        month, total = an.credit_ann(float(text[0]), float(text[1]), float(text[2]))
        months, total1 = an.credit_dif(float(text[0]), float(text[1]), float(text[2]))
        await bot.send_message(message.chat.id, f'Аннуитетный платеж:\n   '
                                                f'* Ежемесячный платеж составит {month} руб.\n   '
                                                f'* Общая сумма выплат составит {total} руб.')
        await bot.send_message(message.chat.id, f'Дифференцированный платеж:\n   '
                                                f'* Ежемесячные платежи составят {months} руб.\n   '
                                                f'* Общая сумма выплат составит {total1} руб.')
    else:
        await bot.send_message(message.chat.id, 'Вы ввели неверные данные')


# запускаем Long Polling(технология, которая позволяет получать данные о новых событиях с помощью «длинных запросов».
# Сервер получает запрос, но отправляет ответ на него не сразу, а лишь тогда, когда произойдет какое-либо
# событие (например, придёт новое сообщение), либо истечет заданное время ожидания.)
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
