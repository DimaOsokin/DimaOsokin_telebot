import telebot
from telebot import types


bot = telebot.TeleBot('TOKEN')


shops = []  # что список покупок
tasks = []  # список дел


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton('Покупки')
    button2 = types.KeyboardButton('Показать покупки')
    button3 = types.KeyboardButton('Дела')
    button4 = types.KeyboardButton('Показать дела')
    button5 = types.KeyboardButton('/start')

    markup.row(button1, button2)
    markup.row(button3, button4)
    markup.row(button5)
    bot.send_message(message.chat.id, 'Какое действие', reply_markup=markup)

    next_step = bot.send_message(message.chat.id, 'ты выбираешь?')
    bot.register_next_step_handler(next_step, start_menu)


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
@bot.message_handler(content_types=['text'])
def start_back(message):
    if message.text == 'Вернуться назад':
        start(message)


def shops_menu(message):
    markup = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton('Добавить покупку')
    button2 = types.KeyboardButton('Показать покупки')
    button3 = types.KeyboardButton('Удалить покупку')
    button4 = types.KeyboardButton('Вернуться назад')

    markup.row(button1, button2)
    markup.row(button3, button4)
    bot.send_message(message.chat.id, 'Вы в разделе "ПОКУПКИ"', reply_markup=markup)

    next_step = bot.send_message(message.chat.id, 'Что делать дальше?')
    bot.register_next_step_handler(next_step, shops_menu_start)


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
    bot.register_next_step_handler(add_message, add_in_shop)

# добавляет в список покупок ответ пользователя
def add_in_shop(message):
    shops.append(message.text)
    shops_menu(message)


def what_del_in_shop(message):
    del_message = bot.send_message(message.chat.id, 'Удалить элемент:')
    bot.register_next_step_handler(del_message, del_in_shop)


def del_in_shop(message):
    try:
        shops.remove(message.text)
        shops_menu(message)
    except ValueError:
        bot.send_message(message.from_user.id, 'ОШИБКА: нет похожих элементов, попробуйте снова')
        shops_menu(message)



def show_shops_in_start(message):
    for i in shops:
        bot.send_message(message.from_user.id, i)
    bot.send_message(message.from_user.id, '----[КОНЕЦ СПИСКА]----')
    start(message)


def show_shops(message):
    for i in shops:
        bot.send_message(message.from_user.id, i)
    bot.send_message(message.from_user.id, '----[КОНЕЦ СПИСКА]----')
    shops_menu(message)


def tasks_menu(message):
    markup = types.ReplyKeyboardMarkup()
    button1 = types.KeyboardButton('Добавить дело')
    button2 = types.KeyboardButton('Показать дела')
    button3 = types.KeyboardButton('Удалить дело')
    button4 = types.KeyboardButton('Вернуться назад')

    markup.row(button1, button2)
    markup.row(button3, button4)
    bot.send_message(message.chat.id, 'Вы в разделе "ДЕЛА"', reply_markup=markup)

    next_step = bot.send_message(message.chat.id, 'Что делать дальше?')
    bot.register_next_step_handler(next_step, tasks_menu_start)


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
    add_message = bot.send_message(message.chat.id, 'К покупкам добавить:')
    bot.register_next_step_handler(add_message, add_in_tasks)

# добавляет в список покупок ответ пользователя
def add_in_tasks(message):
    tasks.append(message.text)
    tasks_menu(message)

def what_del_in_tasks(message):
    del_message = bot.send_message(message.chat.id, 'Удалить элемент:')
    bot.register_next_step_handler(del_message, del_in_tasks)

def del_in_tasks(message):
    try:
        tasks.remove(message.text)
        tasks_menu(message)
    except ValueError:
        bot.send_message(message.from_user.id, 'ОШИБКА: нет похожих элементов, попробуйте снова')
        tasks_menu(message)

def show_tasks_in_start(message):
    for i in tasks:
        bot.send_message(message.from_user.id, i)
    bot.send_message(message.from_user.id, '----[КОНЕЦ СПИСКА]----')
    start(message)


def show_tasks(message):
    for i in tasks:
        bot.send_message(message.from_user.id, i)
    bot.send_message(message.from_user.id, '----[КОНЕЦ СПИСКА]----')
    tasks_menu(message)


bot.polling(none_stop=True, interval=0)
