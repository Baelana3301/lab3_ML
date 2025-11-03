import sqlite3
import numpy as np
from typing import Dict, List, Tuple


class FuzzyInferenceSystem:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.fan_speed_map = {'off': 0, 'slow': 0.33, 'medium': 0.66, 'high': 1.0}
        self.heater_map = {'off': 0, 'on': 1}

    def trapezoid_mf(self, x: float, a: float, b: float, c: float, d: float) -> float:
        """Трапециевидная функция принадлежности"""
        if x <= a or x >= d:
            return 0.0
        elif a < x <= b:
            return (x - a) / (b - a) if b != a else 1.0
        elif b < x <= c:
            return 1.0
        elif c < x < d:
            return (d - x) / (d - c) if d != c else 1.0
        return 0.0

    def fuzzify(self, value: float, variable: str) -> Dict[str, float]:
        """Фаззификация - преобразование четкого значения в нечеткое"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
        SELECT set_name, a, b, c, d FROM fuzzy_sets 
        WHERE variable_name = ?
        ''', (variable,))

        result = {}
        for set_name, a, b, c, d in cursor.fetchall():
            membership = self.trapezoid_mf(value, a, b, c, d)
            result[set_name] = membership

        conn.close()
        return result

    def infer(self, temperature: float, humidity: float) -> Dict[str, float]:
        """Нечеткий вывод - основная функция"""
        # Шаг 1: Фаззификация
        temp_fuzzy = self.fuzzify(temperature, 'temperature')
        hum_fuzzy = self.fuzzify(humidity, 'humidity')

        print(f"Фаззификация: temp={temp_fuzzy}, humidity={hum_fuzzy}")

        # Шаг 2: Получение правил из БД
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rules ORDER BY priority DESC')
        rules = cursor.fetchall()
        conn.close()

        # Шаг 3: Агрегация и активация правил
        fan_output = {}
        heater_output = {}

        for rule in rules:
            _, cond_temp, cond_hum, act_fan, act_heater, priority = rule

            # Вычисляем степень истинности условия
            truth_level = 1.0

            if cond_temp:
                truth_level = min(truth_level, temp_fuzzy.get(cond_temp, 0))
            if cond_hum:
                truth_level = min(truth_level, hum_fuzzy.get(cond_hum, 0))

            if truth_level > 0:
                # Активация заключений
                if act_fan:
                    fan_speed_value = self.fan_speed_map[act_fan]
                    # Метод минимума для активации
                    fan_output[act_fan] = max(fan_output.get(act_fan, 0), truth_level)

                if act_heater:
                    heater_value = self.heater_map[act_heater]
                    heater_output[act_heater] = max(heater_output.get(act_heater, 0), truth_level)

        print(f"Активированные правила: fan={fan_output}, heater={heater_output}")

        # Шаг 4: Дефаззификация (метод центра максимумов)
        fan_result = self.defuzzify_fan(fan_output)
        heater_result = self.defuzzify_heater(heater_output)

        return {
            'fan_speed': fan_result,
            'heater_state': heater_result
        }

    def defuzzify_fan(self, fuzzy_output: Dict[str, float]) -> float:
        """Дефаззификация для скорости вентилятора (метод центра максимумов)"""
        if not fuzzy_output:
            return 0.0

        # Для каждого терма берем его четкое значение и умножаем на степень истинности
        numerator = 0.0
        denominator = 0.0

        for term, membership in fuzzy_output.items():
            crisp_value = self.fan_speed_map[term]
            numerator += crisp_value * membership
            denominator += membership

        return numerator / denominator if denominator != 0 else 0.0

    def defuzzify_heater(self, fuzzy_output: Dict[str, float]) -> float:
        """Дефаззификация для обогревателя"""
        if not fuzzy_output:
            return 0.0

        # Для бинарного выхода используем максимальное значение
        on_value = fuzzy_output.get('on', 0)
        off_value = fuzzy_output.get('off', 0)

        return 1.0 if on_value > off_value else 0.0