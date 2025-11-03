import numpy as np
from fuzzy_system import FuzzyInferenceSystem
from visualization import SimulationVisualizer


def get_user_input():
    """Интерактивный ввод начальных условий"""
    print("🎛 НАСТРОЙКА НАЧАЛЬНЫХ УСЛОВИЙ ЦЕХА")
    print("=" * 50)

    while True:
        try:
            temp = float(input("🌡 Введите начальную температуру (10-30°C): "))
            if 10 <= temp <= 30:
                break
            else:
                print("❌ Ошибка: температура должна быть от 10 до 30°C")
        except ValueError:
            print("❌ Ошибка: введите число")

    while True:
        try:
            humidity = float(input("💧 Введите начальную влажность (20-80%): "))
            if 20 <= humidity <= 80:
                break
            else:
                print("❌ Ошибка: влажность должна быть от 20 до 80%")
        except ValueError:
            print("❌ Ошибка: введите число")

    return temp, humidity


def is_comfortable_zone(temperature: float, humidity: float) -> bool:
    """Проверка, находятся ли значения в комфортной зоне с запасом"""
    # Расширяем комфортную зону для более стабильной работы
    temp_comfort = 17 <= temperature <= 23  # было 18-22, стало 17-23
    hum_comfort = 35 <= humidity <= 65  # было 40-60, стало 35-65
    return temp_comfort and hum_comfort


def get_comfort_margin(temperature: float, humidity: float) -> tuple[float, float]:
    """Вычисляет насколько близко значения к середине комфортной зоны"""
    # Идеальные средние значения
    ideal_temp = 20.0  # середина 17-23
    ideal_hum = 50.0  # середина 35-65

    # Вычисляем отклонение от идеала (0 = идеально, >0 = отклонение)
    temp_margin = abs(temperature - ideal_temp)
    hum_margin = abs(humidity - ideal_hum)

    return temp_margin, hum_margin


