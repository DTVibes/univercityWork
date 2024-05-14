import sqlite3
import telebot
from telebot import types
import base64

def send_message_with_image(chat_id, text, image_data):
    decoded_image = base64.b64decode(image_data)
    bot.send_photo(chat_id, decoded_image)

bot = telebot.TeleBot('6852674354:AAFB5flFuYdLWV9YV_BVHmKQ0MMOs3K-73o')
sessions = {}

def connect_to_db():
    return sqlite3.connect('new.db')

def execute_query(query, args=()):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(query, args)
    result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    buttons = ['Ручной ввод', 'Выбрать из списка']
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    bot.send_message(message.chat.id, "Привет! Как вы хотите ввести название принтера?", reply_markup=markup)
    bot.register_next_step_handler(message, choose_input_method)

def choose_input_method(message):
    if message.text == 'Выбрать из списка':
        printer_models = execute_query('SELECT model FROM Printers')
        if printer_models:
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            buttons = [model[0] for model in printer_models]
            markup.add(*[types.KeyboardButton(btn) for btn in buttons])
            bot.send_message(message.chat.id, "Выберите принтер из списка:", reply_markup=markup)
            bot.register_next_step_handler(message, handle_printer_selection)
        else:
            bot.send_message(message.chat.id, "В базе данных нет доступных моделей принтеров.")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, введите название принтера вручную:")
        bot.register_next_step_handler(message, find_printer)

def handle_printer_selection(message):
    selected_printer_model = message.text
    bot.send_message(message.chat.id, f"Выбран принтер: {selected_printer_model}")
    # Добавим вызов функции, которая находит принтер
    find_printer(message)



def find_printer(message):
    printer_name = message.text
    printer_info = execute_query('SELECT * FROM Printers WHERE model=?', (printer_name,))
    chat_id = message.chat.id
    if printer_info:
        printer_id = printer_info[0][0]
        sessions[chat_id] = {'printer_id': printer_id}
        send_main_menu(chat_id, message.from_user.first_name)
    else:
        bot.send_message(chat_id, f"Принтер с названием '{printer_name}' не найден в базе данных. Попробуйте снова.")
        bot.send_message(chat_id, "Введите название принтера еще раз:")
        bot.register_next_step_handler(message, find_printer)

