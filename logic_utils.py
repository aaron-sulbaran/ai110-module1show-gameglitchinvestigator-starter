import random

# FIX: single source of truth for every difficulty. The range used to live in three
# places (this function, the hint text, and New Game's hardcoded randint(1, 100))
# and they disagreed. Hard was also 1 to 50, an easier range than Normal.
# Each limit is ceil(log2(range_size + 1)) plus slack: one spare guess on Easy
# and Normal, zero on Hard, so Hard is winnable only by a perfect binary search.
DIFFICULTY_SETTINGS = {
    "Easy": {"range": (1, 20), "attempts": 6},
    "Normal": {"range": (1, 100), "attempts": 8},
    "Hard": {"range": (1, 200), "attempts": 8},
}


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    return DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS["Normal"])["range"]


def get_attempt_limit(difficulty: str) -> int:
    return DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS["Normal"])["attempts"]


def new_game_state(difficulty: str, rng=random) -> dict:
    # FIX: one reset path for first load, New Game, and difficulty changes. New Game
    # used to reset only attempts and secret, leaving status "won" forever.
    low, high = get_range_for_difficulty(difficulty)
    return {
        "secret": rng.randint(low, high),
        "attempts": 0,
        "score": 0,
        "status": "playing",
        "history": [],
        "difficulty": difficulty,
    }


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        # FIXME: decimals are silently truncated and out-of-range guesses are accepted
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    # FIX: removed the `except TypeError` fallback that compared values as text
    # ("9" > "50" is True). A str secret is a caller bug, so it should raise, not
    # quietly return a wrong hint. Found by asking Claude why hints flipped on
    # alternating guesses.
    # FIX: outcome labels were right but the messages were swapped. Claude traced
    # it during the bug hunt; the regression tests in tests/ pin the direction.
    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        # FIXME: off by one, a first-try win scores 80 instead of 100
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        # FIXME: a wrong guess should never add points
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score
