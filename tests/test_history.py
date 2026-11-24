from pathlib import Path

import pandas as pd
import pytest

from history import DRAW_COLS, check_historical, load_draws


def _write(path: Path, rows):
    pd.DataFrame(rows, columns=DRAW_COLS).to_csv(path, index=False)


def test_history_loader_and_unordered_match(tmp_path):
    path = tmp_path / "649.csv"
    _write(path, [[1, 2, 3, 4, 5, 6], [41, 33, 27, 19, 12, 3]])
    draws = load_draws(path)
    assert len(draws) == 2
    assert check_historical([3, 12, 19, 27, 33, 41], draws) == 1
    assert check_historical([6, 5, 4, 3, 2, 1], draws) == 1


def test_history_loader_requires_schema(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame({"NUMBER DRAWN 1": [1]}).to_csv(path, index=False)
    with pytest.raises(ValueError, match="missing required columns"):
        load_draws(path)


def test_history_loader_rejects_missing_non_numeric_range_and_duplicates(tmp_path):
    cases = [
        [[1, 2, 3, 4, 5, None]],
        [[1, 2, 3, 4, 5, "x"]],
        [[1, 2, 3, 4, 5, 50]],
        [[1, 2, 3, 4, 5, 5]],
    ]
    for i, rows in enumerate(cases):
        path = tmp_path / f"bad_{i}.csv"
        _write(path, rows)
        with pytest.raises(ValueError):
            load_draws(path)


def test_history_loader_missing_file_is_explicit(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_draws(tmp_path / "missing.csv")
