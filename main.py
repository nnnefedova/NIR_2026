"""
Модель клеточного автомата для оценки выхода Яндекс.Такси
на международные рынки.
"""

from typing import Any

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["font.size"] = 12


# Состояния рынка.
BLOCKED = 0
POTENTIAL = 1
EVALUATING = 2
ENTERED = 3

TARGET_CODES = ["KZ", "AE", "RS", "CI"]


# Исходные данные модели по странам.
countries: dict[str, dict[str, Any]] = {
    "RU": {
        "name": "Россия",
        "population": 0.75,
        "gdp": 0.45,
        "smartphones": 0.80,
        "regulatory": 0.00,
        "competition": 0.20,
        "infrastructure": 0.70,
        "neighbors": ["KZ", "GE", "BY"],
        "actual_entry_year": 2011,
    },
    "KZ": {
        "name": "Казахстан",
        "population": 0.35,
        "gdp": 0.40,
        "smartphones": 0.75,
        "regulatory": 0.10,
        "competition": 0.35,
        "infrastructure": 0.55,
        "neighbors": ["RU"],
        "actual_entry_year": 2016,
    },
    "AE": {
        "name": "ОАЭ (Дубай)",
        "population": 0.90,
        "gdp": 0.85,
        "smartphones": 0.95,
        "regulatory": 0.25,
        "competition": 0.60,
        "infrastructure": 0.95,
        "neighbors": [],
        "actual_entry_year": 2022,
    },
    "RS": {
        "name": "Сербия",
        "population": 0.55,
        "gdp": 0.40,
        "smartphones": 0.75,
        "regulatory": 0.20,
        "competition": 0.40,
        "infrastructure": 0.60,
        "neighbors": [],
        "actual_entry_year": 2018,
    },
    "CI": {
        "name": "Кот-д'Ивуар",
        "population": 0.55,
        "gdp": 0.15,
        "smartphones": 0.45,
        "regulatory": 0.15,
        "competition": 0.30,
        "infrastructure": 0.35,
        "neighbors": [],
        "actual_entry_year": 2018,
    },
}


# Веса факторов в итоговой функции привлекательности.
WEIGHTS: dict[str, float] = {
    "population": 0.20,
    "gdp": 0.15,
    "smartphones": 0.20,
    "regulatory": 0.20,
    "competition": 0.15,
    "infrastructure": 0.10,
}

NEIGHBOR_BONUS = 0.15
ENTRY_THRESHOLD = 0.55
MAX_ENTRIES_PER_YEAR = 2


def calculate_attractiveness(country_data: dict[str, Any]) -> float:
    """
    Рассчитать базовую привлекательность рынка.

    Args:
        country_data: Словарь с параметрами страны.

    Returns:
        Итоговый взвешенный балл, округленный до 3 знаков.
    """
    score = (
        WEIGHTS["population"] * country_data["population"]
        + WEIGHTS["gdp"] * country_data["gdp"]
        + WEIGHTS["smartphones"] * country_data["smartphones"]
        + WEIGHTS["regulatory"] * (1 - country_data["regulatory"])
        + WEIGHTS["competition"] * (1 - country_data["competition"])
        + WEIGHTS["infrastructure"] * country_data["infrastructure"]
    )
    return round(score, 3)


def calculate_neighbor_bonus(country_code: str, states: dict[str, int]) -> float:
    """
    Рассчитать бонус за присутствие компании в соседних странах.

    Args:
        country_code: Код анализируемой страны.
        states: Текущее состояние рынков по странам.

    Returns:
        Бонус соседства, округленный до 3 знаков.
    """
    neighbors = countries[country_code].get("neighbors", [])

    if not neighbors:
        return 0.0

    entered_neighbors = sum(
        1 for neighbor in neighbors if neighbor in states and states[neighbor] == ENTERED
    )
    bonus = NEIGHBOR_BONUS * (entered_neighbors / len(neighbors))
    return round(bonus, 3)


def calculate_total_score(country_code: str, states: dict[str, int]) -> float:
    """
    Рассчитать итоговый балл страны с учетом эффекта соседства.

    Args:
        country_code: Код анализируемой страны.
        states: Текущее состояние рынков по странам.

    Returns:
        Суммарный балл страны, округленный до 3 знаков.
    """
    attractiveness = calculate_attractiveness(countries[country_code])
    neighbor_bonus = calculate_neighbor_bonus(country_code, states)
    return round(attractiveness + neighbor_bonus, 3)


