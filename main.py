import telebot
from telebot import types
import psycopg2

# Токен бота 
bot = telebot.TeleBot('TOKEN')

# Подключение к бд
# Все пользователи данного бота работают в пределах одной БД и пользуются одним юзером
con = psycopg2.connect(
database="db_bot_tg", 
user="user_bot_tg", 
password='1', 
host="127.0.0.1", 
port="5432"
)
con.autocommit = True
cursor = con.cursor()

# Обработчик ждет пока его запустят
@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton('Покупки')
    button2 = types.KeyboardButton('Показать покупки')
    button3 = types.KeyboardButton('Дела')
    button4 = types.KeyboardButton('Показать дела')
    button5 = types.KeyboardButton('Перезапустить бота')
    markup.row(button1, button2)
    markup.row(button3, button4)
    markup.row(button5)

    # получение уникального и неизменного ID пользователя
    # с его помощью бот распознает с какой таблицей работать
    get_user_id = 'user_'+ str(message.from_user.id)
    
    # если нет таблицы для полученного ID, то создает ее
    table_lookup = cursor.execute("""create table if not exists %s(
      id SERIAL PRIMARY KEY,
      name_user varchar(35),
      information text, 
      type_information varchar(5));""" %(get_user_id))

    # ждет выбора действия согласно кнопкам и переходит в следующую функцию
    next_step = bot.send_message(message.chat.id, 'Выберите дейтвие:', reply_markup=markup)
    bot.register_next_step_handler(next_step, start_menu)

# какую кнопку нажали, в ту функцию бот идет
def start_menu(message):
    if message.text == 'Покупки':
        shops_menu(message)
    elif message.text == 'Показать покупки':
        show_shops_in_start(message)
    elif message.text == 'Дела':
        tasks_menu(message)
    elif message.text == 'Показать дела':
        show_tasks_in_start(message)


# позволяет выйти в главное меню из любой точки
# нужно в том случае, если бот выключился не в самом начале программы, что бы не писать /start
@bot.message_handler(content_types=['text'])
def start_back(message):
    if message.text == 'Вернуться назад':
        start(message)
    if message.text == 'Перезапустить бота':
        start(message)

# раздел покупок
def shops_menu(message):
    markup = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton('Добавить покупку')
    button2 = types.KeyboardButton('Показать покупки')
    button3 = types.KeyboardButton('Удалить покупку')
    button4 = types.KeyboardButton('Вернуться назад')

    markup.row(button1, button2)
    markup.row(button3, button4)
    next_step = bot.send_message(message.chat.id, 'Вы в разделе "ПОКУПКИ"', reply_markup=markup)
    # бот ждет нажатия кнопки, что бы в следующей шаге проследовать к нужной функции
    bot.register_next_step_handler(next_step, shops_menu_start)

# следует согласно нажатой кнопке
def shops_menu_start(message):
    if message.text == 'Добавить покупку':
        what_add_in_shop(message)
    elif message.text == 'Показать покупки':
        show_shops(message)
    elif message.text == 'Удалить покупку':
        what_del_in_shop(message)
    elif message.text == 'Вернуться назад':
        start_back(message)


# задает вопрос что добавить и ожидает действие пользователя
def what_add_in_shop(message):
    add_message = bot.send_message(message.chat.id, 'К покупкам добавить:')
    # ждет ответ пользователя
    bot.register_next_step_handler(add_message, add_in_shop)


# добавляет в список покупок ответ пользователя
def add_in_shop(message):
    # получение имени пользователя (изменяемое - ненадежное) для отображении в таблице
    # необходимо для root пользователя
    get_name = message.from_user.first_name +"_"+ message.from_user.last_name
    # получение уникального ID 
    get_user_id = 'user_'+ str(message.from_user.id)
    # запрос к БД
    insert_table = cursor.execute("""INSERT INTO  %s(
    name_user, information, type_information) 
    VALUES('%s', '%s', 'shops')"""%(get_user_id, get_name, message.text))
    # возврат в раздел покупок
    shops_menu(message)


# функция удаления строки из раздела покупок
def what_del_in_shop(message):
    del_message = bot.send_message(message.chat.id, 'Удалить элемент:')
    # ожидает ответа пользователя и передает его в следующую функцию
    bot.register_next_step_handler(del_message, del_in_shop)


# получает ответ пользователя
def del_in_shop(message):
    # получение уникального ID 
    get_user_id = 'user_'+ str(message.from_user.id)
    # поиск в таблице "ответ пользователя" с пометкой shop
    get_me_word = cursor.execute("""SELECT FROM %s WHERE information='%s' and type_information='shops';""" %(get_user_id, message.text))
    # если возвращаемое значениеи None(0 строк в таблице), то переменной присваевается пустой список [], если есть совпадения, то пустой кортеж в списке [()]
    out_rows = cursor.fetchall()
    # если БД вернуло пустой список [], то осуществляется уведомление об ошибке
    if out_rows==[]:
        bot.send_message(message.from_user.id, 'ОШИБКА: нет таких элементов, необходимо ввести в точности')
        shops_menu(message)
    # елси поиск был успешный, то идет запрос DELETE
    else:
        delete_table = cursor.execute("""DELETE FROM %s 
        where information='%s' and type_information='shops';
        """%(get_user_id, message.text))
        # возврат в раздел  покупок
        shops_menu(message)


# посмотреть список покупок не заходя в раздел покупок
def show_shops_in_start(message):
    # получение уникального ID 
    get_user_id = 'user_'+ str(message.from_user.id)
    # возврат записей с пометкой shops
    return_shops = cursor.execute("""SELECT information FROM %s 
    WHERE type_information='shops';""" %(get_user_id))
    # присвоение ответу переменной
    list_return = cursor.fetchall()
    # выведение по одному сообщению всего списка покупок благодаря циклу
    for i in list_return:
        bot.send_message(message.from_user.id, i)
    # уведомление о том, что БД вернула весь список
    bot.send_message(message.from_user.id, '----[КОНЕЦ СПИСКА]----')
    # возврат в начало
    start(message)

