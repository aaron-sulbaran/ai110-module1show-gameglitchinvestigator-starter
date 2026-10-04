"""Tests for update_score: win points and miss penalties."""

import pytest

from logic_utils import update_score


# Bug 6: a first-try win scored 70 in the app because of an off-by-one.
def test_first_try_win_scores_100():
    assert update_score(0, "Win", attempt_number=1) == 100


def test_each_extra_attempt_costs_10_win_points():
    assert update_score(0, "Win", attempt_number=3) == 80


def test_win_points_never_drop_below_10():
    assert update_score(0, "Win", attempt_number=50) == 10


# Bug 6: a "Too High" guess on an even attempt used to add 5 points.
@pytest.mark.parametrize("attempt_number", [1, 2, 3, 4])
@pytest.mark.parametrize("outcome", ["Too High", "Too Low"])
def test_every_wrong_guess_costs_5_regardless_of_direction_or_parity(
    outcome, attempt_number
):
    assert update_score(20, outcome, attempt_number) == 15
