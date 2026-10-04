import streamlit as st

from logic_utils import (
    DIFFICULTY_SETTINGS,
    check_guess,
    get_attempt_limit,
    get_range_for_difficulty,
    new_game_state,
    parse_guess,
    update_score,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    list(DIFFICULTY_SETTINGS),
    index=1,
)

attempt_limit = get_attempt_limit(difficulty)
low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")



def start_new_game() -> None:
    st.session_state.update(new_game_state(difficulty))


# FIX: every reset goes through new_game_state(). This one check covers the first
# page load (no difficulty stored yet) and a difficulty change mid-game, which used
# to leave a secret like 87 inside Easy's 1 to 20 range. Attempts now start at 0
# everywhere instead of 1 here and 0 after New Game.
if st.session_state.get("difficulty") != difficulty:
    start_new_game()

st.subheader("Make a guess")

# FIX: Streamlit reruns this script top to bottom on every click, so an st.info
# drawn here showed the attempt count from before the submit block ran. Reserve
# the slot now and fill it at the end, after the guess is processed.
status_slot = st.empty()


def show_status() -> None:
    attempts_left = attempt_limit - st.session_state.attempts
    status_slot.info(f"Guess a number between {low} and {high}. Attempts left: {attempts_left}")


with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    start_new_game()
    st.rerun()

if st.session_state.status != "playing":
    show_status()
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    ok, guess_int, err = parse_guess(raw_guess, low, high)

    # FIX: validate before counting. Invalid input used to consume an attempt and
    # land in the guess history.
    if not ok:
        st.error(err)
    else:
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        # FIX: the secret used to be cast to str on every even attempt, which made
        # hints flip between right and wrong. Always compare int to int.
        outcome, message = check_guess(guess_int, st.session_state.secret)

        if show_hint:
            st.warning(message)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

show_status()

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
