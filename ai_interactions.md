# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

All work was done with Claude Code (Claude Opus 5.5) in the Claude desktop app, acting agentically in this repo: reading files, running `pytest`, `flake8`, and the headless repro script, and editing code. Every change landed as its own commit, so `git log` shows each step.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Add a "High Score" tracker (Challenge 2) that saves the best score to a file, in a way that fits the architecture from the bug fixes: game rules stay pure and tested in their own module, and `app.py` only displays them.

**What did the agent do?**

1. Wrote `tests/test_high_scores.py` first (11 tests) and ran it to confirm it failed before any implementation existed.
2. Created `high_scores.py` with `load_high_scores`, `record_high_score`, and `save_high_scores`. Design choices: a missing or corrupt file loads as empty instead of crashing the game; `record_high_score` returns a new dict instead of mutating its input; saves are atomic (write a temp file, then `os.replace`) so a crash mid-save cannot corrupt the file. Only wins count toward a high score.
3. Edited `app.py`: imported the module, added a sidebar "🏆 Best <difficulty> score" line, and recorded and saved the score on a win with a "🏆 New best" message.
4. Added `high_scores.json` and `*.tmp` to `.gitignore`.
5. Ran `pytest` (66 passed) and `flake8` (one line too long in the new test file, fixed).
6. Drove the app headlessly with `AppTest` against a throwaway file: the sidebar showed "none yet", then 100 after a first-try win, and stayed at 100 after a later 85-point win.

Files modified: `high_scores.py` (new), `tests/test_high_scores.py` (new), `app.py`, `.gitignore`, `scripts/repro_bugs.py`, `bug_repro_after.txt`. Commit: `feat: per-difficulty high score tracker saved to high_scores.json`.

**What did you have to verify or fix manually?**

- **The repro script started writing real high scores.** Scenario B ends in a win, so after this feature `scripts/repro_bugs.py` wrote to the real `high_scores.json`, and its output depended on whatever was already in that file. That makes the evidence trace non-reproducible. Fix: a `HIGH_SCORES_FILE` environment variable overrides the path, and the script points it at a temp file.
- **Rerun-order bug, again.** A sidebar "Best score" drawn at the top of the script would show the old best right after a winning guess, the same rerun-order bug as the stale "Attempts left" box (bug 5). Fix: the sidebar line is a placeholder filled by `show_status()` at the end of the run.
- **Stale module in the live app.** After the UI feature was added, the running Streamlit server raised `ImportError: cannot import name 'guess_temperature'` even though `pytest` passed. The server process had cached the old `logic_utils` module; restarting it fixed the error. The lesson: when the tests and the live app disagree, suspect the environment before the code.

<!-- Add any correction you made yourself after reviewing the diff. -->

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

Every bug fix was test-first: Claude wrote a failing regression test, ran it to confirm it failed for the right reason, then fixed the code. The edge cases below come from `tests/test_parse_guess.py`. The prompts were my answers to Claude's design questions about how invalid input should behave; Claude turned each rule into specific inputs.

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Decimals (`12.7`, `100.5`, `0.5`, `-3.5`) | "Reject with a message and make it easy for the user to round up or down based on their initial input, something like 'try X or Y instead?'" | `test_decimal_is_rejected_with_both_neighbours_suggested`, `test_decimal_suggestions_skip_neighbours_outside_the_range`, `test_decimal_with_no_neighbour_in_range_reports_the_range` | Failed against the starter (it truncated 12.7 to 12), passes after the fix | Silent truncation changes what the player typed. The range-edge cases matter because a careless fix would suggest 101 on a 1 to 100 game |
| Out-of-range and negative numbers (`0`, `101`, `-5`, a 22-digit number) | "Nothing, show error" (choice for: what should an out-of-range or non-numeric guess cost the player?) | `test_out_of_range_numbers_are_rejected`, `test_range_bounds_are_inclusive` | Failed against the starter (accepted everything), passes after | The starter accepted any int and burned an attempt. Testing 1 and 100 too catches an off-by-one in the bounds check |
| Non-numbers, including floats Python accepts (`abc`, `12abc`, `nan`, `inf`, `-inf`) | Same "Nothing, show error" answer | `test_non_numbers_are_rejected` | Passes | `float("nan")` and `float("inf")` parse without error, so a decimal-handling fix that falls back to `float()` would let them through, and `int(float("inf"))` raises `OverflowError`, which a narrow `except ValueError` would not catch. The fix rejects them with `math.isfinite` |
| Empty and whitespace-only input (`None`, `""`, `"   "`) | Same | `test_empty_input_asks_for_a_guess`, `test_surrounding_whitespace_is_ignored` | Passes | The starter only checked `== ""`, so a guess of spaces fell through to "That is not a number." instead of "Enter a guess." |
| Whole number written as a decimal (`12.0`) | Same decimal answer | `test_decimal_that_is_a_whole_number_is_accepted` | Passes | Rejecting `12.0` as "not whole" would be wrong, so the check uses `float.is_integer()` |

