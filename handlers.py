import sqlite3
import telebot
from telebot import types
import base64

# Функция для отправки сообщения с изображением и текстовым описанием
def send_message_with_image(chat_id, text, image_data):
    # Декодируем изображение из base64
    decoded_image = base64.b64decode(image_data)

    # Отправляем сообщение с изображением и текстовым описанием
    bot.send_photo(chat_id, photo=decoded_image, caption=text)


# Создание объекта бота
bot = telebot.TeleBot('6852674354:AAESQb_YyTmhvX5d9tTwnAzbkWJkQZvb-dc')

# Словарь для хранения данных сессии
sessions = {}

# Подключение к базе данных SQLite
def connect_to_db():
    return sqlite3.connect('new.db')

# Функция для выполнения запросов к базе данных
def execute_query(query, args=()):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(query, args)
    result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

# Функция для вывода главного меню
def send_main_menu(chat_id, user_first_name):
    # Создаем клавиатуру с пятью кнопками
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = ['Скачать инструкцию', 'Выбрать оглавление', 'Функции', 'Описание принтера', 'Выбрать другой принтер']
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    # Отправляем сообщение с главным меню
    bot.send_message(chat_id, f"Привет, {user_first_name}! Чем я могу тебе помочь?", reply_markup=markup)

# Обработчик команды /start
# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    # Создаем клавиатуру с двумя кнопками
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    buttons = ['Ввести принтер вручную', 'Выбрать принтер из списка']
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])

    # Посылаем приветственное сообщение с запросом ввода названия принтера
    bot.send_message(message.chat.id, "Привет! Как ты хочешь ввести название принтера?", reply_markup=markup)

    # Регистрируем следующий шаг - обработчик выбора способа ввода
    bot.register_next_step_handler(message, choose_input_method)


def choose_input_method(message):
    if message.text == 'Выбрать принтер из списка':
        # Получаем все доступные модели принтеров из базы данных
        printer_models = execute_query('SELECT model FROM Printers')
        if printer_models:
            # Создаем клавиатуру с кнопками для каждой модели принтера
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            buttons = [model[0] for model in printer_models]
            markup.add(*[types.KeyboardButton(btn) for btn in buttons])

            # Посылаем сообщение с просьбой выбрать модель принтера
            bot.send_message(message.chat.id, "Выбери принтер из списка:", reply_markup=markup)

            # Регистрируем следующий шаг - обработчик выбора модели принтера
            bot.register_next_step_handler(message, handle_printer_selection)
        else:
            bot.send_message(message.chat.id, "В базе данных нет доступных моделей принтеров.")
    else:
        # Посылаем сообщение с запросом ввода названия принтера вручную
        bot.send_message(message.chat.id, "Пожалуйста, введи название принтера вручную:")

        # Регистрируем следующий шаг - обработчик ввода названия принтера
        bot.register_next_step_handler(message, find_printer)


def handle_printer_selection(message):
    # Получаем выбранную модель принтера
    selected_printer_model = message.text

    # Выполняем необходимые действия с выбранной моделью принтера, например, сохраняем ее в сессии или выполняем другую логику

    # Отправляем сообщение с выбранной моделью принтера
    bot.send_message(message.chat.id, f"Выбран принтер: {selected_printer_model}")

    # Здесь вы можете добавить дополнительную логику в зависимости от выбранной модели принтера


# Обработчик выбора принтера
def find_printer(message):
    printer_name = message.text
    # Ищем информацию о принтере в базе данных
    printer_info = execute_query('SELECT * FROM Printers WHERE model=?', (printer_name,))
    chat_id = message.chat.id
    if printer_info:
        printer_id = printer_info[0][0]
        # Сохраняем ID принтера в словаре сессии
        sessions[chat_id] = {'printer_id': printer_id}
        # Отправляем главное меню
        send_main_menu(chat_id, message.from_user.first_name)
    else:
        # Если принтер не найден, запрашиваем название принтера еще раз
        bot.send_message(chat_id, f"Принтер с названием '{printer_name}' не найден в базе данных. Попробуйте снова.")
        bot.send_message(chat_id, "Введите название принтера еще раз:")
        bot.register_next_step_handler(message, find_printer)

