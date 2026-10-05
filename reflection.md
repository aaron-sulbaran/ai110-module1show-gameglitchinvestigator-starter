# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
The game was unwinnable without checking the secret in the developer debug info. It would always tell the player to go lower, even though the number wasn't lower. Then, pressing new game wouldn't start a new game at all.
- List at least two concrete bugs you noticed at the start  
(for example: "the hints were backwards").
The hint would permanently state to go lower when the number was instead higher. 
There was no way to start a new game, even if the game prompted players to click new game, one would never start

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

All rows reproduced with a pinned secret of 50 on Normal unless noted. The scripted run that produced them is `scripts/repro_bugs.py`, and its full output against the starter code is committed as `bug_repro_before.txt`.


| #   | Input Used                                           | Expected Behavior                                       | Actual Behavior                                                                                     | Console Error / Output              | Suspected Code Location                                                                                                                             |
| --- | ---------------------------------------------------- | ------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Guess `60` (secret 50)                               | "Too High", tell the player to go lower                 | Outcome is "Too High" but the message says "Go HIGHER!" (and `40` says "Go LOWER!")                 | none                                | `check_guess` in `app.py`: the outcome labels are right, the two message strings are swapped                                                        |
| 2   | Guess `9` on the 6th attempt (secret 50)             | "Too Low"                                               | "Too High" / "Go HIGHER!"                                                                           | none (the `TypeError` is swallowed) | `app.py` submit block casts the secret to `str` on every even attempt; `check_guess` then catches the `TypeError` and compares `"9" > "50"` as text |
| 3   | Win, then click "New Game 🔁", then guess `10`       | A fresh game: status playing, score 0, guesses accepted | "You already won. Start a new game to play again." forever; the guess is ignored and score stays 70 | none                                | `new_game` handler in `app.py` resets `attempts` and `secret` but never `status`, `score`, or `history`                                             |
| 4   | Secret 87, switch difficulty to Easy (range 1 to 20) | Secret redrawn inside 1 to 20                           | Secret stays 87, game is unwinnable; New Game also always draws from 1 to 100                       | none                                | `st.session_state.secret` is only set once; `new_game` hardcodes `random.randint(1, 100)` instead of using `get_range_for_difficulty`               |
| 5   | Page load on Normal (8 attempts allowed)             | "Attempts left: 8" and 8 guesses                        | Shows 7 on load, still shows 7 after the first guess, and the game ends after 7 guesses             | none                                | `attempts` initialised to `1` (but reset to `0` by New Game); the info box renders before the submit block updates the count                        |
| 6   | Guess `50` on the first try                          | A high score for a first-try win                        | Score 70; and a wrong "Too High" guess on even attempts adds +5                                     | none                                | `update_score`: `100 - 10 * (attempt_number + 1)` double counts, and the "Too High" branch rewards even attempts                                    |
| 7   | Select Hard                                          | A harder game than Normal                               | Range is 1 to 50 (easier than Normal's 1 to 100); the hint text always says "between 1 and 100"     | none                                | `get_range_for_difficulty` and the hardcoded `st.info` string in `app.py`                                                                           |
| 8   | Type `abc` and submit                                | Error message, attempt not consumed                     | Error shown, but an attempt is used up and `abc` is added to history                                | `That is not a number.`             | `app.py` submit block increments `attempts` before calling `parse_guess`                                                                            |


---



## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
  - I used Claude Code as my preferred AI tool for this project.
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
  - I used AI to help me find the source of the bugs I identified, it traced it to [app.py](http://app.py) and then after reviewing the code it also suggested the fix (which was to change the int > str as it was comparing text instead of integers).
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.
  - For decimals, Claude recommended rejecting them with a plain "whole numbers only" message that used up a one of the player's attempt. I pushed back and suggested that it would simply nudge the player to choose one of whole numbers on either side ("Try 12 or 13?"), and dropping any neighbor outside the range.   
  Why: a bare rejection makes the player retype from scratch and makes them lose an attempt. The suggestion keeps the player's intent without guessing for them, which the starter's silent truncation did.   
  Verification: `test_decimal_is_rejected_with_both_neighbours_suggested`, the two range-edge tests (`100.5` → "Try 100?", `0.5` → "Try 1?"), and typing 12.7 in the live app.

---



## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
  - After verifying the bugsd visually, I would write a test that was expected to fail, implemented the bug fix, and then ran the test again to make sure it passed. 
- Describe at least one test you ran (manual or using pytest) and what it showed you about your code.
  - One of the first tests I wanted to write was one that tackled the new game reset issue which I edned up writing with Claude as def test_new_game_state_is_a_clean_slate(): , where we defined the different states of the game from Normal to playing to new.
- Did AI help you design or understand any tests? How?
  - An AI mistake caught by verification with another agent: Claude's first repro harness reported a confusing KeyError about attempts. The real cause was AppTest not putting the app folder on sys.path, so from logic_utils import ... failed, and the harness hid that error. Fixed by adding the path and making the harness raise the app's actual exception.

---



## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
  - I learned that Streamlist reruns app.py from the top on every single click so every single variable is rebuilt every single time. I'd explain it by saying it's like having a subject or concept on a white board be erased every single time you interact with it but any notes on the side of the whiteboard could be saved through session_state.

---



## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects? This could be a testing habit, a prompting strategy, or a way you used Git.
  - Being in a testing class right now and also recalling Week 2's lesson, I think I'll start by approaching tests with refactoring as the first step to flag all green tests and then fix any that fail after. As opposed to attempting to jump into fixes right away.
- What is one thing you would do differently next time you work with AI on a coding task?
  - I already do this but I have found that breaking tasks down, in this case bug fixes, into one task and one commit for each is the best way to maintain a trace or regression path in case something goes wrong.
- In one or two sentences, describe how this project changed the way you think about AI generated code.
  - Watch for any behavior from the model that catches an exception and continues writing code without addressing it. 

