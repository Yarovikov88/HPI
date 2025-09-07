"""
HPI Radar Chart Generator
Version: 0.1
Release Date: 2024-05-31
Status: Stable

Модуль генерации радарных диаграмм для визуализации HPI.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict
import io
from src.telegram_bot_multi.db_async import get_user_id_by_telegram_id, get_user_answers
from src.calculator import HPICalculator

def create_radar_chart(scores: Dict[str, float], output_path: str, is_dashboard: bool = False) -> None:
    """Create a radar chart from HPI scores.
    
    Args:
        scores: Dictionary with sphere scores (keys '1' through '8' and 'HPI')
        output_path: Path to save the radar chart image
        is_dashboard: Whether to create a compact version for dashboard
    """
    # Подготовка данных
    categories = [
        'Romantic relationships',
        'Family relationships',
        'Friends',
        'Career',
        'Physical health',
        'Mental health',
        'Hobbies and interests',
        'Wealth'
    ]

    if is_dashboard:
        # Для дашборда используем более короткие названия
        categories = [
            'Romantic',
            'Family',
            'Friends',
            'Career',
            'Physical',
            'Mental',
            'Hobbies',
            'Wealth'
        ]
    
    # Получаем значения сфер в правильном порядке
    values = [scores[str(i)] for i in range(1, 9)]
    values += values[:1]  # Замыкаем полигон
    
    # Преобразуем категории в углы для радарной диаграммы
    angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
    angles = np.concatenate((angles, [angles[0]]))  # Замыкаем углы
    
    # Настраиваем размеры и стили в зависимости от версии
    if is_dashboard:
        fig_size = (8, 8)
        title_size = 12
        label_size = 10
        marker_size = 6
        line_width = 2
        grid_width = 0.5
        title_pad = 15
        label_pad = 8
        save_pad = 0.3
    else:
        fig_size = (14, 14)
        title_size = 16
        label_size = 12
        marker_size = 8
        line_width = 2.5
        grid_width = 0.8
        title_pad = 30
        label_pad = 15
        save_pad = 0.7
    
    # Создаем фигуру
    plt.figure(figsize=fig_size, facecolor='#1e1e1e')
    ax = plt.subplot(111, polar=True)
    
    # Настраиваем внешний вид
    ax.set_facecolor('#2d2d2d')
    ax.set_theta_offset(np.pi / 2.0)  # type: ignore[attr-defined]
    ax.set_theta_direction(-1)  # type: ignore[attr-defined]
    
    # Рисуем график
    ax.plot(angles, values, 'o-', linewidth=line_width, color='#ff00ff', 
           label='Значения', markersize=marker_size)
    ax.fill(angles, values, alpha=0.25, color='#ff00ff')
    
    # Настраиваем метки
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=label_size, fontweight='bold')
    
    # Настраиваем шкалу
    ax.set_ylim(0, 10)
    levels = [2, 4, 6, 8, 10]
    ax.set_rgrids(levels, angle=67.5, fontsize=label_size-2, fontweight='bold')  # type: ignore[attr-defined]
    
    # Настраиваем цвета текста
    ax.tick_params(colors='white', pad=label_pad, labelsize=label_size)
    for label in ax.get_xticklabels():
        label.set_color('white')
    for label in ax.get_yticklabels():
        label.set_color('#cccccc')
    
    # Добавляем сетку
    for y in levels[:-1]:
        ax.plot(angles, [y] * len(angles), '--', color='white', alpha=0.3, linewidth=grid_width)
        
    # Добавляем радиальные линии
    for angle in angles[:-1]:
        ax.plot([angle, angle], [0, 10], '--', color='white', alpha=0.3, linewidth=grid_width)
    
    # Добавляем заголовок
    if not is_dashboard:  # Заголовок только для полной версии
        plt.title('HPI Balance', color='white', 
                 pad=title_pad, size=title_size, fontweight='bold')
    
    plt.tight_layout()
    
    # Сохраняем диаграмму
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='#1e1e1e', pad_inches=save_pad)
    plt.close() 

async def plot_radar_chart_for_telegram(user_id, lang='en'):
    """
    Строит радар-график по последним ответам пользователя и возвращает BytesIO для Telegram.
    Использует HPICalculator для расчёта баллов по сферам (шкала Фибоначчи, нормализация, инверсии).
    """
    answers = await get_user_answers(user_id)
    spheres = {str(i): [] for i in range(1, 9)}
    for row in answers:
        if isinstance(row, dict):
            sphere = str(row.get('sphere'))
            answer = row.get('answer')
        else:
            sphere = str(row[0])
            answer = row[2]
        if sphere in spheres:
            spheres[sphere].append(answer)
    answers_dict = {}
    for i in range(1, 9):
        key = str(i)
        vals = spheres[key][-6:]
        if len(vals) == 6:
            answers_dict[key] = vals
        else:
            answers_dict[key] = [0]*6
    calculator = HPICalculator()
    hpi_total, scores = calculator.calculate_from_answers(answers_dict)
    # --- Языковые подписи ---
    if lang == 'ru':
        categories = [
            'Отношения с любимыми',
            'Отношения с родными',
            'Друзья',
            'Карьера',
            'Физическое здоровье',
            'Ментальное здоровье',
            'Хобби и увлечения',
            'Благосостояние'
        ]
        title = 'Баланс по сферам'
    else:
        categories = [
            'Romantic relationships',
            'Family relationships',
            'Friends',
            'Career',
            'Physical health',
            'Mental health',
            'Hobbies and interests',
            'Wealth'
        ]
        title = 'HPI Balance'
    values = [scores[str(i)] for i in range(1, 9)]
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)
    angles = np.concatenate((angles, [angles[0]]))
    plt.figure(figsize=(8, 8), facecolor='#1e1e1e')
    ax = plt.subplot(111, polar=True)
    ax.set_facecolor('#2d2d2d')
    ax.set_theta_offset(np.pi / 2.0)  # type: ignore[attr-defined]
    ax.set_theta_direction(-1)  # type: ignore[attr-defined]
    ax.plot(angles, values, 'o-', linewidth=2, color='#ff00ff', markersize=7)
    ax.fill(angles, values, alpha=0.25, color='#ff00ff')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10, fontweight='bold', color='white')
    ax.set_ylim(0, 10)
    levels = [2, 4, 6, 8, 10]
    ax.set_rgrids(levels, angle=67.5, fontsize=8, fontweight='bold', color='#cccccc')  # type: ignore[attr-defined]
    ax.tick_params(colors='white', pad=8, labelsize=10)
    for label in ax.get_yticklabels():
        label.set_color('#cccccc')
    for y in levels[:-1]:
        ax.plot(angles, [y] * len(angles), '--', color='white', alpha=0.3, linewidth=0.5)
    for angle in angles[:-1]:
        ax.plot([angle, angle], [0, 10], '--', color='white', alpha=0.3, linewidth=0.5)
    plt.title(title, color='white', pad=15, size=12, fontweight='bold')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#1e1e1e', pad_inches=0.3)
    buf.seek(0)
    plt.close()
    return buf 