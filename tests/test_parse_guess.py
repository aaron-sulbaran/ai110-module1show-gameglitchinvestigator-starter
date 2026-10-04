import pytest

from logic_utils import parse_guess


def test_plain_whole_number_is_accepted():
    assert parse_guess("42", 1, 100) == (True, 42, None)


def test_surrounding_whitespace_is_ignored():
    assert parse_guess("  42 ", 1, 100) == (True, 42, None)


@pytest.mark.parametrize("raw", [None, "", "   "])
def test_empty_input_asks_for_a_guess(raw):
    assert parse_guess(raw, 1, 100) == (False, None, "Enter a guess.")


@pytest.mark.parametrize("raw", ["abc", "12abc", "nan", "inf", "-inf"])
def test_non_numbers_are_rejected(raw):
    ok, value, error = parse_guess(raw, 1, 100)
    assert (ok, value) == (False, None)
    assert error == "That is not a number."


# Decimals used to be silently truncated (12.7 became 12). Reject them and
# offer the whole numbers on either side instead of choosing for the player.
def test_decimal_is_rejected_with_both_neighbours_suggested():
    assert parse_guess("12.7", 1, 100) == (False, None, "Whole numbers only. Try 12 or 13?")


def test_decimal_suggestions_skip_neighbours_outside_the_range():
    assert parse_guess("100.5", 1, 100) == (False, None, "Whole numbers only. Try 100?")
    assert parse_guess("0.5", 1, 100) == (False, None, "Whole numbers only. Try 1?")


def test_decimal_with_no_neighbour_in_range_reports_the_range():
    assert parse_guess("-3.5", 1, 100) == (False, None, "Whole numbers between 1 and 100 only.")


def test_decimal_that_is_a_whole_number_is_accepted():
    assert parse_guess("12.0", 1, 100) == (True, 12, None)


@pytest.mark.parametrize("raw", ["0", "101", "-5", "1000000000000000000000"])
def test_out_of_range_numbers_are_rejected(raw):
    assert parse_guess(raw, 1, 100) == (False, None, "Pick a number between 1 and 100.")


@pytest.mark.parametrize("raw", ["1", "100"])
def test_range_bounds_are_inclusive(raw):
    ok, value, _ = parse_guess(raw, 1, 100)
    assert ok and value == int(raw)