def send_main_menu(chat_id, user_first_name):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    buttons = ['Скачать инструкцию', 'Пользовательская инструкция','Описание принтера', 'Выбрать другой принтер', 'Инструкция для администратора']
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    bot.send_message(chat_id, f"Привет, {user_first_name}! Чем я могу вам помочь?", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_main_menu(message):
    current_menu_item = message.text
    chat_id = message.chat.id
    if current_menu_item == 'Скачать инструкцию':
        handle_printer_link(message)
    elif current_menu_item == 'Пользовательская инструкция':
        send_instruction_menu(chat_id)
    elif current_menu_item == 'Описание принтера':
        handle_printer_description(message)
    elif current_menu_item == 'Выбрать другой принтер':
        bot.send_message(chat_id, "Пожалуйста, введите название другого принтера:")
        bot.register_next_step_handler(message, find_printer)
    elif current_menu_item == 'Инструкция для администратора':
        send_instruction_menu(chat_id)

def handle_printer_link(message):
    chat_id = message.chat.id
    printer_id = sessions.get(chat_id, {}).get('printer_id')
    if printer_id:
        printer_info = execute_query('SELECT model, link FROM Printers WHERE id=?', (printer_id,))
        if printer_info:
            printer_name = printer_info[0][0]
            link = printer_info[0][1]
            # Отправляем сообщение без форматирования
            bot.send_message(chat_id, f"Ссылка на принтер {printer_name}: \n\n{link}")
        else:
            bot.send_message(chat_id, f"Принтер с id '{printer_id}' не найден в базе данных. Попробуйте снова.")
    else:
        bot.send_message(chat_id, "Не удалось определить принтер. Пожалуйста, выберите принтер заново.")


def handle_printer_description(message):
    chat_id = message.chat.id
    printer_id = sessions.get(chat_id, {}).get('printer_id')
    if printer_id:
        printer_info = execute_query('SELECT model, description FROM Printers WHERE id=?', (printer_id,))
        if printer_info:
            model = printer_info[0][0]
            description_text = printer_info[0][1]
            bot.send_message(chat_id, f"Описание принтера *{model}*: \n\n{description_text}", parse_mode='Markdown')
        else:
            bot.send_message(chat_id, f"Принтер с id '{printer_id}' не найден в базе данных. Попробуйте снова.")
    else:
        bot.send_message(chat_id, "Не удалось определить принтер. Пожалуйста, выберите принтер заново.")

def send_instruction_menu(chat_id):
    # Получаем разделы без указания конкретной инструкции
    sections = execute_query('SELECT id, title FROM Sections')
    if sections:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for section in sections:
            button = types.KeyboardButton(section[1])
            markup.add(button)
        bot.send_message(chat_id, "Выберите раздел:", reply_markup=markup)
        bot.register_next_step_handler_by_chat_id(chat_id, handle_section_choice)
    else:
        bot.send_message(chat_id, "Отсутствуют доступные разделы инструкций.")



def handle_instruction_choice(message):
    chat_id = message.chat.id
    instruction_title = message.text
    printer_id = sessions.get(chat_id, {}).get('printer_id')
    if printer_id:
        instruction_info = execute_query('SELECT id FROM Instructions WHERE title=? AND id=?', (instruction_title, printer_id))
        if instruction_info:
            instruction_id = instruction_info[0][0]
            send_sections_menu(chat_id, instruction_id, instruction_title)
        else:
            bot.send_message(chat_id, "Инструкция не найдена. Пожалуйста, выберите инструкцию снова.")
    else:
        bot.send_message(chat_id, "Не удалось определить принтер. Пожалуйста, выберите принтер заново.")

def send_sections_menu(chat_id, instruction_id, instruction_title):
    sections = execute_query('SELECT id, title FROM Sections WHERE id_instruction=?', (instruction_id,))
    if sections:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for section in sections:
            button = types.KeyboardButton(section[1])
            markup.add(button)
        bot.send_message(chat_id, "Выберите раздел:", reply_markup=markup)
        bot.register_next_step_handler_by_chat_id(chat_id, handle_section_choice)
    else:
        bot.send_message(chat_id, "Для этой инструкции нет доступных разделов.")

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
            send_subsections_menu(chat_id, section_id, section_title)
        else:
            bot.send_message(chat_id, "Выбранный раздел не найден. Пожалуйста, выберите раздел снова.")
    else:
        bot.send_message(chat_id, "Не удалось определить принтер. Пожалуйста, выберите принтер заново.")





def send_subsections_menu(chat_id, section_id, section_title):
    subsections = execute_query('SELECT id, title FROM Subsections WHERE id_section=?', (section_id,))
    if subsections:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for subsection in subsections:
            button = types.KeyboardButton(subsection[1])
            markup.add(button)
        markup.add(types.KeyboardButton("Назад"))  # Добавляем кнопку "Назад" после создания разметки
        bot.send_message(chat_id, f"Выберите подраздел для раздела '{section_title}':", reply_markup=markup)
        # Передаем chat_id, section_id и section_title в функцию handle_subsection_choice
        bot.register_next_step_handler_by_chat_id(chat_id, handle_subsection_choice, section_id=section_id, section_title=section_title)
    else:
        bot.send_message(chat_id, f"Для раздела '{section_title}' нет доступных подразделов.")





def send_text_and_picture(chat_id, text, photo_data):
    if text and photo_data:
        # Если есть и текст, и фото, отправляем их вместе
        message_text = f"{text}\n\n[Изображение]"
        send_message_with_image(chat_id, message_text, photo_data)
    elif text:
        # Если есть только текст, отправляем его
        bot.send_message(chat_id, text)
    elif photo_data:
        # Если есть только фото, отправляем его
        send_message_with_image(chat_id, "[Изображение]", photo_data)
    else:
        # Если и текст, и фото отсутствуют, отправляем сообщение об этом
        bot.send_message(chat_id, "Для выбранного подраздела нет текста или фото.")


def handle_subsection_choice(message, section_id, section_title):
    chat_id = message.chat.id
    subsection_title = message.text
    printer_id = sessions.get(chat_id, {}).get('printer_id')
    if printer_id:
        subsection_info = execute_query('SELECT id FROM Subsections WHERE title=?', (subsection_title,))
        if subsection_info:
            subsection_id = subsection_info[0][0]
            # Retrieve Subsections2 titles
            subsections2_titles = execute_query('SELECT title FROM Subsections2 WHERE id_subsection=?', (subsection_id,))
            if subsections2_titles:
                markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)  # Установка row_width=2
                buttons = [title[0] for title in subsections2_titles]
                markup.add(*[types.KeyboardButton(btn) for btn in buttons])
                markup.add(types.KeyboardButton("Назад"))
                bot.send_message(chat_id, "Выберите подраздел второго уровня:", reply_markup=markup)
                # Передаем section_id и section_title в функцию handle_subsection2_choice
                bot.register_next_step_handler(message, handle_subsection2_choice, section_id=section_id, section_title=section_title)
            else:
                bot.send_message(chat_id, "Для выбранного подраздела нет доступных подразделов второго уровня.")
        else:
            bot.send_message(chat_id, "Выбранный подраздел не найден. Пожалуйста, выберите подраздел снова.")
    else:
        bot.send_message(chat_id, "Не удалось определить принтер. Пожалуйста, выберите принтер заново.")


