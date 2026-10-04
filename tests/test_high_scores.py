"""Tests for loading, updating, and saving per-difficulty high scores."""

import json

from high_scores import load_high_scores, record_high_score, save_high_scores


def test_missing_file_means_no_high_scores(tmp_path):
    assert load_high_scores(tmp_path / "missing.json") == {}


def test_corrupt_file_is_treated_as_empty_instead_of_crashing(tmp_path):
    path = tmp_path / "high_scores.json"
    path.write_text("{not valid json")
    assert load_high_scores(path) == {}


def test_file_with_the_wrong_shape_is_treated_as_empty(tmp_path):
    path = tmp_path / "high_scores.json"
    path.write_text(json.dumps(["Normal", 90]))
    assert load_high_scores(path) == {}


def test_non_integer_entries_are_dropped(tmp_path):
    path = tmp_path / "high_scores.json"
    path.write_text(json.dumps({"Easy": 90, "Normal": "lots", "Hard": None}))
    assert load_high_scores(path) == {"Easy": 90}


def test_save_then_load_round_trips(tmp_path):
    path = tmp_path / "high_scores.json"
    save_high_scores(path, {"Easy": 90, "Hard": 40})
    assert load_high_scores(path) == {"Easy": 90, "Hard": 40}


def test_save_leaves_no_temporary_files_behind(tmp_path):
    save_high_scores(tmp_path / "high_scores.json", {"Easy": 90})
    assert [p.name for p in tmp_path.iterdir()] == ["high_scores.json"]


def test_first_score_for_a_difficulty_is_a_new_best():
    scores, is_new_best = record_high_score({}, "Normal", 70)
    assert scores == {"Normal": 70} and is_new_best


def test_higher_score_replaces_the_best():
    scores, is_new_best = record_high_score({"Normal": 70}, "Normal", 90)
    assert scores == {"Normal": 90} and is_new_best


def test_lower_or_equal_score_keeps_the_best():
    for score in (50, 70):
        scores, is_new_best = record_high_score(
            {"Normal": 70}, "Normal", score
        )
        assert scores == {"Normal": 70} and not is_new_best


def test_difficulties_are_tracked_separately():
    scores, _ = record_high_score({"Easy": 100}, "Hard", 40)
    assert scores == {"Easy": 100, "Hard": 40}


def test_recording_does_not_mutate_the_input():
    original = {"Normal": 70}
    record_high_score(original, "Normal", 90)
    assert original == {"Normal": 70}
