# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Create and activate a virtual environment: `python3 -m venv .venv && source .venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the game: `python -m streamlit run app.py`
4. Run the tests: `python -m pytest`
5. Replay the bug scenarios headlessly: `python scripts/repro_bugs.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

### The game's purpose

A Streamlit number guessing game. The player picks a difficulty (Easy 1 to 20, Normal 1 to 100, Hard 1 to 200), guesses the secret number, and gets a "go higher / go lower" hint after each guess. The game ends on a correct guess (score depends on how many attempts it took) or when the attempt limit runs out.

### Bugs found

Eight bugs, all reproduced with a pinned secret. Full table with inputs, expected vs. actual behavior, and code locations: `reflection.md` section 1. Scripted evidence: `scripts/repro_bugs.py`, with its output against the starter in `bug_repro_before.txt`.

1. **Backwards hints.** A guess of 60 against 50 said "Go HIGHER!".
2. **Hints flipped on every other guess.** `app.py` cast the secret to `str` on even attempts, and `check_guess` caught the `TypeError` and compared text (`"9" > "50"` is true).
3. **New Game never restarted.** After a win it showed "You already won" forever, because `status`, `score`, and `history` were never reset.
4. **Secret outside the range.** Changing difficulty kept the old secret (87 inside Easy's 1 to 20), and New Game always drew from 1 to 100.
5. **Off-by-one attempts.** Normal promised 8 attempts and gave 7, and the "Attempts left" box lagged one click behind.
6. **Broken scoring.** A first-try win scored 70, and a wrong "Too High" guess on an even attempt *added* 5 points.
7. **Hard was easier than Normal** (1 to 50 vs. 1 to 100), and the hint text always said "between 1 and 100".
8. **Invalid input cost an attempt.** `abc` consumed a guess, decimals were silently truncated (12.7 became 12), and out-of-range numbers were accepted.

### Fixes applied

All game logic now lives in `logic_utils.py` as pure functions, and `app.py` is a thin Streamlit layer that calls them. The move was done first as a behavior-preserving refactor (the repro trace was identical before and after), then each fix landed as its own commit with regression tests.

| Bug | Fix | Where |
|-----|-----|-------|
| 1 | Swapped the two hint messages back | `check_guess` |
| 2 | Always compare int to int; removed the `except TypeError` text fallback so a type mismatch raises instead of returning a wrong hint | `check_guess`, submit block in `app.py` |
| 3, 4, 5 | One reset path, `new_game_state(difficulty)`, used on first load, New Game, and difficulty change. Attempts start at 0 everywhere. The attempts box is a placeholder filled after the guess is processed | `new_game_state`, `start_new_game` / `show_status` in `app.py` |
| 6 | First-try win = 100, minus 10 per extra attempt (floor 10); every miss costs 5 | `update_score` |
| 7 | `DIFFICULTY_SETTINGS` is the single source of truth for ranges and limits. Hard is 1 to 200 with 8 attempts: exactly `ceil(log2(201))`, so it is winnable only with a perfect binary search | `DIFFICULTY_SETTINGS`, `get_range_for_difficulty`, `get_attempt_limit` |
| 8 | Validate before counting an attempt; reject decimals and suggest the neighbours ("Try 12 or 13?"); enforce the range; reject `nan`/`inf` | `parse_guess`, submit block in `app.py` |

The starter tests were also wrong: they compared `check_guess`'s `(outcome, message)` tuple to a bare string, so they would have failed even against correct logic. They now unpack the outcome.

## 📸 Demo Walkthrough

A Normal game with the secret set to 50 (visible under "Developer Debug Info"). Verified by driving the app with Streamlit's `AppTest` harness; the same scenarios are in `bug_repro_after.txt`.

1. Open the app on Normal. The box reads "Guess a number between 1 and 100. Attempts left: 8".
2. Enter `12.7`. The game says "Whole numbers only. Try 12 or 13?" and the attempt count stays at 8.
3. Enter `60`. The hint is "📉 Go LOWER!", attempts left drops to 7, score is -5.
4. Enter `40`. The hint is "📈 Go HIGHER!", attempts left is 6, score is -10.
5. Enter `50`. "🎉 Correct!", balloons, and "You won! The secret was 50. Final score: 70" (80 win points for a third-try win, minus 10 for the two misses).
6. Enter `7`. The guess is ignored with "You already won. Start a new game to play again."
7. Click "New Game 🔁". Score resets to 0, attempts left to 8, and a new secret is drawn inside 1 to 100.

## 🧪 Test Results

46 tests across `tests/test_game_logic.py`, `tests/test_game_state.py`, `tests/test_scoring.py`, and `tests/test_parse_guess.py`. Also saved in `test_results.txt`.

```
$ python -m pytest -v
============================= test session starts ==============================
platform darwin -- Python 3.11.7, pytest
cachedir: .pytest_cache
rootdir: ai110-module1show-gameglitchinvestigator-starter
plugins: anyio-4.15.1
collecting ... collected 46 items