# Обработчик выбора пунктов главного меню
@bot.message_handler(func=lambda message: True)
def handle_main_menu(message):
    current_menu_item = message.text
    chat_id = message.chat.id
    if current_menu_item == 'Скачать инструкцию':
        handle_printer_link(message)
    elif current_menu_item == 'Выбрать оглавление':
        send_instruction_menu(chat_id)
    elif current_menu_item == 'Функции':
        pass  # Добавьте здесь логику для отображения функций принтера
    elif current_menu_item == 'Описание принтера':
        handle_printer_description(message)
    elif current_menu_item == 'Выбрать другой принтер':
        # Если выбран пункт "Выбрать другой принтер", запрашиваем название принтера
        bot.send_message(chat_id, "Пожалуйста, введите название другого принтера:")
        bot.register_next_step_handler(message, find_printer)

# Обработчик вывода описания принтера
def handle_printer_description(message):
    chat_id = message.chat.id
    printer_id = sessions.get(chat_id, {}).get('printer_id')
    if printer_id:
        # Получаем информацию о принтере из базы данных
        printer_info = execute_query('SELECT model, description FROM Printers WHERE id=?', (printer_id,))
        if printer_info:
            model = printer_info[0][0]
            description_text = printer_info[0][1]
            # Отправляем описание принтера
            bot.send_message(chat_id, f"Описание принтера *{model}*: \n\n{description_text}", parse_mode='Markdown')
        else:
            bot.send_message(chat_id, f"Принтер с id '{printer_id}' не найден в базе данных. Попробуйте снова.")
    else:
        bot.send_message(chat_id, "Не удалось определить принтер. Пожалуйста, выберите принтер заново.")

# Обработчик вывода ссылки на инструкцию
def handle_printer_link(message):
    chat_id = message.chat.id
    printer_id = sessions.get(chat_id, {}).get('printer_id')
    if printer_id:
        # Получаем информацию о принтере из базы данных
        printer_info = execute_query('SELECT model, link FROM Printers WHERE id=?', (printer_id,))
        if printer_info:
            printer_name = printer_info[0][0]
            link = printer_info[0][1]
            # Отправляем ссылку на инструкцию
            bot.send_message(chat_id, f"Ссылка для принтера *{printer_name}*: \n\n{link}", parse_mode='Markdown')
        else:
            bot.send_message(chat_id, f"Принтер с id '{printer_id}' не найден в базе данных. Попробуйте снова.")
    else:
        bot.send_message(chat_id, "Не удалось определить принтер. Пожалуйста, выберите принтер заново.")

# Функция для отправки меню выбора инструкций
def send_instruction_menu(chat_id):
    printer_id = sessions.get(chat_id, {}).get('printer_id')
    if printer_id:
        instructions = execute_query('SELECT id, title FROM Instructions WHERE id=?', (printer_id,))
        if instructions:
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            for instruction in instructions:
                button = types.KeyboardButton(instruction[1])
                markup.add(button)
            bot.send_message(chat_id, "Выберите инструкцию:", reply_markup=markup)
            # Регистрируем следующий шаг - обработчик выбора инструкции
            bot.register_next_step_handler_by_chat_id(chat_id, handle_instruction_choice)
        else:
            bot.send_message(chat_id, "Для этого принтера нет инструкции.")
    else:
        bot.send_message(chat_id, "Не удалось определить принтер. Пожалуйста, выберите принтер заново.")

# Обработчик выбора инструкции
def handle_instruction_choice(message):
    chat_id = message.chat.id
    instruction_title = message.text
    printer_id = sessions.get(chat_id, {}).get('printer_id')
    if printer_id:
        instruction_info = execute_query('SELECT id FROM Instructions WHERE title=? AND id=?', (instruction_title, printer_id))
        if instruction_info:
            instruction_id = instruction_info[0][0]
            # Отправляем меню выбора глав
            send_sections_menu(chat_id, instruction_id, instruction_title)
        else:
            bot.send_message(chat_id, "Инструкция не найдена. Пожалуйста, выберите инструкцию заново.")
    else:
        bot.send_message(chat_id, "Не удалось определить принтер. Пожалуйста, выберите принтер заново.")

