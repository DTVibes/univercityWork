import sqlite3git remote add origin https://github.com/DTVibes/univercityWork.git
def save_contact_to_database(user_id, phone_number, user_name):
    conn = sqlite3.connect('contacts2.db')  # Создаем или подключаемся к базе данных SQLite
    cursor = conn.cursor()

    # Создаем таблицу, если она еще не существует
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            user_id INTEGER PRIMARY KEY,
            phone_number TEXT,
            user_name TEXT
        )
    ''')

    try:
        # Пробуем вставить новую запись
        cursor.execute('''
            INSERT INTO contacts (user_id, phone_number, user_name)
            VALUES (?, ?, ?)
        ''', (user_id, phone_number, user_name))
    except sqlite3.IntegrityError:
        # Если запись существует, обновляем ее
        cursor.execute('''
            UPDATE contacts
            SET phone_number = ?, user_name = ?
            WHERE user_id = ?
        ''', (phone_number, user_name, user_id))

    # Сохраняем изменения
    conn.commit()

    # Закрываем соединение
    conn.close()
