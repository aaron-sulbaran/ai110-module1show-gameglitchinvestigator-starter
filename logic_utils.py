"""Pure game logic for the number guessing game.

Everything here is free of Streamlit so it can be unit tested directly.
app.py is a thin UI layer that calls these functions and stores their
results in st.session_state.
"""

import math
import random

# FIX: single source of truth for every difficulty. The range used to live
# in three places (this module, the hint text, and New Game's hardcoded
# randint(1, 100)) and they disagreed. Hard was also 1 to 50, an easier
# range than Normal. Each limit is ceil(log2(range_size + 1)) plus slack:
# one spare guess on Easy and Normal, zero on Hard, so Hard is winnable
# only by a perfect binary search.
DIFFICULTY_SETTINGS = {
    "Easy": {"range": (1, 20), "attempts": 6},
    "Normal": {"range": (1, 100), "attempts": 8},
    "Hard": {"range": (1, 200), "attempts": 8},
}
DEFAULT_DIFFICULTY = "Normal"


def _settings_for(difficulty: str) -> dict:
    """Return the settings for a difficulty, falling back to Normal."""
    return DIFFICULTY_SETTINGS.get(
        difficulty, DIFFICULTY_SETTINGS[DEFAULT_DIFFICULTY]
    )


def get_range_for_difficulty(difficulty: str) -> tuple[int, int]:
    """Return the inclusive (low, high) range of secrets for a difficulty.

    Args:
        difficulty: One of the keys of DIFFICULTY_SETTINGS. Unknown values
            fall back to Normal.

    Returns:
        A (low, high) tuple; both ends are valid secrets and guesses.
    """
    return _settings_for(difficulty)["range"]


def get_attempt_limit(difficulty: str) -> int:
    """Return how many valid guesses a game at this difficulty allows.

    Args:
        difficulty: One of the keys of DIFFICULTY_SETTINGS. Unknown values
            fall back to Normal.

    Returns:
        The maximum number of counted attempts before the game is lost.
    """
    return _settings_for(difficulty)["attempts"]


def new_game_state(difficulty: str, rng=random) -> dict:
    """Build the session state for a fresh game.

    FIX: this is the single reset path, used on first load, on New Game,
    and when the difficulty changes. New Game used to reset only attempts
    and secret, leaving the status "won" forever.

    Args:
        difficulty: The difficulty to start at.
        rng: Anything with a ``randint(a, b)`` method. Defaults to the
            random module; tests pass a seeded ``random.Random``.

    Returns:
        A dict with the keys secret, attempts, score, status, history,
        and difficulty, ready to merge into st.session_state.
    """
    low, high = get_range_for_difficulty(difficulty)
    return {
        "secret": rng.randint(low, high),
        "attempts": 0,
        "score": 0,
        "status": "playing",
        "history": [],
        "difficulty": difficulty,
    }


def parse_guess(raw: str, low: int = 1, high: int = 100):
    """Validate raw text input and convert it to an in-range int guess.

    Args:
        raw: The text the player typed. May be None or blank.
        low: Smallest valid guess, inclusive.
        high: Largest valid guess, inclusive.

    Returns:
        A tuple ``(ok, guess, error)``. On success it is
        ``(True, guess, None)``; on failure ``(False, None, message)``
        where message is safe to show the player.
    """
    if raw is None or not raw.strip():
        return False, None, "Enter a guess."
    text = raw.strip()

    try:
        value = int(text)
    except ValueError:
        try:
            number = float(text)
        except ValueError:
            return False, None, "That is not a number."
        if not math.isfinite(number):
            return False, None, "That is not a number."
        if not number.is_integer():
            # FIX: decimals used to be truncated silently (12.7 became 12).
            # Reject them and offer the in-range whole numbers on either
            # side. Claude first suggested a plain rejection; I changed it
            # to suggest the neighbours.
            candidates = (math.floor(number), math.ceil(number))
            neighbours = [n for n in candidates if low <= n <= high]
            if not neighbours:
                message = f"Whole numbers between {low} and {high} only."
                return False, None, message
            options = " or ".join(str(n) for n in neighbours)
            return False, None, f"Whole numbers only. Try {options}?"
        value = int(number)

    # FIX: out-of-range guesses used to be accepted and burn an attempt.
    if not low <= value <= high:
        return False, None, f"Pick a number between {low} and {high}."
    return True, value, None


def check_guess(guess: int, secret: int):
    """Compare a guess to the secret.

    FIX: removed the ``except TypeError`` fallback that compared values as
    text ("9" > "50" is True). A str secret is a caller bug, so it now
    raises instead of quietly returning a wrong hint. Found by asking
    Claude why hints flipped on alternating guesses. The two hint messages
    were also swapped relative to their outcomes.

    Args:
        guess: The player's validated guess.
        secret: The number to find.

    Returns:
        A tuple ``(outcome, message)`` where outcome is "Win", "Too High",
        or "Too Low" and message is the hint shown to the player.

    Raises:
        TypeError: If guess and secret cannot be ordered, e.g. int vs str.
    """
    if guess == secret:
        return "Win", "🎉 Correct!"
    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Return the score after one counted guess.

    FIX: a first-try win now earns 100 (the old ``+ 1`` double counted the
    attempt), and a "Too High" guess no longer adds points on even
    attempts. The original intent is otherwise kept.

    Args:
        current_score: Score before this guess.
        outcome: "Win", "Too High", or "Too Low" from check_guess.
        attempt_number: 1-based count of attempts, including this one.

    Returns:
        The new score: plus 100 minus 10 per extra attempt (never less
        than 10) for a win, minus 5 for any miss.
    """
    if outcome == "Win":
        return current_score + max(10, 100 - 10 * (attempt_number - 1))
    if outcome in ("Too High", "Too Low"):
        return current_score - 5
    return current_score


# Distance thresholds as a fraction of the range size, checked in order. Using
# a fraction keeps "Hot" meaning the same thing on Easy (1 to 20) and Hard
# (1 to 200), where a fixed distance like 10 would not.
TEMPERATURE_BANDS = (
    (0.05, "🔥 Hot"),
    (0.15, "♨️ Warm"),
    (0.30, "🌤️ Cool"),
)


def guess_temperature(guess: int, secret: int, low: int, high: int) -> str:
    """Describe how close a guess is to the secret, relative to the range.

    Args:
        guess: The player's validated guess.
        secret: The number to find.
        low: Smallest value in the difficulty's range, inclusive.
        high: Largest value in the difficulty's range, inclusive.

    Returns:
        "🎯 Exact" for a correct guess, otherwise "🔥 Hot", "♨️ Warm",
        "🌤️ Cool", or "🧊 Cold" based on distance as a share of the range.
    """
    if guess == secret:
        return "🎯 Exact"
    closeness = abs(guess - secret) / (high - low + 1)
    for limit, label in TEMPERATURE_BANDS:
        if closeness <= limit:
            return label
    return "🧊 Cold"


def summarize_guesses(history, secret: int, low: int, high: int) -> list:
    """Build one table row per guess for the session summary.

    Args:
        history: Valid guesses in the order they were made.
        secret: The number to find.
        low: Smallest value in the difficulty's range, inclusive.
        high: Largest value in the difficulty's range, inclusive.

    Returns:
        A list of dicts with the keys "#", "Guess", "Result", and
        "Temperature", ready for st.table.
    """
    rows = []
    for number, guess in enumerate(history, start=1):
        outcome, _ = check_guess(guess, secret)
        rows.append({
            "#": number,
            "Guess": guess,
            "Result": outcome,
            "Temperature": guess_temperature(guess, secret, low, high),
        })
    return rows