def should_enter_market(country_code: str, states: dict[str, int]) -> tuple[bool, float]:
    """
    Проверить, преодолевает ли рынок порог входа.

    Args:
        country_code: Код анализируемой страны.
        states: Текущее состояние рынков по странам.

    Returns:
        Кортеж из флага решения и рассчитанного балла.
    """
    score = calculate_total_score(country_code, states)
    return score >= ENTRY_THRESHOLD, score


def print_base_attractiveness() -> None:
    """
    Вывести базовую привлекательность всех стран из модели.
    """
    print("\nБазовая привлекательность рынков:")
    print("-" * 40)

    for code, data in countries.items():
        score = calculate_attractiveness(data)
        print(f"{data['name']:20} : {score:.3f}")


def print_market_evaluation(states: dict[str, int]) -> None:
    """
    Вывести оценку целевых стран при заданном состоянии рынков.

    Args:
        states: Текущее состояние рынков по странам.
    """
    print("\nОценка стран при наличии действующего рынка в России:")
    print("-" * 60)

    for code in TARGET_CODES:
        decision, score = should_enter_market(code, states)
        label = "вход возможен" if decision else "вход откладывается"
        print(f"{countries[code]['name']:20} | score = {score:.3f} | {label}")


def run_simulation(
    start_year: int = 2015, end_year: int = 2024
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """
    Смоделировать выход компании на рынки по годам.

    Args:
        start_year: Первый год моделирования.
        end_year: Последний год моделирования.

    Returns:
        История состояний по годам и словарь прогнозных лет выхода.
    """
    states = {code: POTENTIAL for code in countries}
    states["RU"] = ENTERED

    history: list[dict[str, Any]] = []
    entry_years: dict[str, int] = {"RU": 2011}

    for year in range(start_year, end_year + 1):
        candidates: list[dict[str, Any]] = []

        for code in countries:
            if states[code] != POTENTIAL:
                continue

            decision, score = should_enter_market(code, states)
            if decision:
                candidates.append(
                    {
                        "code": code,
                        "name": countries[code]["name"],
                        "score": score,
                    }
                )

        candidates.sort(key=lambda item: item["score"], reverse=True)

        year_entries: list[dict[str, Any]] = []
        for candidate in candidates[:MAX_ENTRIES_PER_YEAR]:
            code = candidate["code"]
            states[code] = ENTERED
            entry_years[code] = year
            year_entries.append(
                {
                    "country": candidate["name"],
                    "code": code,
                    "score": candidate["score"],
                    "year": year,
                }
            )

        history.append({"year": year, "states": dict(states), "entries": year_entries})

        if year_entries:
            print(f"\n{year} год:")
            for entry in year_entries:
                print(f"  {entry['country']} (score = {entry['score']:.3f})")

    return history, entry_years


def print_comparison(predicted_years: dict[str, int]) -> None:
    """
    Сравнить фактические и расчетные годы выхода на рынок.

    Args:
        predicted_years: Словарь прогнозных лет выхода по странам.
    """
    print("\n" + "=" * 50)
    print("Сравнение с фактическими данными")
    print("=" * 50)

    print(f"\n{'Страна':<20} {'Факт':<10} {'Модель':<10} {'Отклонение':<12}")
    print("-" * 55)

    for code in TARGET_CODES:
        actual = countries[code]["actual_entry_year"]
        predicted = predicted_years.get(code, "N/A")

        if predicted != "N/A":
            diff = predicted - actual
            diff_str = f"{diff:+d} лет"
        else:
            diff_str = "нет выхода"

        print(f"{countries[code]['name']:<20} {actual:<10} {predicted:<10} {diff_str:<12}")


def plot_attractiveness() -> None:
    """
    Построить столбчатую диаграмму итоговых оценок стран.
    """
    names = [countries[code]["name"] for code in TARGET_CODES]
    base_scores = [calculate_attractiveness(countries[code]) for code in TARGET_CODES]
    states_ru = {"RU": ENTERED}
    neighbor_bonuses = [calculate_neighbor_bonus(code, states_ru) for code in TARGET_CODES]
    total_scores = [base + bonus for base, bonus in zip(base_scores, neighbor_bonuses)]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(names))
    width = 0.6

    ax.bar(x, base_scores, width, label="Базовая привлекательность", color="#3498db")
    ax.bar(
        x,
        neighbor_bonuses,
        width,
        bottom=base_scores,
        label="Бонус соседства",
        color="#2ecc71",
    )
    ax.axhline(
        y=ENTRY_THRESHOLD,
        color="#e74c3c",
        linestyle="--",
        linewidth=2,
        label=f"Порог входа ({ENTRY_THRESHOLD})",
    )

    ax.set_ylabel("Итоговый балл")
    ax.set_title("Оценка привлекательности рынков")
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.legend()
    ax.set_ylim(0, 1.0)

    for index, total in enumerate(total_scores):
        ax.text(index, total + 0.02, f"{total:.2f}", ha="center", fontweight="bold")

    plt.tight_layout()
    plt.show()


