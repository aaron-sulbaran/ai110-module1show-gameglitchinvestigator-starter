"""Tests for check_guess: outcomes, hint direction, and type safety."""

import pytest

from logic_utils import check_guess

# check_guess returns an (outcome, message) tuple, and app.py needs both
# parts, so these starter tests unpack the outcome instead of comparing the
# tuple to a string.


def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


# Bug 1: the hint message pointed the player the wrong way.
def test_too_high_guess_tells_player_to_go_lower():
    _, message = check_guess(60, 50)
    assert "LOWER" in message


def test_too_low_guess_tells_player_to_go_higher():
    _, message = check_guess(40, 50)
    assert "HIGHER" in message


# Bug 2: app.py turned the secret into a str on even attempts, and check_guess
# swallowed the resulting TypeError and compared the two values as text.
def test_single_digit_guess_below_two_digit_secret_is_too_low():
    outcome, _ = check_guess(9, 50)
    assert outcome == "Too Low"


def test_mismatched_types_fail_loudly_instead_of_comparing_as_text():
    with pytest.raises(TypeError):
        check_guess(9, "50")