# возврат списка покупок из раздела покупок
def show_shops(message):
    # получение уникального ID 
    get_user_id = 'user_'+ str(message.from_user.id)
    # возврат записей с пометкой shops
    return_shops = cursor.execute("""SELECT information FROM %s 
    WHERE type_information='shops';""" %(get_user_id))
    # присвоение ответу переменной
    list_return = cursor.fetchall()
    # выведение по одному сообщению всего списка покупок благодаря циклу
    for i in list_return:
        bot.send_message(message.from_user.id, i)
        # уведомление о том, что БД вернула весь список
    bot.send_message(message.from_user.id, '----[КОНЕЦ СПИСКА]----')
    # возврат в начало
    shops_menu(message)

# раздел дела
def tasks_menu(message):
    markup = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton('Добавить дело')
    button2 = types.KeyboardButton('Показать дела')
    button3 = types.KeyboardButton('Удалить дело')
    button4 = types.KeyboardButton('Вернуться назад')

    markup.row(button1, button2)
    markup.row(button3, button4)
    next_step = bot.send_message(message.chat.id, 'Вы в разделе "ДЕЛА"', reply_markup=markup)
    # бот ждет нажатия кнопки, что бы в следующей шаге проследовать к нужной функции
    bot.register_next_step_handler(next_step, tasks_menu_start)

#  следует согласно нажатой кнопке
def tasks_menu_start(message):
    if message.text == 'Добавить дело':
        what_add_in_tasks(message)
    elif message.text == 'Показать дела':
        show_tasks(message)
    elif message.text == 'Удалить дело':
        what_del_in_tasks(message)
    elif message.text == 'Вернуться назад':
        start_back(message)


# задает вопрос что добавить и ожидает действие пользователя
def what_add_in_tasks(message):
    add_message = bot.send_message(message.chat.id, 'К списку дел добавить:')
    bot.register_next_step_handler(add_message, add_in_tasks)

# добавляет в список задач ответ пользователя
def add_in_tasks(message):
    # получение имени пользователя (изменяемое - ненадежное) для отображении в таблице
    # необходимо для root пользователя
    get_name = message.from_user.first_name +"_"+ message.from_user.last_name
    # получение уникального ID 
    get_user_id = 'user_'+ str(message.from_user.id)
    # запрос к БД
    insert_table = cursor.execute("""INSERT INTO  %s(
    name_user, information, type_information) 
    VALUES('%s', '%s', 'tasks')"""%(get_user_id, get_name, message.text))
    # возврат в раздел задач
    tasks_menu(message)


# функция удаления строки из раздела задач
def what_del_in_tasks(message):
    del_message = bot.send_message(message.chat.id, 'Удалить элемент:')
    # ожидает ответа пользователя и передает его в следующую функцию
    bot.register_next_step_handler(del_message, del_in_tasks)


# получает ответ пользователя
def del_in_tasks(message):
    get_user_id = 'user_'+ str(message.from_user.id)
    # получение уникального ID 
    get_me_word = cursor.execute("""SELECT information FROM %s WHERE information='%s' and type_information='tasks';""" %(get_user_id, message.text))
    # если возвращаемое значениеи None(0 строк в таблице), то переменной присваевается пустой список [], если есть совпадения, то пустой кортеж в списке [()]
    out_rows = cursor.fetchall()
    # если БД вернуло пустой список [], то осуществляется уведомление об ошибке
    if out_rows==[]:
        bot.send_message(message.from_user.id, 'ОШИБКА: нет таких элементов, необходимо ввести в точности')
        tasks_menu(message)
    # елси поиск был успешный, то идет запрос DELETE    
    else:
        delete_table = cursor.execute("""DELETE FROM %s 
        where information='%s' and type_information='tasks';
        """%(get_user_id, message.text))
        # возврат в раздел  задач
        tasks_menu(message)


# посмотреть список задач не заходя в раздел задач
def show_tasks_in_start(message):
     # получение уникального ID 
    get_user_id = 'user_'+ str(message.from_user.id)
    # возврат записей с пометкой shops
    return_shops = cursor.execute("""SELECT information FROM %s 
    WHERE type_information='tasks';""" %(get_user_id))
     # присвоение ответу переменной
    list_return = cursor.fetchall()
    # выведение по одному сообщению всего списка задач благодаря циклу
    for i in list_return:
        bot.send_message(message.from_user.id, i)
    # уведомление о том, что БД вернула весь список
    bot.send_message(message.from_user.id, '----[КОНЕЦ СПИСКА]----')
    # возврат в начало
    start(message)


# возврат списка хадач из раздела задач
def show_tasks(message):
    get_user_id = 'user_'+ str(message.from_user.id)
     # получение уникального ID 
    return_shops = cursor.execute("""SELECT information FROM %s 
    WHERE type_information='tasks';""" %(get_user_id))
    # присвоение ответу переменной
    list_return = cursor.fetchall()
    # выведение по одному сообщению всего списка покупок благодаря циклу
    for i in list_return:
        bot.send_message(message.from_user.id, i)
        # уведомление о том, что БД вернула весь список
    bot.send_message(message.from_user.id, '----[КОНЕЦ СПИСКА]----')
    # возврат в начало
    tasks_menu(message)


# запуск бота
# бот спрашивает сервера телеги о новых сообщениях - постоянно (none_stop=True)
# с интервалом в 0 секунд (interval=0)
bot.polling(none_stop=True, interval=0)
