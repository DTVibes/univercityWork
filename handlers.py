from aiogram import Bot, types, Dispatcher, executor
from aiogram import Bot, types, Dispatcher, executor
from sql import save_contact_to_database

# Подключение к API Telegram
bot = Bot(token='6781534893:AAFCBKyrHMID3lpFRqWSyGaWGK5wA3ng7yU')
dp = Dispatcher(bot)



@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    help_text = "Привет! Я бот для предоставления инструкций по оборудованию Triumph-Adler.\n\n"
    help_text += "Доступные команды:\n"
    help_text += "/start - Начало работы с ботом\n"
    help_text += "/help - Получить помощь и список команд\n"
    help_text += "/instructions - Получить инструкции по оборудованию\n"
    help_text += "/support - Обратиться за поддержкой\n"
    help_text += "/feedback - Оставить отзыв\n"
    help_text += "/site - Открыть официальный сайт Triumph-Adler\n"

    await message.reply(help_text)

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Инструкции')
    btn2 = types.KeyboardButton('Поддержка')
    btn3 = types.KeyboardButton('Обратная связь')
    markup.add(btn1, btn2, btn3)


    photo_path = 'pictures/file.jpg'
    with open(photo_path, mode='rb') as photo:
        await bot.send_photo(message.chat.id, photo)

    await bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! Чем я могу тебе помочь?\n"
        f"Вы можете обратиться к команде /help, чтобы посмотреть всевозможные команды",
        reply_markup= markup
    )


@dp.message_handler(commands=['site'])
async def process_site_command(message: types.Message):
    # Создаем инлайн-клавиатуру с кнопкой, которая откроет сайт
    markup = types.InlineKeyboardMarkup()
    site_button = types.InlineKeyboardButton(text='Открыть сайт', url='https://www.triumph-adler.com')
    markup.add(site_button)
 # Отправляем сообщение с инлайн-клавиатурой
    await bot.send_message(message.chat.id, "Нажмите кнопку, чтобы открыть сайт:", reply_markup=markup)


@dp.message_handler(lambda message: message.text == 'Обратная связь')
async def process_support_button(message: types.Message):
    feedback_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    positive_btn = types.KeyboardButton('👍 Положительная', callback_data='positive_feedback')
    negative_btn = types.KeyboardButton('👎 Отрицательная', callback_data='negative_feedback')
    back_btn = types.KeyboardButton('Назад')
    feedback_markup.row(positive_btn, negative_btn)
    feedback_markup.row(back_btn)

    await message.reply("Оставьте ваш отзыв:", reply_markup=feedback_markup)

@dp.message_handler(lambda message: message.text == '👍 Положительная' )
async def process_feedback_button(message: types.Message):
    await message.answer("Спасибо, Чушпан!")

@dp.message_handler(lambda message: message.text == '👎 Отрицательная' )
async def process_feedback_button(message: types.Message):
    await message.answer("Больше не приходи сюда")
    await bot.send_sticker(message.chat.id, sticker = "CAACAgEAAxkBAAELNCNlqBRu7ClX26Hd5_wX-IM24mky2wAC8gEAAufQ0xnLvDvqVrO-0TQE")

@dp.message_handler(lambda message: message.text == 'Назад')
async def process_back_button(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Инструкции')
    btn2 = types.KeyboardButton('Поддержка')
    btn3 = types.KeyboardButton('Обратная связь')
    markup.add(btn1, btn2, btn3)

    await message.answer("Вы вернулись в главное меню:", reply_markup=markup)


@dp.message_handler(lambda message: message.text == 'Инструкции')
async def instruction(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('TA Color 2508ci / 3508ci')
    btn3= types.KeyboardButton('TASKalfa 2553ci')
    btn2 = types.KeyboardButton('Назад')
    markup.row(btn1, btn3)
    markup.row(btn2)

    await message.answer("Выберите модель для получения инструкций:", reply_markup=markup)




@dp.message_handler(lambda message: message.text == 'TA Color 2508ci / 3508ci')
async def send_instruction_video(message: types.Message):
    # Отправляем видео в чат
    video_path = 'videos/video.mp4'  # Замените на путь к вашему видеофайлу
    caption_text = ("В этом уроке мы подробно рассмотрим методы улучшения изображений с низким разрешением пикселей на принтерах Kyocera TASKalfa Color 2508ci / 3508ci."
                    " Вы узнаете эффективные приемы и инструменты для повышения качества изображений, чтобы достичь оптимальных результатов при печати."
                    " Если у вас возникнут вопросы или вам потребуется дополнительная информация, не стесняйтесь обращаться. "
                    "Спасибо за выбор TA Triumph-Adler для вашей печатной техники!")
    with open(video_path, 'rb') as video:
        await bot.send_video(message.chat.id, video, caption=caption_text)

@dp.message_handler(lambda message: message.text == 'TASKalfa 2553ci')
async def send_instruction_video(message: types.Message):
    # Отправляем видео в чат
    video_path = 'videos/video3.mp4'  # Замените на путь к вашему видеофайлу
    caption_text = ("В этом видео вы найдете пошаговую инструкцию по замене цветного тонера на принтере Kyocera TASKalfa."
                    " Следуйте простым шагам, чтобы обеспечить непрерывную и качественную работу вашего устройства. "
                    "Если у вас возникнут вопросы или потребуется дополнительная помощь, не стесняйтесь обращаться к нам."
                    " Спасибо, что выбрали SumnerOne для поддержки ваших печатных нужд!")
    with open(video_path, 'rb') as video:
        await bot.send_video(message.chat.id, video, caption=caption_text)




@dp.message_handler(lambda message: message.text == 'Поддержка')
async def process_support_button(message: types.Message):
    # Создаем клавиатуру для запроса контакта
    contact_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    contact_button = types.KeyboardButton('Отправить контакт', request_contact=True)
    back_button = types.KeyboardButton('Назад')
    contact_markup.row(contact_button)
    contact_markup.row(back_button)

    await message.reply("Для получения поддержки, пожалуйста, отправьте свой контакт ☎️", reply_markup=contact_markup)



@dp.message_handler(content_types=types.ContentTypes.CONTACT)
async def process_contact(message: types.Message):
    # Обрабатываем полученный контакт
    user_id = message.from_user.id
    user_name = f"{message.from_user.first_name} {message.from_user.last_name}"
    phone_number = message.contact.phone_number

    # Сохраняем контакт в базе данных (SQLite)
    save_contact_to_database(user_id, phone_number, user_name)

    # Отправляем подтверждение пользователю
    await message.answer(f"Спасибо за предоставленный контакт, {user_name}! Мы свяжемся с вами в ближайшее время 📲")

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
