"""Best score per difficulty, saved to a small JSON file.

Kept out of logic_utils.py on purpose: that module is pure game rules,
while this one touches the disk. The update rule (record_high_score) is
still pure, so only load and save do I/O.
"""

import json
import os
import tempfile
from pathlib import Path

# HIGH_SCORES_FILE lets scripts and tests point the game at a throwaway file
# so they never read or overwrite the player's real high scores.
HIGH_SCORES_PATH = Path(
    os.environ.get(
        "HIGH_SCORES_FILE",
        Path(__file__).resolve().parent / "high_scores.json",
    )
)


def load_high_scores(path=HIGH_SCORES_PATH) -> dict:
    """Read saved high scores, treating a missing or bad file as empty.

    A broken save file should never stop the game from starting, so any
    read or parse problem returns an empty dict instead of raising.

    Args:
        path: The JSON file to read.

    Returns:
        A dict mapping difficulty name to best score. Entries whose
        value is not an int are dropped.
    """
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {
        difficulty: score
        for difficulty, score in data.items()
        if isinstance(score, int) and not isinstance(score, bool)
    }


def record_high_score(scores: dict, difficulty: str, score: int):
    """Return updated high scores after a finished game.

    Args:
        scores: Current best score per difficulty. Not modified.
        difficulty: The difficulty the game was played at.
        score: The final score of that game.

    Returns:
        A tuple ``(new_scores, is_new_best)``. is_new_best is True only
        when the score beats the previous best (or there was none).
    """
    best = scores.get(difficulty)
    if best is not None and score <= best:
        return dict(scores), False
    return {**scores, difficulty: score}, True


def save_high_scores(path, scores: dict) -> None:
    """Write high scores atomically.

    The data goes to a temporary file in the same folder first and is then
    swapped in with os.replace, so a crash mid-write can never leave a
    half-written high_scores.json behind.

    Args:
        path: The JSON file to write.
        scores: Best score per difficulty.
    """
    path = Path(path)
    descriptor, temp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(descriptor, "w") as temp_file:
            json.dump(scores, temp_file, indent=2, sort_keys=True)
        os.replace(temp_name, path)
    except BaseException:
        os.unlink(temp_name)
        raise
