"""
Модуль визуализации для Telegram-бота HPI
"""
import io
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import Dict, Optional, cast
import logging
from matplotlib.projections.polar import PolarAxes


class HPIVisualizer:
    """Визуализатор для создания диаграмм HPI."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Настройка стиля
        plt.style.use('default')
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['font.size'] = 10
        
        # Цвета для сфер
        self.sphere_colors = {
            "1": "#FF6B6B",  # Красный - любовь
            "2": "#4ECDC4",  # Бирюзовый - семья
            "3": "#45B7D1",  # Синий - друзья
            "4": "#96CEB4",  # Зеленый - карьера
            "5": "#FFEAA7",  # Желтый - здоровье
            "6": "#DDA0DD",  # Фиолетовый - ментальное здоровье
            "7": "#FFB347",  # Оранжевый - хобби
            "8": "#98D8C8"   # Мятный - благосостояние
        }
        
        # Названия сфер
        self.sphere_names = {
            "1": "Любовь",
            "2": "Семья", 
            "3": "Друзья",
            "4": "Карьера",
            "5": "Здоровье",
            "6": "Ментал",
            "7": "Хобби",
            "8": "Финансы"
        }
    
    def create_radar_chart(self, scores: Dict[str, float]) -> Optional[io.BytesIO]:
        """Создает радарную диаграмму баланса по сферам."""
        try:
            # Подготавливаем данные
            categories = list(self.sphere_names.values())
            values = [scores.get(str(i), 1.0) for i in range(1, 9)]
            
            # Количество категорий
            N = len(categories)
            
            # Углы для каждой категории
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]  # Замыкаем круг
            
            # Значения
            values += values[:1]
            
            # Создаем фигуру
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
            
            # Рисуем сетку (углы)
            polar_ax = cast(PolarAxes, ax)
            polar_ax.set_theta_offset(float(np.pi) / 2.0)
            polar_ax.set_theta_direction(-1)
            
            # Добавляем метки категорий
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=12, fontweight='bold')
            
            # Настраиваем сетку
            ax.set_ylim(0, 10)
            ax.set_yticks([2, 4, 6, 8, 10])
            ax.set_yticklabels(['2', '4', '6', '8', '10'], fontsize=10)
            ax.grid(True, alpha=0.3)
            
            # Рисуем основную линию
            ax.plot(angles, values, 'o-', linewidth=2, color='#2E86AB', markersize=8)
            ax.fill(angles, values, alpha=0.25, color='#2E86AB')
            
            # Добавляем точки для каждой сферы
            for i, (angle, value) in enumerate(zip(angles[:-1], values[:-1])):
                color = list(self.sphere_colors.values())[i]
                ax.scatter(angle, value, s=100, c=color, zorder=5, edgecolors='white', linewidth=2)
            
            # Заголовок
            plt.title('Баланс по сферам жизни', fontsize=16, fontweight='bold', pad=20)
            
            # Сохраняем в буфер
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
            buf.seek(0)
            plt.close()
            
            return buf
            
        except Exception as e:
            self.logger.error(f"Ошибка создания радарной диаграммы: {e}")
            return None
    
    def create_trend_chart(self, scores: Dict[str, float], hpi_total: float) -> Optional[io.BytesIO]:
        """Создает график тренда HPI."""
        try:
            # Создаем фигуру
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            # Верхний график - HPI общий
            ax1.bar(['HPI'], [hpi_total], color=self._get_hpi_color(hpi_total), alpha=0.7, edgecolor='black', linewidth=2)
            ax1.set_ylim(0, 100)
            ax1.set_ylabel('HPI Score', fontsize=12, fontweight='bold')
            ax1.set_title(f'Human Performance Index: {hpi_total:.1f}', fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3, axis='y')
            
            # Добавляем текстовые метки
            ax1.text(0, hpi_total + 2, f'{hpi_total:.1f}', ha='center', va='bottom', fontsize=16, fontweight='bold')
            
            # Добавляем цветовые зоны
            self._add_hpi_zones(ax1)
            
            # Нижний график - оценки по сферам
            sphere_nums = list(range(1, 9))
            sphere_values = [scores.get(str(i), 1.0) for i in sphere_nums]
            sphere_colors = [self.sphere_colors[str(i)] for i in sphere_nums]
            
            bars = ax2.bar(sphere_nums, sphere_values, color=sphere_colors, alpha=0.7, edgecolor='black', linewidth=1)
            ax2.set_ylim(0, 10)
            ax2.set_xlim(0.5, 8.5)
            ax2.set_ylabel('Score', fontsize=12, fontweight='bold')
            ax2.set_title('Оценки по сферам жизни', fontsize=14, fontweight='bold')
            ax2.set_xticks(sphere_nums)
            ax2.set_xticklabels([self.sphere_names[str(i)] for i in sphere_nums], rotation=45, ha='right')
            ax2.grid(True, alpha=0.3, axis='y')
            
            # Добавляем значения на столбцы
            for bar, value in zip(bars, sphere_values):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{value:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            plt.tight_layout()
            
            # Сохраняем в буфер
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
            buf.seek(0)
            plt.close()
            
            return buf
            
        except Exception as e:
            self.logger.error(f"Ошибка создания графика тренда: {e}")
            return None
    
    def _get_hpi_color(self, hpi_score: float) -> str:
        """Возвращает цвет для HPI в зависимости от значения."""
        if hpi_score >= 80:
            return '#4CAF50'  # Зеленый
        elif hpi_score >= 60:
            return '#2196F3'  # Синий
        elif hpi_score >= 40:
            return '#FF9800'  # Оранжевый
        else:
            return '#F44336'  # Красный
    
    def _add_hpi_zones(self, ax):
        """Добавляет цветовые зоны на график HPI."""
        zones = [
            (80, 100, '#4CAF50', 'Отлично'),
            (60, 80, '#2196F3', 'Хорошо'),
            (40, 60, '#FF9800', 'Удовлетворительно'),
            (20, 40, '#F44336', 'Требует внимания')
        ]
        
        for min_val, max_val, color, label in zones:
            rect = patches.Rectangle((0, min_val), 1, max_val - min_val, 
                                   linewidth=0, facecolor=color, alpha=0.1)
            ax.add_patch(rect)
            ax.text(0.5, (min_val + max_val) / 2, label, ha='center', va='center', 
                   fontsize=10, fontweight='bold', rotation=90)
    
    def create_radar_chart_compare(self, scores_prev: Dict[str, float], scores_curr: Dict[str, float]) -> Optional[io.BytesIO]:
        """
        Создаёт радар-диаграмму сравнения баланса по сферам жизни (прошлый и текущий результат).
        """
        try:
            # Подготовка данных
            categories = list(self.sphere_names.values())
            N = len(categories)
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]
            # Значения
            values_prev = [scores_prev.get(str(i), 1.0) for i in range(1, 9)]
            values_curr = [scores_curr.get(str(i), 1.0) for i in range(1, 9)]
            values_prev += values_prev[:1]
            values_curr += values_curr[:1]
            # Стилизация
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
            polar_ax = cast(PolarAxes, ax)
            polar_ax.set_theta_offset(np.pi / 2)
            polar_ax.set_theta_direction(-1)
            # Оси и подписи
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=12, fontweight='bold')
            ax.set_ylim(0, 10)
            # Линии
            ax.plot(angles, values_prev, color="deepskyblue", linewidth=2, label="Прошлый", marker="o")
            ax.fill(angles, values_prev, color="deepskyblue", alpha=0.15)
            ax.plot(angles, values_curr, color="magenta", linewidth=2, label="Текущий", marker="o")
            ax.fill(angles, values_curr, color="magenta", alpha=0.15)
            # Сетка
            levels = [2, 4, 6, 8, 10]
            for y in levels[:-1]:
                ax.plot(angles, [y] * len(angles), '--', color='white', alpha=0.3, linewidth=0.7)
            for angle in angles[:-1]:
                ax.plot([angle, angle], [0, 10], '--', color='white', alpha=0.3, linewidth=0.7)
            # Цвета текста
            ax.tick_params(colors='white', pad=10, labelsize=12)
            for label in ax.get_xticklabels():
                label.set_color('white')
            for label in ax.get_yticklabels():
                label.set_color('#cccccc')
            # Заголовок и легенда
            ax.set_title("Баланс по сферам жизни (сравнение)", fontsize=16, pad=20, color='white', fontweight='bold')
            ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=200, bbox_inches='tight', facecolor='#1e1e1e')
            buf.seek(0)
            plt.close()
            return buf
        except Exception as e:
            self.logger.error(f"Ошибка создания сравнительной радар-диаграммы: {e}")
            return None 