def handle_subsection2_choice(message, section_id, section_title):
    chat_id = message.chat.id
    subsection_title = message.text
    if subsection_title == "Назад":
        send_subsections_menu(chat_id, section_id, section_title)
        return

    printer_id = sessions.get(chat_id, {}).get('printer_id')
    if printer_id:
        subsection_info = execute_query('SELECT id FROM Subsections2 WHERE title=?', (subsection_title,))
        if subsection_info:
            subsection_id = subsection_info[0][0]
            # Retrieve text from Steps table
            steps = execute_query('SELECT text FROM Steps WHERE id_subsection2=?', (subsection_id,))
            text = '\n\n'.join(step[0] for step in steps) if steps else None

            # Retrieve photos from StepPhotos table
            photos = execute_query('SELECT photo FROM StepPhotos WHERE id_subsection2=?', (subsection_id,))
            photo_data_list = [photo[0] for photo in photos] if photos else None

            # Проверяем наличие текста и фото перед отправкой
            if text is not None or photo_data_list:
                # Отправляем текст с разметкой Markdown, только если он существует
                if text is not None:
                    bot.send_message(chat_id, f"Текст подраздела *{subsection_title}*: \n\n{text}", parse_mode='Markdown')

                # Отправляем фотографии
                if photo_data_list:
                    for photo_data in photo_data_list:
                        send_message_with_image(chat_id, "", photo_data)

                # После отправки информации о текущем подразделе ждем следующего выбора пользователя
                bot.send_message(chat_id, "Выберите еще один подраздел второго уровня или нажмите 'Назад':")
                # Передаем section_id и section_title в функцию handle_subsection2_choice
                bot.register_next_step_handler(message, handle_subsection2_choice, section_id=section_id, section_title=section_title)
            else:
                bot.send_message(chat_id, "Для выбранного подраздела нет текста или фото.")
        else:
            bot.send_message(chat_id, "Выбранный подраздел не найден. Пожалуйста, выберите подраздел снова.")
    else:
        bot.send_message(chat_id, "Не удалось определить принтер. Пожалуйста, выберите принтер заново.")



if __name__ == '__main__':
    bot.polling(none_stop=True)
