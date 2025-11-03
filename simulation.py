import numpy as np
from fuzzy_system import FuzzyInferenceSystem


class VentilationSimulator:
    def __init__(self):
        self.fis = FuzzyInferenceSystem('knowledge_base.db')

        # Начальное состояние цеха
        self.temperature = 20.0
        self.humidity = 50.0

        # Внешние условия (имитация)
        self.external_temp = 15.0
        self.external_humidity = 60.0

        print("Симулятор системы вентиляции цеха запущен!")
        print("Начальные условия:")
        print(f"  Температура: {self.temperature}°C")
        print(f"  Влажность: {self.humidity}%")
        print("-" * 50)

    def update_environment(self):
        """Имитация изменения внешней среды"""
        # Простое циклическое изменение
        self.external_temp = 15 + 10 * np.sin(self.step * 0.1)
        self.external_humidity = 50 + 20 * np.sin(self.step * 0.05)

    def apply_control_actions(self, fan_speed: float, heater_state: float):
        """Применение управляющих воздействий к модели цеха"""
        # Влияние вентилятора на температуру
        temp_change_from_fan = (self.external_temp - self.temperature) * 0.02 * fan_speed
        # Влияние вентилятора на влажность
        hum_change_from_fan = (self.external_humidity - self.humidity) * 0.02 * fan_speed
        # Влияние обогревателя
        temp_change_from_heater = heater_state * 0.8

        # Обновление состояния
        self.temperature += temp_change_from_fan + temp_change_from_heater
        self.humidity += hum_change_from_fan

        # Ограничения
        self.temperature = max(10, min(30, self.temperature))
        self.humidity = max(20, min(80, self.humidity))

    def run(self, steps=50):
        """Запуск симуляции"""
        self.step = 0

        for step in range(steps):
            self.step = step
            print(f"\nШаг {step + 1}:")

            # Обновляем внешнюю среду
            self.update_environment()
            print(f"Внешние условия: temp={self.external_temp:.1f}°C, hum={self.external_humidity:.1f}%")

            # Получаем управляющие воздействия от нечеткой системы
            actions = self.fis.infer(self.temperature, self.humidity)
            fan_speed = actions['fan_speed']
            heater_state = actions['heater_state']

            print(f"Состояние цеха: temp={self.temperature:.1f}°C, hum={self.humidity:.1f}%")
            print(f"Управление: вентилятор={fan_speed:.2f}, обогреватель={'ВКЛ' if heater_state > 0.5 else 'ВЫКЛ'}")

            # Применяем управление
            self.apply_control_actions(fan_speed, heater_state)

            print("-" * 50)


if __name__ == "__main__":
    # Запуск симуляции
    simulator = VentilationSimulator()
    simulator.run(steps=20)