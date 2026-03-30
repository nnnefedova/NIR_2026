"""
Скрипт для генерации и сохранения графиков модели.
Запускать: python3 generate_plots.py
"""

import matplotlib
matplotlib.use('Agg')  # Без GUI

import matplotlib.pyplot as plt
import numpy as np
import os

# Импортируем данные из основного модуля
from main import (
    countries, TARGET_CODES, ENTRY_THRESHOLD, ENTERED,
    calculate_attractiveness, calculate_neighbor_bonus,
    run_simulation
)

# Создаём папку для скриншотов
os.makedirs('screenshots', exist_ok=True)

plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["font.size"] = 12


def save_attractiveness_plot():
    """Сохранить график привлекательности рынков."""
    names = [countries[code]["name"] for code in TARGET_CODES]
    base_scores = [calculate_attractiveness(countries[code]) for code in TARGET_CODES]
    states_ru = {"RU": ENTERED}
    neighbor_bonuses = [calculate_neighbor_bonus(code, states_ru) for code in TARGET_CODES]
    total_scores = [base + bonus for base, bonus in zip(base_scores, neighbor_bonuses)]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(names))
    width = 0.6

    ax.bar(x, base_scores, width, label="Базовая привлекательность", color="#3498db")
    ax.bar(x, neighbor_bonuses, width, bottom=base_scores, label="Бонус соседства", color="#2ecc71")
    ax.axhline(y=ENTRY_THRESHOLD, color="#e74c3c", linestyle="--", linewidth=2,
               label=f"Порог входа ({ENTRY_THRESHOLD})")

    ax.set_ylabel("Итоговый балл")
    ax.set_title("Оценка привлекательности рынков")
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.legend()
    ax.set_ylim(0, 1.0)

    for index, total in enumerate(total_scores):
        ax.text(index, total + 0.02, f"{total:.2f}", ha="center", fontweight="bold")

    plt.tight_layout()
    plt.savefig('screenshots/01_attractiveness.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✓ Сохранён: screenshots/01_attractiveness.png")


def save_factors_radar():
    """Сохранить радарную диаграмму факторов."""
    factors = ["population", "gdp", "smartphones", "regulatory", "competition", "infrastructure"]
    factor_labels = ["Население", "ВВП", "Смартфоны", "Барьеры\n(обр.)", "Конкуренция\n(обр.)", "Инфраструктура"]

    angles = np.linspace(0, 2 * np.pi, len(factors), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    colors = ["#3498db", "#e74c3c", "#2ecc71", "#9b59b6"]

    for index, code in enumerate(TARGET_CODES):
        data = countries[code]
        values = [
            data["population"], data["gdp"], data["smartphones"],
            1 - data["regulatory"], 1 - data["competition"], data["infrastructure"]
        ]
        values += values[:1]
        ax.plot(angles, values, "o-", linewidth=2, label=data["name"], color=colors[index])
        ax.fill(angles, values, alpha=0.10, color=colors[index])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(factor_labels)
    ax.set_ylim(0, 1)
    ax.set_title("Сравнение стран по выбранным факторам", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.0))

    plt.tight_layout()
    plt.savefig('screenshots/02_factors_radar.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✓ Сохранён: screenshots/02_factors_radar.png")


def save_timeline_plot(predicted_years):
    """Сохранить график сравнения сроков выхода."""
    names = [countries[code]["name"] for code in TARGET_CODES]
    actual_years = [countries[code]["actual_entry_year"] for code in TARGET_CODES]
    predicted = [predicted_years.get(code) for code in TARGET_CODES]

    fig, ax = plt.subplots(figsize=(12, 5))
    y_positions = np.arange(len(TARGET_CODES))

    ax.scatter(actual_years, y_positions, s=200, c="#3498db", marker="o",
               label="Фактический год", zorder=3)

    pred_years_clean = [year if year else 0 for year in predicted]
    ax.scatter(pred_years_clean, y_positions, s=200, c="#e74c3c", marker="s",
               label="Расчетный год", zorder=3)

    for index, (actual, predicted_year) in enumerate(zip(actual_years, pred_years_clean)):
        if predicted_year > 0:
            color = "#2ecc71" if abs(actual - predicted_year) <= 1 else "#f39c12"
            ax.plot([actual, predicted_year], [index, index], color=color, linewidth=2, alpha=0.7)

    ax.set_yticks(y_positions)
    ax.set_yticklabels(names)
    ax.set_xlabel("Год")
    ax.set_title("Сопоставление расчетных и фактических сроков выхода")
    ax.legend(loc="upper left")
    ax.grid(axis="x", alpha=0.3)
    ax.set_xlim(2014, 2025)

    plt.tight_layout()
    plt.savefig('screenshots/03_timeline.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✓ Сохранён: screenshots/03_timeline.png")


def main():
    print("Генерация графиков...")
    print("-" * 40)
    
    # Запускаем симуляцию для получения данных
    _, predicted_years = run_simulation()
    
    print("-" * 40)
    save_attractiveness_plot()
    save_factors_radar()
    save_timeline_plot(predicted_years)
    
    print("-" * 40)
    print("Все графики сохранены в папке screenshots/")


if __name__ == "__main__":
    main()
