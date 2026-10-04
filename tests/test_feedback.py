"""Tests for the hot/cold temperature and the guess summary table."""

import pytest

from logic_utils import guess_temperature, summarize_guesses


@pytest.mark.parametrize(
    ("guess", "expected"),
    [
        (50, "🎯 Exact"),
        (53, "🔥 Hot"),  # within 5% of a 100-number range
        (40, "♨️ Warm"),  # within 15%
        (75, "🌤️ Cool"),  # within 30%
        (1, "🧊 Cold"),  # anything farther
    ],
)
def test_temperature_bands_on_normal_range(guess, expected):
    assert guess_temperature(guess, secret=50, low=1, high=100) == expected


def test_temperature_scales_with_the_range_size():
    # 10 away is "Cold" on Easy (1 to 20) but "Warm" on Normal (1 to 100).
    assert guess_temperature(15, secret=5, low=1, high=20) == "🧊 Cold"
    assert guess_temperature(60, secret=50, low=1, high=100) == "♨️ Warm"


def test_temperature_is_symmetric_above_and_below():
    above = guess_temperature(58, secret=50, low=1, high=100)
    below = guess_temperature(42, secret=50, low=1, high=100)
    assert above == below


def test_summary_has_one_row_per_guess_in_order():
    rows = summarize_guesses([60, 40, 50], secret=50, low=1, high=100)
    assert [row["Guess"] for row in rows] == [60, 40, 50]
    assert [row["#"] for row in rows] == [1, 2, 3]
    assert [row["Result"] for row in rows] == ["Too High", "Too Low", "Win"]


def test_summary_of_no_guesses_is_empty():
    assert summarize_guesses([], secret=50, low=1, high=100) == []
