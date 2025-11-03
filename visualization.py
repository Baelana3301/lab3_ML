import matplotlib.pyplot as plt
import numpy as np


class SimulationVisualizer:
    def __init__(self):
        self.steps = []
        self.temperatures = []
        self.humidities = []
        self.fan_speeds = []
        self.heater_states = []

        # Настройка графика
        plt.ion()  # Интерактивный режим
        self.fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.suptitle('СИСТЕМА ВЕНТИЛЯЦИИ ПРОМЫШЛЕННОГО ЦЕХА', fontsize=14, fontweight='bold')

    def update(self, step, temperature, humidity, fan_speed, heater_state):
        """Обновление данных для графика"""
        self.steps.append(step)
        self.temperatures.append(temperature)
        self.humidities.append(humidity)
        self.fan_speeds.append(fan_speed)
        self.heater_states.append(heater_state)

        self._plot_all()

    def _plot_all(self):
        """Отрисовка всех графиков"""
        # Очищаем предыдущие графики
        for ax in self.fig.axes:
            ax.clear()

        # НОВЫЕ ГРАНИЦЫ КОМФОРТНОЙ ЗОНЫ
        temp_comfort_min, temp_comfort_max = 17, 23
        hum_comfort_min, hum_comfort_max = 35, 65

        # График температуры
        ax1 = self.fig.axes[0]
        ax1.plot(self.steps, self.temperatures, 'r-o', linewidth=2, markersize=4)
        ax1.set_title('ТЕМПЕРАТУРА В ЦЕХЕ')
        ax1.set_ylabel('Температура (°C)')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=temp_comfort_min, color='blue', linestyle='--', alpha=0.7, label='Комфортная зона')
        ax1.axhline(y=temp_comfort_max, color='blue', linestyle='--', alpha=0.7)
        ax1.legend()

        # График влажности
        ax2 = self.fig.axes[1]
        ax2.plot(self.steps, self.humidities, 'b-o', linewidth=2, markersize=4)
        ax2.set_title('ВЛАЖНОСТЬ В ЦЕХЕ')
        ax2.set_ylabel('Влажность (%)')
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=hum_comfort_min, color='green', linestyle='--', alpha=0.7, label='Комфортная зона')
        ax2.axhline(y=hum_comfort_max, color='green', linestyle='--', alpha=0.7)
        ax2.legend()

        # График скорости вентилятора
        ax3 = self.fig.axes[2]
        ax3.plot(self.steps, self.fan_speeds, 'g-o', linewidth=2, markersize=4)
        ax3.set_title('СКОРОСТЬ ВЕНТИЛЯТОРА')
        ax3.set_ylabel('Скорость (0-1)')
        ax3.set_xlabel('Шаг симуляции')
        ax3.set_ylim(-0.1, 1.1)
        ax3.grid(True, alpha=0.3)

        # График состояния обогревателя
        ax4 = self.fig.axes[3]
        ax4.plot(self.steps, self.heater_states, 'orange', linewidth=2, marker='o', markersize=4)
        ax4.set_title('СОСТОЯНИЕ ОБОГРЕВАТЕЛЯ')
        ax4.set_ylabel('Состояние (0/1)')
        ax4.set_xlabel('Шаг симуляции')
        ax4.set_ylim(-0.1, 1.1)
        ax4.grid(True, alpha=0.3)
        ax4.set_yticks([0, 1])
        ax4.set_yticklabels(['ВЫКЛ', 'ВКЛ'])

        plt.tight_layout()
        plt.draw()
        plt.pause(0.1)

    def show_final(self):
        """Показать финальный график"""
        plt.ioff()
        plt.show()