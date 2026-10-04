# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

All rows reproduced with a pinned secret of 50 on Normal unless noted. The scripted run that produced them is `scripts/repro_bugs.py`, and its full output against the starter code is committed as `bug_repro_before.txt`.

| # | Input Used | Expected Behavior | Actual Behavior | Console Error / Output | Suspected Code Location |
|---|------------|-------------------|-----------------|------------------------|-------------------------|
| 1 | Guess `60` (secret 50) | "Too High", tell the player to go lower | Outcome is "Too High" but the message says "Go HIGHER!" (and `40` says "Go LOWER!") | none | `check_guess` in `app.py`: the outcome labels are right, the two message strings are swapped |
| 2 | Guess `9` on the 6th attempt (secret 50) | "Too Low" | "Too High" / "Go HIGHER!" | none (the `TypeError` is swallowed) | `app.py` submit block casts the secret to `str` on every even attempt; `check_guess` then catches the `TypeError` and compares `"9" > "50"` as text |
| 3 | Win, then click "New Game 🔁", then guess `10` | A fresh game: status playing, score 0, guesses accepted | "You already won. Start a new game to play again." forever; the guess is ignored and score stays 70 | none | `new_game` handler in `app.py` resets `attempts` and `secret` but never `status`, `score`, or `history` |
| 4 | Secret 87, switch difficulty to Easy (range 1 to 20) | Secret redrawn inside 1 to 20 | Secret stays 87, game is unwinnable; New Game also always draws from 1 to 100 | none | `st.session_state.secret` is only set once; `new_game` hardcodes `random.randint(1, 100)` instead of using `get_range_for_difficulty` |
| 5 | Page load on Normal (8 attempts allowed) | "Attempts left: 8" and 8 guesses | Shows 7 on load, still shows 7 after the first guess, and the game ends after 7 guesses | none | `attempts` initialised to `1` (but reset to `0` by New Game); the info box renders before the submit block updates the count |
| 6 | Guess `50` on the first try | A high score for a first-try win | Score 70; and a wrong "Too High" guess on even attempts adds +5 | none | `update_score`: `100 - 10 * (attempt_number + 1)` double counts, and the "Too High" branch rewards even attempts |
| 7 | Select Hard | A harder game than Normal | Range is 1 to 50 (easier than Normal's 1 to 100); the hint text always says "between 1 and 100" | none | `get_range_for_difficulty` and the hardcoded `st.info` string in `app.py` |
| 8 | Type `abc` and submit | Error message, attempt not consumed | Error shown, but an attempt is used up and `abc` is added to history | `That is not a number.` | `app.py` submit block increments `attempts` before calling `parse_guess` |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
