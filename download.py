import base64
import sqlite3

# Подключение к базе данных SQLite
conn = sqlite3.connect('new.db')
c = conn.cursor()

# Считывание изображения из файла
with open('pictures/file.jpg', 'rb') as f:
    image_data = f.read()

# Кодирование изображения в base64
encoded_image = base64.b64encode(image_data).decode('utf-8')

# Определение id записи, в которую хотим вставить изображение
id = 4

# Вставка изображения в таблицу Steps для строки с определенным id
c.execute("UPDATE Steps SET picture = ? WHERE id = ?", (encoded_image, id))

# Сохранение изменений и закрытие базы данных
conn.commit()
conn.close()
