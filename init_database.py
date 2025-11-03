import sqlite3


def init_database():
    conn = sqlite3.connect('knowledge_base.db')
    cursor = conn.cursor()

    # Таблица с нечеткими множествами
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fuzzy_sets (
        id INTEGER PRIMARY KEY,
        variable_name TEXT NOT NULL,
        set_name TEXT NOT NULL,
        a REAL, b REAL, c REAL, d REAL
    )
    ''')

    # Таблица правил
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rules (
        id INTEGER PRIMARY KEY,
        condition_temp TEXT,
        condition_humidity TEXT,
        action_fan_speed TEXT,
        action_heater_state TEXT,
        priority INTEGER
    )
    ''')

    # Очищаем таблицы
    cursor.execute("DELETE FROM fuzzy_sets")
    cursor.execute("DELETE FROM rules")

    # Обновите параметры нечетких множеств:
    temp_sets = [
        ('temperature', 'cold', 10, 10, 15, 17),  # было 10,10,16,18
        ('temperature', 'comfortable', 15, 17, 23, 25),  # было 16,18,22,24
        ('temperature', 'hot', 23, 25, 30, 30)  # было 22,24,30,30
    ]

    humidity_sets = [
        ('humidity', 'low', 0, 0, 30, 35),  # было 0,0,30,40
        ('humidity', 'normal', 30, 35, 65, 70),  # было 30,40,60,70
        ('humidity', 'high', 65, 70, 100, 100)  # было 60,70,100,100
    ]

    cursor.executemany('INSERT INTO fuzzy_sets VALUES (NULL, ?, ?, ?, ?, ?, ?)',
                       temp_sets + humidity_sets)

    # В разделе с правилами добавьте:
    rules = [
        # temp, humidity, fan_speed, heater_state, priority
        ('cold', None, 'slow', 'on', 10),
        ('hot', None, 'high', 'off', 10),
        ('comfortable', 'normal', 'off', 'off', 5),
        (None, 'high', 'medium', 'off', 8),
        ('cold', 'high', 'medium', 'on', 9),
        (None, 'low', 'medium', 'off', 7),
        ('comfortable', 'low', 'slow', 'off', 6),
        ('comfortable', 'high', 'medium', 'off', 6),
        # ДОБАВЬТЕ ЭТИ ПРАВИЛА ДЛЯ БОЛЕЕ ТОЧНОЙ РЕГУЛИРОВКИ:
        (None, 'normal', 'slow', 'off', 4),  # Мягкая вентиляция при нормальной влажности
        ('comfortable', None, 'off', 'off', 3),  # Выключение при комфортной температуре
    ]

    cursor.executemany('''
    INSERT INTO rules VALUES (NULL, ?, ?, ?, ?, ?)
    ''', rules)

    conn.commit()
    conn.close()
    print("База данных инициализирована!")


if __name__ == "__main__":
    init_database()