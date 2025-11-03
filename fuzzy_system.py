import sqlite3
import numpy as np
from typing import Dict, List, Tuple


class FuzzyInferenceSystem:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.fan_speed_map = {'off': 0, 'slow': 0.33, 'medium': 0.66, 'high': 1.0}
        self.heater_map = {'off': 0, 'on': 1}

    def trapezoid_mf(self, x: float, a: float, b: float, c: float, d: float) -> float:
        """ИСПРАВЛЕННАЯ трапециевидная функция принадлежности"""
        if x < a:
            return 0.0
        elif a <= x < b:
            if b == a:
                return 1.0
            return (x - a) / (b - a)
        elif b <= x <= c:
            return 1.0
        elif c < x <= d:
            if d == c:
                return 1.0
            return (d - x) / (d - c)
        else:
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
            if membership > 0:  # Показываем только ненулевые значения
                result[set_name] = membership

        conn.close()
        return result

    def infer(self, temperature: float, humidity: float) -> Dict[str, float]:
        """Нечеткий вывод - основная функция"""
        # Шаг 1: Фаззификация
        temp_fuzzy = self.fuzzify(temperature, 'temperature')
        hum_fuzzy = self.fuzzify(humidity, 'humidity')

        print("🎯 ФАЗЗИФИКАЦИЯ:")
        print(f"   Температура {temperature}°C → {temp_fuzzy}")
        print(f"   Влажность {humidity}% → {hum_fuzzy}")

        # Шаг 2: Получение правил из БД
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rules ORDER BY priority DESC')
        rules = cursor.fetchall()
        conn.close()

        # Шаг 3: Агрегация и активация правил
        fan_output = {}
        heater_output = {}

        print("\n📋 ПРОВЕРКА ПРАВИЛ:")

        for rule in rules:
            rule_id, cond_temp, cond_hum, act_fan, act_heater, priority = rule

            # Формируем читаемое условие
            condition_parts = []
            if cond_temp:
                condition_parts.append(f"temp={cond_temp}")
            if cond_hum:
                condition_parts.append(f"hum={cond_hum}")
            condition_str = " И ".join(condition_parts) if condition_parts else "ВСЕГДА"

            # Формируем читаемое действие
            action_parts = []
            if act_fan:
                action_parts.append(f"вентилятор={act_fan}")
            if act_heater:
                action_parts.append(f"обогреватель={act_heater}")
            action_str = ", ".join(action_parts)

            # Вычисляем степень истинности условия
            truth_level = 1.0

            if cond_temp:
                temp_truth = temp_fuzzy.get(cond_temp, 0)
                truth_level = min(truth_level, temp_truth)
            if cond_hum:
                hum_truth = hum_fuzzy.get(cond_hum, 0)
                truth_level = min(truth_level, hum_truth)

            # Красивый вывод правила
            status = "✅ СРАБОТАЛО" if truth_level > 0 else "❌ НЕ СРАБОТАЛО"
            print(f"   Правило {rule_id}: ЕСЛИ {condition_str} ТО {action_str}")
            print(f"        Приоритет: {priority}, Истинность: {truth_level:.2f} → {status}")

            if truth_level > 0:
                # Активация заключений
                if act_fan:
                    current_value = fan_output.get(act_fan, 0)
                    fan_output[act_fan] = max(current_value, truth_level)

                if act_heater:
                    current_value = heater_output.get(act_heater, 0)
                    heater_output[act_heater] = max(current_value, truth_level)

        print(f"\n🎛 АКТИВИРОВАННЫЕ ДЕЙСТВИЯ:")
        print(f"   Вентилятор: {fan_output}")
        print(f"   Обогреватель: {heater_output}")

        # Шаг 4: Дефаззификация
        fan_result = self.defuzzify_fan(fan_output)
        heater_result = self.defuzzify_heater(heater_output)

        return {
            'fan_speed': fan_result,
            'heater_state': heater_result
        }

    def defuzzify_fan(self, fuzzy_output: Dict[str, float]) -> float:
        """Дефаззификация для скорости вентилятора"""
        if not fuzzy_output:
            print("   Вентилятор: нет активированных правил → ВЫКЛ")
            return 0.0

        numerator = 0.0
        denominator = 0.0

        for term, membership in fuzzy_output.items():
            # ПРЕОБРАЗУЕМ numpy типы в обычные float
            membership_val = float(membership)
            crisp_value = self.fan_speed_map[term]
            numerator += crisp_value * membership_val
            denominator += membership_val

        result = numerator / denominator if denominator != 0 else 0.0
        print(f"   Вентилятор: {fuzzy_output} → скорость {result:.2f}")
        return result

    def defuzzify_heater(self, fuzzy_output: Dict[str, float]) -> float:
        """Дефаззификация для обогревателя"""
        if not fuzzy_output:
            print("   Обогреватель: нет активированных правил → ВЫКЛ")
            return 0.0

        on_value = fuzzy_output.get('on', 0)
        off_value = fuzzy_output.get('off', 0)

        result = 1.0 if on_value > off_value else 0.0
        status = "ВКЛ" if result > 0.5 else "ВЫКЛ"
        print(f"   Обогреватель: {fuzzy_output} → {status}")
        return result