import math

import pytest

from probability import (
    DEFAULT_PRIZES,
    TOTAL,
    distinct_ticket_coverage_probability,
    expected_value,
    lifetime_horizon,
    match_count,
    match_probability,
    multi_ticket_probability,
    one_ticket_probability,
    plays_for_jackpot_probability,
    repeated_play_jackpot_probability,
    simulate_lifetimes,
    validate_ticket,
)


def test_total_combinations():
    assert TOTAL == math.comb(49, 6) == 13_983_816


def test_exact_match_counts_partition_draw_space():
    assert sum(match_count(k) for k in range(7)) == TOTAL
    assert math.isclose(sum(match_probability(k) for k in range(7)), 1.0,
                        rel_tol=0, abs_tol=1e-15)


def test_known_exact_five_match_count():
    assert match_count(5) == 258
    assert match_probability(5) == 258 / TOTAL


def test_jackpot_is_one_combination():
    assert match_count(6) == 1
    assert one_ticket_probability() == 1 / TOTAL


def test_distinct_same_draw_coverage_is_linear_and_bounded():
    assert distinct_ticket_coverage_probability(0) == 0.0
    assert distinct_ticket_coverage_probability(100) == 100 / TOTAL
    assert distinct_ticket_coverage_probability(TOTAL) == 1.0
    assert multi_ticket_probability(100) == 100 / TOTAL


def test_invalid_distinct_ticket_counts_fail_instead_of_silent_clipping():
    with pytest.raises(ValueError):
        distinct_ticket_coverage_probability(-1)
    with pytest.raises(ValueError):
        distinct_ticket_coverage_probability(TOTAL + 1)
    with pytest.raises(TypeError):
        distinct_ticket_coverage_probability(1.5)


def test_repeated_play_formula_differs_from_same_draw_coverage():
    p = one_ticket_probability()
    n = 200_000
    expected = -math.expm1(n * math.log1p(-p))
    assert math.isclose(repeated_play_jackpot_probability(n), expected,
                        rel_tol=0, abs_tol=1e-15)
    assert repeated_play_jackpot_probability(TOTAL) < 0.633
    assert repeated_play_jackpot_probability(TOTAL) > 0.631
    assert distinct_ticket_coverage_probability(TOTAL) == 1.0


def test_match_count_domain_is_strict():
    with pytest.raises(ValueError):
        match_count(-1)
    with pytest.raises(ValueError):
        match_count(7)
    with pytest.raises(TypeError):
        match_count(2.5)


def test_expected_value_reconstructs_from_exact_match_probabilities():
    r = expected_value(ticket_price=2.0)
    hand = sum(match_probability(k) * v for k, v in DEFAULT_PRIZES.items())
    assert math.isclose(r["expected_winnings"], hand, abs_tol=1e-12)
    assert math.isclose(r["expected_loss"], 2.0 - hand, abs_tol=1e-12)
    assert 0.47 < r["loss_fraction_of_price"] < 0.48


def test_expected_value_respects_explicit_empty_prize_table():
    r = expected_value(ticket_price=2.0, prizes={})
    assert r["expected_winnings"] == 0.0
    assert r["expected_loss"] == 2.0


def test_expected_value_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        expected_value(-1)
    with pytest.raises(ValueError):
        expected_value(2, prizes={7: 10})
    with pytest.raises(ValueError):
        expected_value(2, prizes={6: -10})


def test_lifetime_horizon_probability_and_expectation_identities():
    n = 200_000
    r = lifetime_horizon(n, 2.0)
    p6 = 1 / TOTAL
    expected = -math.expm1(n * math.log1p(-p6))
    assert math.isclose(r["jackpot_probability"], expected,
                        rel_tol=0, abs_tol=1e-15)
    assert math.isclose(r["expected_jackpots"], n * p6, abs_tol=1e-15)
    assert math.isclose(r["no_jackpot_probability"],
                        1 - r["jackpot_probability"], abs_tol=1e-15)
    assert 0.985 < r["no_jackpot_probability"] < 0.987
    assert 1.30 < r["no_jackpot_expected_loss_per_play"] < 1.31


def test_independent_play_horizon_inversion_hits_target():
    for target in (0.5, 0.95, 0.99):
        n = plays_for_jackpot_probability(target)
        assert repeated_play_jackpot_probability(n) >= target
        assert repeated_play_jackpot_probability(n - 1) < target


def test_repeated_world_simulation_shows_typical_no_jackpot_horizon():
    r = simulate_lifetimes(200_000, n_worlds=5_000, ticket_price=2.0, seed=25)
    exact = lifetime_horizon(200_000, 2.0)
    assert abs(r["median_loss_per_play"]
               - exact["no_jackpot_expected_loss_per_play"]) < 0.02
    assert abs(r["jackpot_world_fraction"]
               - exact["jackpot_probability"]) < 0.01


def test_validate_ticket_accepts_order_but_normalises_it():
    assert validate_ticket([49, 1, 6, 20, 11, 35]) == (1, 6, 11, 20, 35, 49)


def test_validate_ticket_rejects_wrong_size_duplicates_and_range():
    with pytest.raises(ValueError):
        validate_ticket([1, 2, 3, 4, 5])
    with pytest.raises(ValueError):
        validate_ticket([1, 2, 3, 4, 5, 5])
    with pytest.raises(ValueError):
        validate_ticket([0, 2, 3, 4, 5, 6])
    with pytest.raises(ValueError):
        validate_ticket([1, 2, 3, 4, 5, 50])
