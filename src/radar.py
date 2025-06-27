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

def create_radar_chart(scores: Dict[str, float], output_path: str, is_dashboard: bool = False) -> None:
    """Create a radar chart from HPI scores.
    
    Args:
        scores: Dictionary with sphere scores (keys '1' through '8' and 'HPI')
        output_path: Path to save the radar chart image
        is_dashboard: Whether to create a compact version for dashboard
    """
    # Подготовка данных
    categories = [
        'Отношения с\nлюбимыми',
        'Отношения с\nродными',
        'Друзья',
        'Карьера',
        'Физическое\nздоровье',
        'Ментальное\nздоровье',
        'Хобби и\nувлечения',
        'Благосостояние'
    ]

    if is_dashboard:
        # Для дашборда используем более короткие названия
        categories = [
            'Любимые',
            'Родные',
            'Друзья',
            'Карьера',
            'Физ.\nздоровье',
            'Мент.\nздоровье',
            'Хобби',
            'Благо-\nсостояние'
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
    ax.set_theta_offset(np.pi / 2.0)
    ax.set_theta_direction(-1)
    
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
    ax.set_rgrids(levels, angle=67.5, fontsize=label_size-2, fontweight='bold')
    
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
        plt.title('HPI баланс', color='white', 
                 pad=title_pad, size=title_size, fontweight='bold')
    
    plt.tight_layout()
    
    # Сохраняем диаграмму
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='#1e1e1e', pad_inches=save_pad)
    plt.close() 