# Функция для отправки меню выбора глав
def send_sections_menu(chat_id, instruction_id, instruction_title):
    sections = execute_query('SELECT id, title FROM Sections WHERE id_instruction=?', (instruction_id,))
    if sections:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for section in sections:
            button = types.KeyboardButton(section[1])
            markup.add(button)
        bot.send_message(chat_id, "Выберите главу:", reply_markup=markup)
        # Регистрируем следующий шаг - обработчик выбора главы
        bot.register_next_step_handler_by_chat_id(chat_id, handle_section_choice)
    else:
        bot.send_message(chat_id, "Для этой инструкции нет доступных глав.")

# Обработчик выбора главы
def handle_section_choice(message):
    chat_id = message.chat.id
    section_title = message.text
    printer_id = sessions.get(chat_id, {}).get('printer_id')
    if printer_id:
        sections = execute_query('SELECT id, title FROM Sections WHERE id_instruction=?', (printer_id,))
        section_id = None
        for section in sections:
            if section[1] == section_title:
                section_id = section[0]
                break
        if section_id:
            # Отправляем меню выбора подглав
            send_subsections_menu(chat_id, section_id, section_title)
        else:
            bot.send_message(chat_id, "Выбранная глава не найдена. Пожалуйста, выберите главу заново.")
    else:
        bot.send_message(chat_id, "Не удалось определить принтер. Пожалуйста, выберите принтер заново.")

# Функция для отправки меню выбора подглав
def send_subsections_menu(chat_id, section_id, section_title):
    subsections = execute_query('SELECT id, title FROM Subsections WHERE id_section=?', (section_id,))
    if subsections:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for subsection in subsections:
            button = types.KeyboardButton(subsection[1])
            markup.add(button)
        bot.send_message(chat_id, f"Выберите подглаву для главы:", reply_markup=markup)
        # Регистрируем следующий шаг - обработчик выбора подглавы
        bot.register_next_step_handler_by_chat_id(chat_id, handle_subsection_choice)
    else:
        bot.send_message(chat_id, f"Для главы '{section_title}' нет доступных подглав.")

def send_subsections_menu(chat_id, section_id, section_title, chosen_subsections=None):
    if chosen_subsections is None:
        chosen_subsections = []
    subsections = execute_query('SELECT id, title FROM Subsections WHERE id_section=?', (section_id,))
    if subsections:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for subsection in subsections:
            button = types.KeyboardButton(subsection[1])
            markup.add(button)
        bot.send_message(chat_id, f"Выберите подглаву для главы:", reply_markup=markup)
        # Регистрируем следующий шаг - обработчик выбора подглавы
        bot.register_next_step_handler_by_chat_id(chat_id, lambda message: handle_subsection_choice(message, section_id, section_title, chosen_subsections))
    else:
        bot.send_message(chat_id, f"Для главы '{section_title}' нет доступных подглав.")


import base64

import base64

import base64

def handle_subsection_choice(message, section_id, section_title, chosen_subsections):
    chat_id = message.chat.id
    subsection_title = message.text
    chosen_subsections.append(subsection_title)

    # Получаем ID выбранной подглавы
    subsection_info = execute_query('SELECT id FROM Subsections WHERE title=?', (subsection_title,))
    if subsection_info:
        subsection_id = subsection_info[0][0]

        # Получаем текст из таблицы Steps для выбранной подглавы
        steps = execute_query('SELECT text FROM Steps WHERE id_subsection=?', (subsection_id,))
        if steps:
            text = steps[0][0]
        else:
            text = "Для выбранной подглавы нет текста."

        # Отправляем текст подглавы
        bot.send_message(chat_id, f"Текст подглавы '{subsection_title}':\n\n{text}")

        # Получаем изображения из таблицы StepPhotos для данной подглавы
        photos = execute_query('SELECT photo FROM StepPhotos WHERE step_id=?', (subsection_id,))
        print("Photos from StepPhotos:", photos)  # Отладочное сообщение
        for photo in photos:
            # Декодируем изображение из формата base64 и отправляем его
            decoded_image = base64.b64decode(photo[0])
            send_message_with_image(chat_id, "Изображение:", decoded_image)

    else:
        bot.send_message(chat_id, "Выбранная подглава не найдена. Пожалуйста, выберите подглаву заново.")





# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