Terminal output for the full suite is in `README.md` under Test Results and in `test_results.txt`.

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

**Prompt used:**

```
3: Docstrings + PEP 8 (Recommended) -- +2. Docstrings on logic_utils,
ruff/flake8 lint output logged in ai_interactions.md.
```

(My stretch selection in Claude Code. Claude then ran `flake8` with the `flake8-docstrings` plugin, fixed every finding, and re-ran it.)

**Linting output before:**

78 findings: 36 D103 (function missing a docstring), 35 E501 (line over 79 characters), 6 D100 (module missing a docstring), 1 E303 (too many blank lines). Full output: `lint_before.txt`. A sample:

```
app.py:1:1: D100 Missing docstring in public module
app.py:34:1: E303 too many blank lines (3)
app.py:55:80: E501 line too long (96 > 79 characters)
logic_utils.py:22:80: E501 line too long (89 > 79 characters)
logic_utils.py:62:80: E501 line too long (97 > 79 characters)
tests/test_game_state.py:37:80: E501 line too long (103 > 79 characters)
tests/test_scoring.py:22:80: E501 line too long (94 > 79 characters)
```

**Linting output after:** `flake8 .` reports 0 findings (`lint_after.txt`).

**Changes applied:**

- Google-style docstrings (Args, Returns, Raises) on every function in `logic_utils.py`, plus module docstrings everywhere and one-line docstrings on the helpers in `app.py` and `scripts/repro_bugs.py`.
- Wrapped every line to PEP 8's 79 characters. Where wrapping made a line uglier, the code was restructured instead: a `rejected(message)` helper in `tests/test_parse_guess.py`, a named `ranges` list in `tests/test_game_state.py`, and a `_settings_for()` helper in `logic_utils.py` that also removed a duplicated fallback expression.
- Added a `setup.cfg` so the lint rules live in the repo, not in someone's memory.
- **Not applied:** docstrings on test functions (flake8's D103). Names like `test_first_try_win_scores_100` already say what each test checks, and a docstring would repeat them. The exemption is written down in `setup.cfg` (`per-file-ignores = tests/*:D103`), not just ignored.
- Verified behavior was unchanged: 46 tests still passed and the repro trace was identical before and after.

`flake8` and `flake8-docstrings` are development tools, so they're listed in `requirements-dev.txt`, not in the app's `requirements.txt`.

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

**Task given to both models:**

The same prompt (`model_comparison/prompt.txt`), on an untouched copy of the starter code, in a fresh session with read-only access: explain why the "Go HIGHER / Go LOWER" hints are inconsistent (with the example that a guess of 9 against a secret of 50 is sometimes "Too High"), and propose a focused fix as a diff. Raw answers: `model_comparison/claude_sonnet.md` and `model_comparison/codex_gpt-5.5.md`.

| | Model A | Model B |
|-|---------|---------|
| **Model name** | Claude Sonnet (fresh Claude Code agent) | OpenAI gpt-5.5 via Codex CLI 0.154.0 (reasoning effort high) |
| **Response summary** | Found both causes: the even-attempt `str(secret)` cast and the `except TypeError` fallback that compares text (`"9" > "50"`), plus the swapped messages. Explained why the hints are only *sometimes* wrong: on string turns, the wrong "Too High" label is paired with the swapped "Go HIGHER!" text, which happens to be correct advice. Diff removes the fallback, swaps the messages, and passes `st.session_state.secret` straight into `check_guess`. **Contained one false claim** (see below). | Found the same two causes in about a third of the length. Diff removes the fallback and swaps the messages, but keeps a now-pointless local variable (`secret = st.session_state.secret`) where the branch used to be. No factual errors. |
| **More Pythonic?** | Slightly: the call site uses `st.session_state.secret` directly, with no leftover variable. | Nearly identical; the leftover `secret = ...` line is harmless but adds nothing. |
| **Clearer explanation?** | More complete: the "accidentally correct on string turns" point is the real reason the bug looks random, and neither the prompt nor Codex mentions it. | Shorter and easier to scan, and nothing in it is wrong. |

**The hallucination.** Claude claimed that on a string turn `int == str` is always False, "so an exact guess can never win on a string turn." That is false: the `except TypeError` branch re-checks `str(guess) == secret` and returns "Win". Our own evidence disproves it. In the starter the first submit is always a string turn (attempts goes from 1 to 2), and Scenario B in `bug_repro_before.txt` wins on that first submit with a guess of 50. The fix itself was still correct. This is the course's "verify, don't trust" point in miniature: a confident, plausible explanation can contain a wrong sentence, and a test or trace is what catches it.

**Which did you prefer and why?**

<!-- Your conclusion -->