tests/test_game_logic.py::test_winning_guess PASSED                      [  2%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [  4%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [  6%]
tests/test_game_logic.py::test_too_high_guess_tells_player_to_go_lower PASSED [  8%]
tests/test_game_logic.py::test_too_low_guess_tells_player_to_go_higher PASSED [ 10%]
tests/test_game_logic.py::test_single_digit_guess_below_two_digit_secret_is_too_low PASSED [ 13%]
tests/test_game_logic.py::test_mismatched_types_fail_loudly_instead_of_comparing_as_text PASSED [ 15%]
tests/test_game_state.py::test_new_game_state_is_a_clean_slate PASSED    [ 17%]
tests/test_game_state.py::test_secret_always_inside_the_difficulty_range[Easy] PASSED [ 19%]
tests/test_game_state.py::test_secret_always_inside_the_difficulty_range[Normal] PASSED [ 21%]
tests/test_game_state.py::test_secret_always_inside_the_difficulty_range[Hard] PASSED [ 23%]
tests/test_game_state.py::test_difficulty_ranges_grow_from_easy_to_hard PASSED [ 26%]
tests/test_game_state.py::test_every_difficulty_is_winnable_with_binary_search[Easy] PASSED [ 28%]
tests/test_game_state.py::test_every_difficulty_is_winnable_with_binary_search[Normal] PASSED [ 30%]
tests/test_game_state.py::test_every_difficulty_is_winnable_with_binary_search[Hard] PASSED [ 32%]
tests/test_parse_guess.py::test_plain_whole_number_is_accepted PASSED    [ 34%]
tests/test_parse_guess.py::test_surrounding_whitespace_is_ignored PASSED [ 36%]
tests/test_parse_guess.py::test_empty_input_asks_for_a_guess[None] PASSED [ 39%]
tests/test_parse_guess.py::test_empty_input_asks_for_a_guess[] PASSED    [ 41%]
tests/test_parse_guess.py::test_empty_input_asks_for_a_guess[   ] PASSED [ 43%]
tests/test_parse_guess.py::test_non_numbers_are_rejected[abc] PASSED     [ 45%]
tests/test_parse_guess.py::test_non_numbers_are_rejected[12abc] PASSED   [ 47%]
tests/test_parse_guess.py::test_non_numbers_are_rejected[nan] PASSED     [ 50%]
tests/test_parse_guess.py::test_non_numbers_are_rejected[inf] PASSED     [ 52%]
tests/test_parse_guess.py::test_non_numbers_are_rejected[-inf] PASSED    [ 54%]
tests/test_parse_guess.py::test_decimal_is_rejected_with_both_neighbours_suggested PASSED [ 56%]
tests/test_parse_guess.py::test_decimal_suggestions_skip_neighbours_outside_the_range PASSED [ 58%]
tests/test_parse_guess.py::test_decimal_with_no_neighbour_in_range_reports_the_range PASSED [ 60%]
tests/test_parse_guess.py::test_decimal_that_is_a_whole_number_is_accepted PASSED [ 63%]
tests/test_parse_guess.py::test_out_of_range_numbers_are_rejected[0] PASSED [ 65%]
tests/test_parse_guess.py::test_out_of_range_numbers_are_rejected[101] PASSED [ 67%]
tests/test_parse_guess.py::test_out_of_range_numbers_are_rejected[-5] PASSED [ 69%]
tests/test_parse_guess.py::test_out_of_range_numbers_are_rejected[1000000000000000000000] PASSED [ 71%]
tests/test_parse_guess.py::test_range_bounds_are_inclusive[1] PASSED     [ 73%]
tests/test_parse_guess.py::test_range_bounds_are_inclusive[100] PASSED   [ 76%]
tests/test_scoring.py::test_first_try_win_scores_100 PASSED              [ 78%]
tests/test_scoring.py::test_each_extra_attempt_costs_10_win_points PASSED [ 80%]
tests/test_scoring.py::test_win_points_never_drop_below_10 PASSED        [ 82%]
tests/test_scoring.py::test_every_wrong_guess_costs_5_regardless_of_direction_or_parity[Too High-1] PASSED [ 84%]
tests/test_scoring.py::test_every_wrong_guess_costs_5_regardless_of_direction_or_parity[Too High-2] PASSED [ 86%]
tests/test_scoring.py::test_every_wrong_guess_costs_5_regardless_of_direction_or_parity[Too High-3] PASSED [ 89%]
tests/test_scoring.py::test_every_wrong_guess_costs_5_regardless_of_direction_or_parity[Too High-4] PASSED [ 91%]
tests/test_scoring.py::test_every_wrong_guess_costs_5_regardless_of_direction_or_parity[Too Low-1] PASSED [ 93%]
tests/test_scoring.py::test_every_wrong_guess_costs_5_regardless_of_direction_or_parity[Too Low-2] PASSED [ 95%]
tests/test_scoring.py::test_every_wrong_guess_costs_5_regardless_of_direction_or_parity[Too Low-3] PASSED [ 97%]
tests/test_scoring.py::test_every_wrong_guess_costs_5_regardless_of_direction_or_parity[Too Low-4] PASSED [100%]

============================== 46 passed in 0.02s ==============================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
