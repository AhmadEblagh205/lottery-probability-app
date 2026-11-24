"""Probability utilities for an illustrative 6-from-49 lottery model.

The combinatorial event counts are exact integers. Public-facing probabilities
are ratios of those counts, represented as Python floats for convenience.
"""
from __future__ import annotations

from math import comb, expm1, isfinite, log1p, log
from numbers import Integral
from typing import Mapping

N_NUMBERS = 49
TICKET_SIZE = 6
TOTAL = comb(N_NUMBERS, TICKET_SIZE)  # 13,983,816 unordered tickets

# Illustrative fixed-prize table. This is deliberately not labelled as the
# current payout table of any real operator; actual lotteries can have bonus
# games, changing jackpots and shared/pari-mutuel prizes.
DEFAULT_PRIZES = {6: 5_000_000.0, 5: 1_750.0, 4: 140.0, 3: 30.0}


def _nonnegative_int(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{name} must be an integer")
    value = int(value)
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
    return value


def validate_ticket(ticket: list[int] | tuple[int, ...]) -> tuple[int, ...]:
    """Return a sorted validated 6-number ticket."""
    if len(ticket) != TICKET_SIZE:
        raise ValueError("A ticket must contain exactly 6 numbers")
    if any(isinstance(n, bool) or not isinstance(n, Integral) for n in ticket):
        raise TypeError("Ticket numbers must be integers")
    values = tuple(sorted(int(n) for n in ticket))
    if len(set(values)) != TICKET_SIZE:
        raise ValueError("Ticket numbers must be distinct")
    if not all(1 <= n <= N_NUMBERS for n in values):
        raise ValueError("Ticket numbers must lie between 1 and 49")
    return values


def match_count(k: int) -> int:
    """Exact number of draws matching exactly ``k`` numbers on a fixed ticket."""
    if isinstance(k, bool) or not isinstance(k, Integral):
        raise TypeError("k must be an integer")
    k = int(k)
    if not 0 <= k <= TICKET_SIZE:
        raise ValueError("k must be between 0 and 6")
    return comb(TICKET_SIZE, k) * comb(N_NUMBERS - TICKET_SIZE,
                                       TICKET_SIZE - k)


def match_probability(k: int) -> float:
    """Probability of exactly ``k`` matches under a uniform 6-from-49 draw."""
    return match_count(k) / TOTAL


def one_ticket_probability() -> float:
    """Jackpot probability for one valid ticket."""
    return match_probability(TICKET_SIZE)


def distinct_ticket_coverage_probability(n_tickets: int) -> float:
    """Jackpot probability for N *distinct* tickets in the same draw.

    Since one of ``TOTAL`` unordered combinations is drawn, N distinct tickets
    cover exactly N mutually exclusive jackpot outcomes. This is therefore
    exactly N / TOTAL, not the repeated-play formula.
    """
    n_tickets = _nonnegative_int(n_tickets, "n_tickets")
    if n_tickets > TOTAL:
        raise ValueError(f"n_tickets cannot exceed the {TOTAL:,} distinct tickets")
    return n_tickets / TOTAL


def multi_ticket_probability(n_tickets: int) -> float:
    """Backward-compatible alias for distinct same-draw ticket coverage."""
    return distinct_ticket_coverage_probability(n_tickets)


def repeated_play_jackpot_probability(n_plays: int) -> float:
    """Probability of at least one jackpot in N independent plays/draws."""
    n_plays = _nonnegative_int(n_plays, "n_plays")
    if n_plays == 0:
        return 0.0
    p = one_ticket_probability()
    # Numerically stable form of 1 - (1-p)**n for small p.
    return -expm1(n_plays * log1p(-p))


def plays_for_jackpot_probability(target_probability: float) -> int:
    """Smallest number of independent plays giving at least ``target_probability``.

    This is a horizon calculation, not a recommendation to play.
    """
    if not isfinite(target_probability) or not 0 < target_probability < 1:
        raise ValueError("target_probability must be strictly between 0 and 1")
    p = one_ticket_probability()
    # ceil without importing math.ceil: exact integer floor transform.
    x = log1p(-target_probability) / log1p(-p)
    n = int(x)
    if repeated_play_jackpot_probability(n) < target_probability:
        n += 1
    return n


def probability_less_6(k: int) -> float:
    """Compatibility wrapper for the original project's exact-match helper."""
    if not 2 <= k <= 5:
        raise ValueError("k must be between 2 and 5")
    return match_probability(k)


def one_in(p: float) -> str:
    """Human-readable reciprocal-odds approximation."""
    if not isfinite(p) or p < 0 or p > 1:
        raise ValueError("p must be a finite probability between 0 and 1")
    return f"1 in {round(1 / p):,}" if p > 0 else "impossible"


def _validated_prizes(prizes: Mapping[int, float] | None) -> dict[int, float]:
    prizes = DEFAULT_PRIZES if prizes is None else dict(prizes)
    out: dict[int, float] = {}
    for k, prize in prizes.items():
        if isinstance(k, bool) or not isinstance(k, Integral) or not 0 <= int(k) <= 6:
            raise ValueError("Prize-tier match counts must be integers from 0 to 6")
        prize = float(prize)
        if not isfinite(prize) or prize < 0:
            raise ValueError("Prize amounts must be finite and non-negative")
        out[int(k)] = prize
    return out


def expected_value(ticket_price: float = 2.0,
                   prizes: Mapping[int, float] | None = None) -> dict:
    """Expected return under a fixed-prize illustrative payout model.

    This is *not* an estimate of the current expected value of Canadian Lotto
    6/49 or any other real game. Real prize structures can include changing and
    shared jackpots, bonus games and other rules absent from this toy model.
    """
    ticket_price = float(ticket_price)
    if not isfinite(ticket_price) or ticket_price < 0:
        raise ValueError("ticket_price must be finite and non-negative")
    prizes = _validated_prizes(prizes)
    breakdown = {}
    expected_winnings = 0.0
    for k in sorted(prizes, reverse=True):
        p = match_probability(k)
        contribution = p * prizes[k]
        breakdown[k] = {"probability": p, "prize": prizes[k],
                        "contribution": contribution}
        expected_winnings += contribution
    expected_loss = ticket_price - expected_winnings
    return {
        "ticket_price": ticket_price,
        "expected_winnings": expected_winnings,
        "expected_loss": expected_loss,
        "loss_fraction_of_price": (expected_loss / ticket_price
                                    if ticket_price > 0 else None),
        # Keep the original field name for compatibility.
        "loss_per_pound": (expected_loss / ticket_price
                           if ticket_price > 0 else None),
        "breakdown": breakdown,
    }


def lifetime_horizon(n_plays: int, ticket_price: float = 2.0,
                     prizes: Mapping[int, float] | None = None) -> dict:
    """Exact horizon diagnostics for N independent ticket outcomes.

    The distinction between the unconditional mean and the no-jackpot-conditional
    mean is central: rare jackpot worlds can materially affect the mathematical
    expectation even when the typical finite horizon contains no jackpot.
    """
    n_plays = _nonnegative_int(n_plays, "n_plays")
    ticket_price = float(ticket_price)
    if not isfinite(ticket_price) or ticket_price < 0:
        raise ValueError("ticket_price must be finite and non-negative")
    prizes = _validated_prizes(prizes)

    p6 = one_ticket_probability()
    p_any_jackpot = repeated_play_jackpot_probability(n_plays)
    ev = expected_value(ticket_price, prizes)

    jackpot_prize = prizes.get(6, 0.0)
    lower_ev = sum(match_probability(k) * prize
                   for k, prize in prizes.items() if k != 6)
    # Conditional on no jackpot, each independent outcome is distributed as
    # the original categorical draw renormalised over k != 6.
    no_jackpot_winnings_per_play = lower_ev / (1.0 - p6)
    return {
        "plays": n_plays,
        "jackpot_probability": p_any_jackpot,
        "no_jackpot_probability": 1.0 - p_any_jackpot,
        "expected_jackpots": n_plays * p6,
        "unconditional_expected_winnings_per_play": ev["expected_winnings"],
        "unconditional_expected_loss_per_play": ev["expected_loss"],
        "no_jackpot_expected_winnings_per_play": no_jackpot_winnings_per_play,
        "no_jackpot_expected_loss_per_play": ticket_price - no_jackpot_winnings_per_play,
        "jackpot_prize": jackpot_prize,
    }


def simulate_lifetimes(n_plays: int, n_worlds: int = 10_000,
                       ticket_price: float = 2.0,
                       prizes: Mapping[int, float] | None = None,
                       seed: int = 0) -> dict:
    """Repeated-world Monte Carlo for finite-horizon realised losses.

    This is an illustration of distributional skew, not a substitute for the
    exact combinatorial probabilities or expected-value calculation.
    """
    import numpy as np

    n_plays = _nonnegative_int(n_plays, "n_plays")
    n_worlds = _nonnegative_int(n_worlds, "n_worlds")
    if n_plays == 0 or n_worlds == 0:
        raise ValueError("n_plays and n_worlds must both be positive")
    ticket_price = float(ticket_price)
    if not isfinite(ticket_price) or ticket_price < 0:
        raise ValueError("ticket_price must be finite and non-negative")
    prizes = _validated_prizes(prizes)

    pmf = np.array([match_probability(k) for k in range(7)], dtype=float)
    prize_vector = np.array([prizes.get(k, 0.0) for k in range(7)], dtype=float)
    rng = np.random.default_rng(seed)
    counts = rng.multinomial(n_plays, pmf, size=n_worlds)
    winnings = counts @ prize_vector
    loss_per_play = ticket_price - winnings / n_plays

    q025, q25, q50, q75, q975 = np.quantile(
        loss_per_play, [0.025, 0.25, 0.5, 0.75, 0.975]
    )
    return {
        "plays_per_world": n_plays,
        "worlds": n_worlds,
        "mean_loss_per_play": float(loss_per_play.mean()),
        "median_loss_per_play": float(q50),
        "q025_loss_per_play": float(q025),
        "q25_loss_per_play": float(q25),
        "q75_loss_per_play": float(q75),
        "q975_loss_per_play": float(q975),
        "jackpot_world_fraction": float((counts[:, 6] > 0).mean()),
    }


def exact_match_probability(k: int) -> float:
    """Backward-compatible exact-k probability for all k from 0 through 6."""
    return match_probability(k)


def simulate_play(n_tickets: int, ticket_price: float = 2.0,
                  prizes: Mapping[int, float] | None = None,
                  seed: int = 0) -> dict:
    """Backward-compatible single-world simulation.

    Kept for callers of the archived API, but no longer described as proving
    convergence. The audited project uses :func:`simulate_lifetimes` for the
    repeated-world distributional result.
    """
    result = simulate_lifetimes(n_tickets, n_worlds=1,
                                ticket_price=ticket_price,
                                prizes=prizes, seed=seed)
    loss = result["median_loss_per_play"]
    spent = float(ticket_price) * n_tickets
    won = spent - loss * n_tickets
    return {
        "tickets": n_tickets,
        "spent": spent,
        "won": round(won, 2),
        "loss_per_ticket": round(loss, 4),
        "running_loss_per_ticket": [],
    }
