"""
Unit-тесты для клеточно-автоматной модели.

Запуск: pytest test_main.py -v
"""

import pytest
from main import (
    calculate_attractiveness,
    calculate_neighbor_bonus,
    calculate_total_score,
    should_enter_market,
    run_simulation,
    countries,
    TARGET_CODES,
    ENTERED,
    POTENTIAL,
    ENTRY_THRESHOLD,
    WEIGHTS,
    NEIGHBOR_BONUS,
)


class TestCalculateAttractiveness:
    """Тесты расчёта привлекательности."""

    def test_russia_score(self):
        """Россия: ожидаемый балл ~0.768."""
        score = calculate_attractiveness(countries["RU"])
        assert 0.7 < score < 0.8

    def test_uae_score(self):
        """ОАЭ: ожидаемый балл ~0.802."""
        score = calculate_attractiveness(countries["AE"])
        assert 0.75 < score < 0.85

    def test_scores_in_range(self):
        """Все оценки в диапазоне [0, 1]."""
        for code, data in countries.items():
            score = calculate_attractiveness(data)
            assert 0 <= score <= 1

    def test_weights_sum(self):
        """Сумма весов = 1."""
        assert abs(sum(WEIGHTS.values()) - 1.0) < 0.001


class TestNeighborBonus:
    """Тесты бонуса соседства."""

    def test_no_neighbors_no_bonus(self):
        """Нет соседей — нет бонуса."""
        bonus = calculate_neighbor_bonus("AE", {"RU": ENTERED})
        assert bonus == 0.0

    def test_neighbor_entered_gives_bonus(self):
        """Сосед на рынке — есть бонус."""
        bonus = calculate_neighbor_bonus("KZ", {"RU": ENTERED})
        assert bonus == NEIGHBOR_BONUS

    def test_neighbor_not_entered_no_bonus(self):
        """Сосед не на рынке — нет бонуса."""
        bonus = calculate_neighbor_bonus("KZ", {"RU": POTENTIAL})
        assert bonus == 0.0


class TestMarketEntry:
    """Тесты решения о входе."""

    def test_kazakhstan_enters(self):
        """Казахстан проходит порог."""
        decision, score = should_enter_market("KZ", {"RU": ENTERED})
        assert decision is True
        assert score >= ENTRY_THRESHOLD

    def test_ivory_coast_below_threshold(self):
        """Кот-д'Ивуар ниже порога."""
        decision, score = should_enter_market("CI", {})
        assert decision is False


class TestSimulation:
    """Тесты симуляции."""

    def test_history_length(self):
        """Длина истории = количество лет."""
        history, _ = run_simulation(2015, 2017)
        assert len(history) == 3

    def test_russia_preset(self):
        """Россия с 2011 года."""
        _, entry_years = run_simulation()
        assert entry_years["RU"] == 2011

    def test_entries_occur(self):
        """Есть выходы на рынок."""
        _, entry_years = run_simulation(2015, 2020)
        new_entries = {k: v for k, v in entry_years.items() if k != "RU"}
        assert len(new_entries) > 0

    def test_max_entries_per_year(self):
        """Не более 2 выходов в год."""
        history, _ = run_simulation()
        for year in history:
            assert len(year["entries"]) <= 2


class TestDataIntegrity:
    """Тесты целостности данных."""

    def test_target_codes_exist(self):
        """Все целевые страны в данных."""
        for code in TARGET_CODES:
            assert code in countries

    def test_required_fields(self):
        """Обязательные поля присутствуют."""
        fields = ["name", "population", "gdp", "smartphones", 
                  "regulatory", "competition", "infrastructure"]
        for code, data in countries.items():
            for field in fields:
                assert field in data

    def test_numeric_range(self):
        """Числовые поля в [0, 1]."""
        fields = ["population", "gdp", "smartphones", 
                  "regulatory", "competition", "infrastructure"]
        for code, data in countries.items():
            for field in fields:
                assert 0 <= data[field] <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
