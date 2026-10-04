"""Tests for difficulty settings and the new-game reset path."""

import math
import random

import pytest

from logic_utils import (
    DIFFICULTY_SETTINGS,
    get_attempt_limit,
    get_range_for_difficulty,
    new_game_state,
)

DIFFICULTIES = list(DIFFICULTY_SETTINGS)


# Bug 3: New Game never reset status, score, or history, so a won game
# stayed won.
def test_new_game_state_is_a_clean_slate():
    state = new_game_state("Normal", rng=random.Random(0))
    assert state["status"] == "playing"
    assert state["score"] == 0
    assert state["attempts"] == 0
    assert state["history"] == []
    assert state["difficulty"] == "Normal"


# Bug 4: the secret could sit outside the range the player was told about.
@pytest.mark.parametrize("difficulty", DIFFICULTIES)
def test_secret_always_inside_the_difficulty_range(difficulty):
    low, high = get_range_for_difficulty(difficulty)
    rng = random.Random(42)
    secrets = [
        new_game_state(difficulty, rng=rng)["secret"] for _ in range(500)
    ]
    assert all(low <= secret <= high for secret in secrets)


# Bug 7: Hard (1 to 50) was an easier range than Normal (1 to 100).
def test_difficulty_ranges_grow_from_easy_to_hard():
    ranges = [get_range_for_difficulty(d) for d in DIFFICULTIES]
    sizes = [high - low + 1 for low, high in ranges]
    assert sizes == sorted(sizes) and len(set(sizes)) == len(sizes)


# Binary search halves the candidates each guess, so a range of n numbers needs
# at most ceil(log2(n + 1)) guesses. Every difficulty must be winnable by
# perfect play.
@pytest.mark.parametrize("difficulty", DIFFICULTIES)
def test_every_difficulty_is_winnable_with_binary_search(difficulty):
    low, high = get_range_for_difficulty(difficulty)
    guesses_needed = math.ceil(math.log2(high - low + 2))
    assert get_attempt_limit(difficulty) >= guesses_needed
