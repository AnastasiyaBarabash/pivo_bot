import sqlite3
from datetime import datetime

DRINKS_SEED = [
    ('ОТВЕРТКА', 'Водка, Апельсиновый сок', 'M', 'Сладкий', 'Лёгкий'),
    ('БЕЛЫЙ РУССКИЙ', 'Водка, Кофейный ликёр, Сливки', 'S', 'Сладкий', 'Средний'),
    ('ЧЁРНЫЙ РУССКИЙ', 'Водка, Кофейный ликёр', 'S', 'Сладкий', 'Лёгкий'),
    ('КРОВАВАЯ МЭРИ', 'Водка, Сок томатный, Сок лимонный, Ворчестершир, Табаско, Соль, Перец', 'M', 'Кислый', 'Лёгкий'),
    ('КОСМОПОЛИТАН', 'Водка, Ликер Куантро, Сок лайма, Сок лимона, Клюквенный сок', 'S', 'Сладкий', 'Лёгкий'),
    ('СЕКС НА ПЛЯЖЕ', 'Водка, Персиковый сок, Апельсиновый сок, Клюквенный сок', 'M', 'Сладкий', 'Лёгкий'),
    ('ЭСПРЕССО МАРТИНИ', 'Водка, Сироп сахарный, Ликер кофейный, Кофе', 'S', 'Сладкий', 'Лёгкий'),
    ('КАМИКАДЗЕ', 'Водка, Triple Sec, Сок лайма', 'S', 'Кислый', 'Средний'),
    ('БАКАРДИ КОКТЕЙЛЬ', 'Светлый ром; Лимонный сок; Сироп Гренадин', 'S', 'Кислый', 'Лёгкий'),
    ('ДАЙКИРИ', 'Светлый ром, Сок лайма, Сахарный сироп', 'S', 'Кислый', 'Лёгкий'),
    ('КУБА-ЛИБРЕ', 'Светлый ром, Кока кола, Сок лайма', 'M', 'Сладкий', 'Лёгкий'),
    ('ПИНА КОЛАДА', 'Ром белый, Cироп кокосовый, Ананасовый сок', 'M', 'Сладкий', 'Средний'),
    ('МОХИТО', 'Ром белый, Мята, Сок лайма, Cахарный сироп, Содовая до верху', 'L', 'Сладкий', 'Лёгкий'),
    ('МАРГАРИТА', 'Текила серебряная, Ликер Куантро, Сок лайма', 'S', 'Кислый', 'Средний'),
    ('ТЕКИЛА САНРАЙЗ', 'Текила серебряная, Апельсиновый сок, Сироп Гренадин', 'M', 'Сладкий', 'Лёгкий'),
    ('КЛУБНИЧНАЯ МАРГАРИТА', 'Текила серебряная, Куантро, Лаймовый сок, Сироп Клубника, Клубничное пюре', 'M', 'Сладкий', 'Лёгкий'),
    ('КЛЕВЕР КЛУБ', 'Джин, Малиновый сироп, Лимонный сок, Белок яйца', 'S', 'Сладкий', 'Лёгкий'),
    ('СУХОЙ МАРТИНИ', 'Джин, Сухой вермут', 'S', 'Горький', 'Крепкий'),
    ('ДЖИН ФИЗ', 'Джин, Лимонный сок, Сахарный сироп; Содовая', 'L', 'Кислый', 'Лёгкий'),
    ('ДЖОН КОЛЛИНЗ', 'Джин, Лимонный сок, Сахарный сироп, Содовая, Биттер Ангостура', 'M', 'Кислый', 'Лёгкий'),
    ('БЕЛАЯ ЛЕДИ', 'Джин, Ликер Куантро, Лимонный сок', 'S', 'Кислый', 'Лёгкий'),
    ('ФРАНЦУЗСКИЙ 75', 'Джин, Сок лимонный, Сироп сахарный, Шампанское', 'S', 'Сладкий', 'Средний'),
    ('МЕЖДУ ПРОСТЫНЯМИ', 'Светлый ром, Коньяк, Ликер Куантро, Лимонный сок', 'S', 'Кислый', 'Крепкий'),
    ('МОТОЦИКЛЕТНАЯ КОЛЯСКА', 'Коньяк, Ликер Куантро, Лаймовый сок', 'S', 'Кислый', 'Крепкий'),
    ('МАНХЭТТЕН', 'Ржаной виски или бурбон, Красный вермут, Биттер Ангостура', 'S', 'Сладкий', 'Крепкий'),
    ('ОЛД ФЕШЕН', 'Виски, 1 кубик сахара, Биттер Ангостура, Немного содовой', 'S', 'Горький', 'Крепкий'),
    ('ВИСКИ САУЭР', 'Бурбон, Сироп сахарный, Лимонный сок, Яичный белок', 'M', 'Кислый', 'Средний'),
    ('РОБ РОЙ', 'Виски, Красный вермут, Биттер Ангостура', 'S', 'Горький', 'Крепкий'),
    ('ЛОНГ АЙЛЕНД АЙС ТИ', 'Водка, Джин, Текила серебряная, Ром белый, Ликер Куантро, Лимонный сок, Сахарный сироп, Кока-Кола', 'L', 'Сладкий', 'Крепкий'),
    ('ХИРОСИМА', 'Ликер Самбука, Ликер Бейлиз, Абсент', 'S', 'Сладкий', 'Крепкий'),
    ('АПЕРОЛЬ СМПРИТЦ', 'Вино игристое, Биттер Апероль, Содовая', 'M', 'Горький', 'Средний'),
    ('БЕЛИНИ', 'Вино игристое, Персиковый сок', 'M', 'Сладкий', 'Средний'),
    ('ИТАЛЬЯНСКОЕ НАСЛАЖДЕНИЕ', 'Амаретто, Апельстновый сок, Сливки', 'M', 'Сладкий', 'Лёгкий'),
    ('ВОДКА', 'ВОДКА', 'ШОТ', 'Чистый', 'Крепкий'),
    ('ВОДКА С ГРЕНАДИНОМ', 'Водка, Гренадин', 'ШОТ', 'Сладкий', 'Крепкий'),
    ('ХИРОСИМА ШОТ', 'Абсент, Бейлис, Гренадин', 'ШОТ', 'Сладкий', 'Сверх крекий'),
    ('JAGERMEISTER', 'Jagermeister', 'ШОТ', 'Сладкий', 'Крепкий'),
    ('Б-52', 'Кофейный, сливочный и апельсиновый ликёры', 'ШОТ', 'Сладкий', 'Крепкий'),
    ('ТЕКИЛА', 'Текила', 'ШОТ', 'Чистый', 'Крепкий'),
    ('КОКТЕЙЛЬ НОМЕР 38', 'Блю Кюрасао, Ананасовый сок, Сок лимона, Ежевика, Содовая', 'L', 'Сладкий', 'Б/А'),
    ('МАЛИНОВЫЙ', 'Малина, Апельсиновый сок, Сок лимона, Тоник', 'L', 'Сладкий', 'Б/А'),
    ('КЛЮКОВКА', 'Ежевика, Сок лайма, Клюквенный сок, Тоник', 'M', 'Сладкий', 'Б/А'),
    ('БЛЕК', 'Блю Кюрасао, Апельсин, Лимон, Клюквенный сок, Содовая', 'M', 'Сладкий', 'Б/А'),
    ('БОКАЛ БЕЛОГО ВИНА', 'Вино, а что ты здесь хотел увидеть?', 'M', 'Чистый', 'Средний'),
    ('БОКАЛ КРАСНОГО ВИНА', 'Вино, а что ты здесь хотел увидеть?', 'M', 'Чистый', 'Средний'),
    ('БОКАЛ ШАМПАНСКОГО', 'Шампанское, а что ты здесь хотел увидеть?', 'M', 'Чистый', 'Средний'),
    ('ESSA', 'Ананас, грейпфрут', 'M', 'Чистый', 'Средний'),
]