def plot_factors_comparison() -> None:
    """
    Построить радарную диаграмму факторов для целевых стран.
    """
    factors = [
        "population",
        "gdp",
        "smartphones",
        "regulatory",
        "competition",
        "infrastructure",
    ]
    factor_labels = [
        "Население",
        "ВВП",
        "Смартфоны",
        "Барьеры\n(обр.)",
        "Конкуренция\n(обр.)",
        "Инфраструктура",
    ]

    angles = np.linspace(0, 2 * np.pi, len(factors), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    colors = ["#3498db", "#e74c3c", "#2ecc71", "#9b59b6"]

    for index, code in enumerate(TARGET_CODES):
        data = countries[code]
        values = [
            data["population"],
            data["gdp"],
            data["smartphones"],
            1 - data["regulatory"],
            1 - data["competition"],
            data["infrastructure"],
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
    plt.show()


def plot_timeline(predicted_years: dict[str, int]) -> None:
    """
    Построить сравнение фактических и прогнозных сроков выхода.

    Args:
        predicted_years: Словарь прогнозных лет выхода по странам.
    """
    names = [countries[code]["name"] for code in TARGET_CODES]
    actual_years = [countries[code]["actual_entry_year"] for code in TARGET_CODES]
    predicted = [predicted_years.get(code) for code in TARGET_CODES]

    fig, ax = plt.subplots(figsize=(12, 5))
    y_positions = np.arange(len(TARGET_CODES))

    ax.scatter(
        actual_years,
        y_positions,
        s=200,
        c="#3498db",
        marker="o",
        label="Фактический год",
        zorder=3,
    )

    pred_years_clean = [year if year else 0 for year in predicted]
    ax.scatter(
        pred_years_clean,
        y_positions,
        s=200,
        c="#e74c3c",
        marker="s",
        label="Расчетный год",
        zorder=3,
    )

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
    plt.show()


def print_summary(predicted_years: dict[str, int]) -> None:
    """
    Вывести краткие выводы и оценку точности модели.

    Args:
        predicted_years: Словарь прогнозных лет выхода по странам.
    """
    print("\n" + "=" * 60)
    print("Краткие выводы")
    print("=" * 60)

    correct = 0
    total = 0

    for code in TARGET_CODES:
        actual = countries[code]["actual_entry_year"]
        predicted = predicted_years.get(code)

        if predicted:
            total += 1
            if abs(actual - predicted) <= 1:
                correct += 1

    accuracy = correct / total * 100 if total > 0 else 0

    print(
        """
1. В модели каждая страна рассматривается как отдельная клетка,
   состояние которой меняется в зависимости от набора факторов.

2. Итоговая оценка формируется на основе шести показателей:
   населения, уровня дохода, распространенности смартфонов,
   регуляторных условий, конкуренции и инфраструктуры.

3. Дополнительно учитывается эффект соседства:
   присутствие компании в близких странах повышает вероятность
   выхода на новый рынок.

4. Полученные результаты позволяют сопоставить расчетные сроки
   выхода на рынок с фактическими данными.
"""
    )

    print(f"Точность модели с допуском ±1 год: {correct} из {total} ({accuracy:.0f}%)")

    print(
        """
По результатам расчета можно отметить, что Казахстан получает
дополнительное преимущество за счет соседства с Россией.
ОАЭ характеризуются высокой базовой привлекательностью,
но одновременно и существенной конкуренцией.
Сербия и Кот-д'Ивуар выступают как примеры рынков с иными
структурными характеристиками и условиями входа.
"""
    )


def main() -> None:
    """
    Выполнить полный сценарий расчета, вывода и визуализации.
    """
    print("Импорт библиотек выполнен.")
    print("Данные по странам загружены.")

    print_base_attractiveness()
    print_market_evaluation({"RU": ENTERED})

    print("\n" + "=" * 50)
    print("Результаты моделирования")
    print("=" * 50)

    _, predicted_years = run_simulation()
    print_comparison(predicted_years)

    plot_attractiveness()
    plot_factors_comparison()
    plot_timeline(predicted_years)
    print_summary(predicted_years)


if __name__ == "__main__":
    main()
