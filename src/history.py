"""Historical combination checker for a Canadian 6/49-format CSV.

The optional source used by the original guided project was the Kaggle
"Lottery 6/49" dataset. The raw file is intentionally not bundled here.
Historical coincidence is descriptive only; under the model of independent,
uniform draws it does not update the next-draw probability.
"""
from pathlib import Path

import pandas as pd

from probability import validate_ticket

RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "649.csv"
DRAW_COLS = [f"NUMBER DRAWN {i}" for i in range(1, 7)]


def load_draws(path: Path = RAW) -> pd.Series:
    """Load and validate the six main-number columns as unordered combinations."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Historical draw file not found: {path}. "
            "Place the optional CSV at data/raw/649.csv."
        )
    df = pd.read_csv(path)
    missing = [c for c in DRAW_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Historical CSV is missing required columns: {missing}")

    raw = df[DRAW_COLS]
    numeric = raw.apply(pd.to_numeric, errors="coerce")
    if numeric.isna().any().any():
        raise ValueError("Historical draw columns contain missing/non-numeric values")
    arr = numeric.to_numpy(dtype=float)
    if not (arr == arr.astype(int)).all():
        raise ValueError("Historical draw numbers must be integers")
    arr = arr.astype(int)
    if ((arr < 1) | (arr > 49)).any():
        raise ValueError("Historical draw numbers must lie between 1 and 49")
    if any(len(set(row)) != 6 for row in arr):
        raise ValueError("Each historical draw must contain six distinct numbers")

    return pd.Series((frozenset(row) for row in arr), index=df.index,
                     name="main_numbers")


def check_historical(ticket: list[int], draws: pd.Series) -> int:
    """Count historical occurrences of the same unordered six-number set."""
    valid = frozenset(validate_ticket(ticket))
    return int((draws == valid).sum())