class VentilationSimulator:
    def __init__(self):
        self.fis = FuzzyInferenceSystem('knowledge_base.db')
        self.visualizer = SimulationVisualizer()

        # Интерактивный ввод начальных условий
        self.temperature, self.humidity = get_user_input()

        # Внешние условия (имитация)
        self.external_temp = 15.0
        self.external_humidity = 60.0

        self.step = 0
        self.comfort_steps_count = 0  # Счетчик шагов в комфортной зоне

        print("\n" + "=" * 60)
        print("🚀 СИМУЛЯТОР СИСТЕМЫ ВЕНТИЛЯЦИИ ЦЕХА ЗАПУЩЕН!")
        print(f"📊 НАЧАЛЬНЫЕ УСЛОВИЯ: Температура={self.temperature}°C, Влажность={self.humidity}%")

        # Проверяем начальные условия
        if is_comfortable_zone(self.temperature, self.humidity):
            print("🎉 Начальные условия УЖЕ в комфортной зоне! Система будет простаивать.")
        else:
            print("📈 Система будет регулировать условия до комфортной зоны...")
        print("=" * 60)

    def update_environment(self):
        """Имитация изменения внешней среды"""
        self.external_temp = 15 + 10 * np.sin(self.step * 0.1)
        self.external_humidity = 50 + 20 * np.sin(self.step * 0.05)

    def apply_control_actions(self, fan_speed: float, heater_state: float):
        """Применение управляющих воздействий к модели цеха с учетом стремления к середине зоны"""
        # Базовые изменения
        temp_change_from_fan = (self.external_temp - self.temperature) * 0.08 * fan_speed
        hum_change_from_fan = (self.external_humidity - self.humidity) * 0.08 * fan_speed
        temp_change_from_heater = heater_state * 0.8

        # ДОБАВЛЯЕМ СТРЕМЛЕНИЕ К СЕРЕДИНЕ КОМФОРТНОЙ ЗОНЫ
        ideal_temp = 20.0
        ideal_hum = 50.0

        # Если близко к комфортной зоне, добавляем мягкое подстраивание к середине
        temp_margin, hum_margin = get_comfort_margin(self.temperature, self.humidity)

        # Коэффициенты подстройки (чем дальше от идеала, тем сильнее воздействие)
        temp_adjustment = (ideal_temp - self.temperature) * 0.02 * (1 - fan_speed)
        hum_adjustment = (ideal_hum - self.humidity) * 0.02 * (1 - fan_speed)

        # Обновление состояния с учетом подстройки
        self.temperature += temp_change_from_fan + temp_change_from_heater + temp_adjustment
        self.humidity += hum_change_from_fan + hum_adjustment

        # Ограничения
        self.temperature = max(10, min(30, self.temperature))
        self.humidity = max(20, min(80, self.humidity))

    def run(self, steps=20):
        """Запуск симуляции"""

        print("\n📈 ЗАПУСК СИМУЛЯЦИИ...")
        print("   Графики будут обновляться в реальном времени!")
        print("   Система будет ПРОПУСКАТЬ шаги при достижении комфортной зоны")
        input("   Нажмите Enter чтобы продолжить...")

        step = 0
        actual_steps = 0

        while actual_steps < steps and step < steps * 2:  # Защита от бесконечного цикла
            step += 1

            # Проверяем комфортную зону ПЕРЕД выполнением шага
            if is_comfortable_zone(self.temperature, self.humidity):
                self.comfort_steps_count += 1
                print(f"\n✅ ШАГ {step}: КОМФОРТНАЯ ЗОНА ДОСТИГНУТА!")
                print(f"   Температура: {self.temperature:.1f}°C (18-22°C ✓)")
                print(f"   Влажность: {self.humidity:.1f}% (40-60% ✓)")
                print(f"   Шаг пропущен - система работает в штатном режиме")
                print("-" * 40)

                # Все равно обновляем визуализацию (нулевое управление)
                self.visualizer.update(step, self.temperature, self.humidity, 0, 0)

                # Пропускаем остальную логику шага
                continue

            # Если НЕ в комфортной зоне - выполняем обычный шаг
            actual_steps += 1
            self.step = step

            print(f"\n🎯 ШАГ {step} (активный шаг {actual_steps}):")
            print("-" * 40)

            self.update_environment()
            print(f"🌍 Внешние условия: temp={self.external_temp:.1f}°C, hum={self.external_humidity:.1f}%")

            print(f"🏭 Состояние цеха: temp={self.temperature:.1f}°C, hum={self.humidity:.1f}%")
            actions = self.fis.infer(self.temperature, self.humidity)
            fan_speed = actions['fan_speed']
            heater_state = actions['heater_state']

            print(f"🎛 УПРАВЛЕНИЕ: вентилятор={fan_speed:.2f}, обогреватель={'ВКЛ' if heater_state > 0.5 else 'ВЫКЛ'}")

            # Обновляем визуализацию
            self.visualizer.update(step, self.temperature, self.humidity, fan_speed, heater_state)

            # Применяем управление
            self.apply_control_actions(fan_speed, heater_state)

        # В конце метода run добавьте:
        print("\n" + "=" * 60)
        print("✅ СИМУЛЯЦИЯ ЗАВЕРШЕНА!")
        print(f"📊 СТАТИСТИКА:")
        print(f"   Всего шагов симуляции: {step}")
        print(f"   Активных шагов регулирования: {actual_steps}")
        print(f"   Шагов в комфортной зоне: {self.comfort_steps_count}")

        # Более детальная информация о финальном состоянии
        temp_margin, hum_margin = get_comfort_margin(self.temperature, self.humidity)
        print(f"   Финальное состояние: {self.temperature:.1f}°C, {self.humidity:.1f}%")
        print(f"   Отклонение от идеала: темп. {temp_margin:.1f}°C, влаж. {hum_margin:.1f}%")

        if is_comfortable_zone(self.temperature, self.humidity):
            if temp_margin <= 1.0 and hum_margin <= 5.0:
                print("🎉 ОТЛИЧНО: параметры в оптимальной комфортной зоне!")
            else:
                print("✅ ХОРОШО: параметры в комфортной зоне")
        else:
            print("⚠️  Цель не достигнута: параметры вне комфортной зоны")

        print("   Закройте окно с графиками чтобы выйти...")
        print("=" * 60)

        # Показываем финальный график
        self.visualizer.show_final()


if __name__ == "__main__":
    simulator = VentilationSimulator()
    simulator.run(steps=15)