def init_db():
    with sqlite3.connect('party_hard.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS drinks (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            components TEXT,
                            size TEXT,
                            taste TEXT,
                            strength TEXT
                        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            username TEXT NOT NULL UNIQUE
                        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            drink_id INTEGER,
                            created_at DATETIME,
                            status TEXT,
                            FOREIGN KEY(user_id) REFERENCES users(id),
                            FOREIGN KEY(drink_id) REFERENCES drinks(id)
                        )''')

        # Заполняем меню только если оно пустое
        cursor.execute('SELECT COUNT(*) FROM drinks')
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                'INSERT INTO drinks (name, components, size, taste, strength) VALUES (?, ?, ?, ?, ?)',
                DRINKS_SEED
            )

        conn.commit()


def get_drinks():
    with sqlite3.connect('party_hard.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM drinks')
        drinks = cursor.fetchall()
    return [{"id": row[0], "name": row[1], "components": row[2],
             "size": row[3], "taste": row[4], "strength": row[5]} for row in drinks]


def get_user_by_id(user_id):
    with sqlite3.connect('party_hard.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
    return {"id": user[0], "username": user[1]} if user else None


def get_drink_by_id(drink_id):
    with sqlite3.connect('party_hard.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM drinks WHERE id = ?', (drink_id,))
        drink = cursor.fetchone()
    if drink:
        return {"drink_id": drink[0], "drink_name": drink[1], "components": drink[2],
                "size": drink[3], "taste": drink[4], "strength": drink[5]}
    return None


def is_order_by_id(order_id):
    with sqlite3.connect('party_hard.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
            order = cursor.fetchone()
            return {"order_id": order[0]} if order else None
        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")
            return None


def add_user(user_id, username):
    with sqlite3.connect('party_hard.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (id, username) VALUES (?, ?)', (user_id, username))
            conn.commit()
            return {"status": "User added"}
        except sqlite3.IntegrityError:
            return {"status": "User already exists"}


def create_order(user_id, drink_id, created_at):
    with sqlite3.connect('party_hard.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO orders (user_id, drink_id, created_at, status) VALUES (?, ?, ?, ?)',
            (user_id, drink_id, created_at, 'ожидает'))
        conn.commit()
        return cursor.lastrowid


def get_all_orders():
    with sqlite3.connect('party_hard.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT orders.id, users.username, drinks.name AS drink_name, orders.created_at, orders.status
            FROM orders
            JOIN users ON orders.user_id = users.id
            JOIN drinks ON orders.drink_id = drinks.id
        ''')
        rows = cursor.fetchall()
        return [{"id": row[0], "username": row[1], "drink_name": row[2],
                 "created_at": row[3], "status": row[4]} for row in rows]


def update_order_status_in_db(order_id, new_status):
    try:
        with sqlite3.connect('party_hard.db') as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
            if cursor.rowcount == 0:
                return None
            conn.commit()
            cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
            updated_order = cursor.fetchone()
            return {"id": updated_order[0], "user_id": updated_order[1],
                    "drink_id": updated_order[2], "created_at": updated_order[3],
                    "status": updated_order[4]}
    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        return None


def filter_drinks(filters: dict) -> list:
    try:
        with sqlite3.connect('party_hard.db') as conn:
            cursor = conn.cursor()
            conditions = []
            values = []
            for key, value in filters.items():
                if value != 'Далее':
                    conditions.append(f"{key} = ?")
                    values.append(value)
            query = "SELECT id, name, components FROM drinks WHERE " + \
                    (" AND ".join(conditions) if conditions else "1")
            cursor.execute(query, values)
            cocktails = cursor.fetchall()
        return [{"id": c[0], "name": c[1], "components": c[2]} for c in cocktails]
    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        return []