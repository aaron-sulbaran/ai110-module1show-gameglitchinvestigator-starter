"""Scripted reproduction of the game's bugs.

Drives app.py headlessly with Streamlit's AppTest harness, pins the secret to
a known value, and prints what the player would see after every click. Run it
against the starter to capture the bugs, and again after the fixes to confirm
the same scenarios now behave correctly.

Usage: python scripts/repro_bugs.py
"""

import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

REPO_ROOT = Path(__file__).resolve().parent.parent
APP_PATH = str(REPO_ROOT / "app.py")

# `streamlit run` puts the app's folder on sys.path; AppTest does not, so
# without this the `from logic_utils import ...` in app.py fails.
sys.path.insert(0, str(REPO_ROOT))


def start_game(secret: int, difficulty: str = "Normal") -> AppTest:
    app = AppTest.from_file(APP_PATH, default_timeout=30).run()
    if difficulty != "Normal":
        app.sidebar.selectbox[0].set_value(difficulty).run()
    app.session_state.secret = secret
    return app


def shown_messages(app: AppTest) -> list[str]:
    elements = [*app.warning, *app.error, *app.success]
    return [element.value for element in elements]


def report(app: AppTest, event: str) -> None:
    if app.exception:
        raise RuntimeError(f"app.py raised during '{event}': {app.exception[0].value}")
    state = app.session_state
    print(
        f"  {event:<24} attempts={state.attempts:<2} score={state.score:<4} "
        f"status={state.status:<8} secret={state.secret}"
    )
    print(f"  {'':<24} info: {app.info[0].value}")
    print(f"  {'':<24} shown: {shown_messages(app)}")


def guess(app: AppTest, raw: str) -> None:
    app.text_input[0].set_value(raw)
    app.button[0].click().run()
    report(app, f"guess {raw!r}")


def scenario_hints_and_scoring() -> None:
    print("\n[Scenario A] Normal difficulty, secret pinned to 50")
    app = start_game(secret=50)
    report(app, "page load")
    for raw in ["60", "60", "40", "40", "9", "100", "abc"]:
        guess(app, raw)


def scenario_new_game_after_win() -> None:
    print("\n[Scenario B] Win on the first guess, then press New Game")
    app = start_game(secret=50)
    guess(app, "50")
    app.button[1].click().run()
    report(app, "click New Game")
    guess(app, "10")


def scenario_difficulty_ranges() -> None:
    print("\n[Scenario C] Difficulty ranges and secret placement")
    for difficulty in ["Easy", "Normal", "Hard"]:
        app = AppTest.from_file(APP_PATH, default_timeout=30).run()
        app.sidebar.selectbox[0].set_value(difficulty).run()
        captions = [caption.value for caption in app.sidebar.caption]
        print(f"  {difficulty:<7} sidebar={captions} secret={app.session_state.secret}")
    app = AppTest.from_file(APP_PATH, default_timeout=30).run()
    app.session_state.secret = 87
    app.sidebar.selectbox[0].set_value("Easy").run()
    captions = [caption.value for caption in app.sidebar.caption]
    print(f"  secret 87, switch to Easy: sidebar={captions} secret={app.session_state.secret}")


if __name__ == "__main__":
    scenario_hints_and_scoring()
    scenario_new_game_after_win()
    scenario_difficulty_ranges()
