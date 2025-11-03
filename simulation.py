import numpy as np
from fuzzy_system import FuzzyInferenceSystem


class VentilationSimulator:
    def __init__(self):
        self.fis = FuzzyInferenceSystem('knowledge_base.db')

        # НАСТРОЙКА НАЧАЛЬНЫХ УСЛОВИЙ ДЛЯ ДЕМОНСТРАЦИИ:
        self.temperature = 26.0  # Примеры: 15 (холодно), 20 (комфортно), 26 (жарко)
        self.humidity = 70.0  # Примы: 30 (низкая), 50 (норма), 75 (высокая)

        # Внешние условия (имитация)
        self.external_temp = 15.0
        self.external_humidity = 60.0

        self.step = 0

        print("=" * 60)
        print("Симулятор системы вентиляции цеха запущен!")
        print(f"НАЧАЛЬНЫЕ УСЛОВИЯ: Температура={self.temperature}°C, Влажность={self.humidity}%")
        print("=" * 60)

    def update_environment(self):
        """Имитация изменения внешней среды"""
        # Простое циклическое изменение
        self.external_temp = 15 + 10 * np.sin(self.step * 0.1)
        self.external_humidity = 50 + 20 * np.sin(self.step * 0.05)

    def apply_control_actions(self, fan_speed: float, heater_state: float):
        """Применение управляющих воздействий к модели цеха"""
        # Влияние вентилятора на температуру
        temp_change_from_fan = (self.external_temp - self.temperature) * 0.05 * fan_speed
        # Влияние вентилятора на влажность
        hum_change_from_fan = (self.external_humidity - self.humidity) * 0.05 * fan_speed
        # Влияние обогревателя
        temp_change_from_heater = heater_state * 0.5

        # Обновление состояния
        self.temperature += temp_change_from_fan + temp_change_from_heater
        self.humidity += hum_change_from_fan

        # Ограничения
        self.temperature = max(10, min(30, self.temperature))
        self.humidity = max(20, min(80, self.humidity))

    def run(self, steps=10):  # Уменьшил до 10 шагов для наглядности
        """Запуск симуляции"""

        for step in range(steps):
            self.step = step
            print(f"\n🎯 ШАГ {step + 1}:")
            print("-" * 40)

            # Обновляем внешнюю среду
            self.update_environment()
            print(f"🌡 Внешние условия: temp={self.external_temp:.1f}°C, hum={self.external_humidity:.1f}%")

            # Получаем управляющие воздействия от нечеткой системы
            print(f"📊 Состояние цеха: temp={self.temperature:.1f}°C, hum={self.humidity:.1f}%")
            actions = self.fis.infer(self.temperature, self.humidity)
            fan_speed = actions['fan_speed']
            heater_state = actions['heater_state']

            print(f"🎛 УПРАВЛЕНИЕ: вентилятор={fan_speed:.2f}, обогреватель={'ВКЛ' if heater_state > 0.5 else 'ВЫКЛ'}")

            # Применяем управление
            self.apply_control_actions(fan_speed, heater_state)


if __name__ == "__main__":
    # Запуск симуляции
    simulator = VentilationSimulator()
    simulator.run(steps=10)